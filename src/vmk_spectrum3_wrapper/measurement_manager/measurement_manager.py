import time
from typing import Iterator, overload

import pyspectrum3 as ps3

from vmk_spectrum3_wrapper.data import Data
from vmk_spectrum3_wrapper.exception import WrapperSetupError
from vmk_spectrum3_wrapper.measurement_manager.exceptions import SchemaError
from vmk_spectrum3_wrapper.measurement_manager.filters import F, HighDynamicRangeIntegrationPreset, PipeFilter, StandardIntegrationPreset
from vmk_spectrum3_wrapper.measurement_manager.schemas import ExtendedSchema, Schema, StandardSchema, schema_factory
from vmk_spectrum3_wrapper.measurement_manager.storage import Storage
from vmk_spectrum3_wrapper.types import Array, MilliSecond


def default_filter_factory(schema: Schema) -> PipeFilter:

    if isinstance(schema, StandardSchema):
        return StandardIntegrationPreset()
    if isinstance(schema, ExtendedSchema):
        return HighDynamicRangeIntegrationPreset()

    raise SchemaError(f'Schema is not supported: {schema}')


@overload
def measurement_manager_factory(
    n_times: int,
    exposure: MilliSecond,
    capacity: int,
    filter: F | None = None,
) -> 'MeasurementManager': ...
@overload
def measurement_manager_factory(
    n_times: int,
    exposure: tuple[MilliSecond, MilliSecond],
    capacity: tuple[int, int],
    filter: F | None = None,
) -> 'MeasurementManager': ...
def measurement_manager_factory(n_times, exposure, capacity, filter):

    try:
        schema = schema_factory(exposure, capacity)
    except SchemaError as error:
        raise WrapperSetupError from error

    try:
        filter = filter or default_filter_factory(schema)
    except SchemaError as error:
        raise WrapperSetupError from error

    return MeasurementManager(
        n_times=n_times,
        schema=schema,
        storage=Storage(exposure, capacity, filter),
    )


class MeasurementManager:
    """Менеджер измерения.
    Параметры:
        `n_times` - количество выполнений схемы измерений;
        `schema` - схема измерения;
        `storage` - хранилище данных.
    """

    create = measurement_manager_factory

    def __init__(self, n_times: int, schema: Schema, storage: Storage):
        self._n_times = n_times
        self._schema = schema
        self._storage = storage

        self._started_at = None
        self._finished_at = None

    @property
    def n_times(self) -> int | None:
        return self._n_times

    @property
    def schema(self) -> Schema:
        return self._schema

    @property
    def storage(self) -> Storage:
        return self._storage

    @property
    def progress(self) -> float | None:
        """Доля выполненного измерения."""
        if self.n_times is None:
            return None

        return len(self.storage) / self.n_times

    @property
    def capacity_total(self) -> int:
        """Полное количество кадров."""
        if self.n_times is None:
            return None

        return self.n_times * self.schema.capacity_total

    @property
    def duration_total(self) -> MilliSecond | None:
        """Полное время измерения."""
        if self.n_times is None:
            return None

        return self.n_times * self.schema.duration_total

    def put(self, frame: Array[int]) -> None:
        """Добавить новый `frame` в `storage`."""
        time_at = time.perf_counter()

        if self._started_at is None:
            self._started_at = time_at
        self._finished_at = time_at

        self.storage.put(frame)

    def pull(self) -> Data:
        """Забрать все `data` из `storage`."""
        if self.progress < 1:
            raise ValueError  # TODO: add custom exception!

        return Data.squeeze(self.storage.pull())

    def __eq__(self, other: 'MeasurementManager') -> bool:
        return all([
            self.n_times == other.n_times,
            self.schema == other.schema,
            self.storage == other.storage,
        ])

    def __iter__(self) -> Iterator:

        if isinstance(self.schema, StandardSchema):
            return iter([
                ps3.Exposure(*self.schema), self.capacity_total, 0,
            ])
        if isinstance(self.schema, ExtendedSchema):
            return iter([
                ps3.Exposure(ps3.DoubleTimer(*self.schema)), self.capacity_total, 0,
            ])

    def __str__(self) -> str:
        cls = self.__class__
        return f'{cls.__name__}({self.n_times}, schema={repr(self.schema)})'
