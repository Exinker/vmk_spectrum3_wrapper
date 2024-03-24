import time
from typing import overload

from vmk_spectrum3_wrapper.data import Data
from vmk_spectrum3_wrapper.filter import Filter
from vmk_spectrum3_wrapper.measurement.schema import Schema, fetch_schema
from vmk_spectrum3_wrapper.measurement.storage import Storage
from vmk_spectrum3_wrapper.typing import Array, MilliSecond


class Measurement:

    def __init__(self, schema: Schema, storage: Storage):
        self._schema = schema
        self._storage = storage

        self._n_iters = None
        self._started_at = None
        self._finished_at = None

    @property
    def schema(self) -> Schema:
        return self._schema

    @property
    def storage(self) -> Storage:
        return self._storage

    @property
    def n_iters(self) -> int | None:
        return self._n_iters

    @property
    def progress(self) -> float | None:
        if self.n_iters is None:
            return None

        return len(self.storage) / self.n_iters

    @property
    def capacity_total(self) -> int:
        """Полное количество кадров."""
        if self.n_iters is None:
            return None

        return self.n_iters * self.schema.capacity_total

    @property
    def duration_total(self) -> MilliSecond | None:
        """Полное время измерения."""
        if self.n_iters is None:
            return None

        return self.n_iters * self.schema.duration_total

    def setup(self, n_iters: int) -> None:
        self._n_iters = n_iters

    def put(self, frame: Array[int]) -> None:
        """Добавить новый `frame` в `storage`."""

        # time
        time_at = time.perf_counter()

        if self._started_at is None:
            self._started_at = time_at

        self._finished_at = time_at

        #
        self.storage.put(frame)

    def pull(self) -> Data:
        """Забрать все `data` из `storage`."""
        if self.progress < 1:
            raise ValueError  # TODO: add custom exception!

        #
        return Data.squeeze(self.storage.pull())


# --------        factory        --------
@overload
def fetch_measurement(exposure: MilliSecond, capacity: int, handler: Filter | None = None) -> Measurement: ...
@overload
def fetch_measurement(exposure: tuple[MilliSecond, MilliSecond], capacity: tuple[int, int], handler: Filter | None = None) -> Measurement: ...
def fetch_measurement(exposure, capacity, handler):
    return Measurement(
        schema=fetch_schema(exposure, capacity),
        storage=Storage(exposure, capacity, handler),
    )
