import itertools
from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Iterator, TypeAlias, overload

from vmk_spectrum3_wrapper.measurement_manager.exceptions import SchemaCapacityError, SchemaExposureError, SchemaError
from vmk_spectrum3_wrapper.measurement_manager.utils import to_microsecond
from vmk_spectrum3_wrapper.types import MicroSecond, MilliSecond


@overload
def schema_factory(exposure: MilliSecond, capacity: int) -> 'StandardSchema': ...
@overload
def schema_factory(exposure: Sequence[MilliSecond, MilliSecond], capacity: Sequence[int, int]) -> 'ExtendedSchema': ...
def schema_factory(exposure, capacity):

    if isinstance(exposure, (int, float)):
        return StandardSchema.create(exposure, capacity)
    if isinstance(exposure, Sequence) and isinstance(capacity, Sequence):
        return ExtendedSchema.create(exposure, capacity)

    raise SchemaError(f'Schema is not supported: ({exposure}, {capacity})')


class SchemaABC(ABC):

    @property
    @abstractmethod
    def duration_total(self) -> MilliSecond:
        """Длительность проведения одной схемы измерения."""
        raise NotImplementedError

    @property
    @abstractmethod
    def capacity_total(self) -> int:
        """Количество кадров для проведения одной схемы измерения."""
        raise NotImplementedError

    @abstractmethod
    def __iter__(self) -> Iterator:
        """ """
        raise NotImplementedError

    @abstractmethod
    def __str__(self) -> str:
        raise NotImplementedError


@dataclass(frozen=True)
class StandardSchema(SchemaABC):
    exposure: MilliSecond
    capacity: int

    @property
    def duration_total(self) -> MilliSecond:
        """Длительность проведения одной схемы измерения."""
        return self.exposure * self.capacity

    @property
    def capacity_total(self) -> int:
        """Количество кадров для проведения одной схемы измерения."""
        return self.capacity

    @classmethod
    def create(cls, exposure: MilliSecond, capacity: int) -> 'StandardSchema':
        _validate_exposure(exposure)
        _validate_capacity(capacity)

        return cls(
            exposure=exposure,
            capacity=capacity,
        )

    def __iter__(self) -> Iterator[MicroSecond]:
        return iter([
            to_microsecond(self.exposure),
        ])

    def __str__(self) -> str:
        return f'({self.exposure}, {self.capacity})'


@dataclass(frozen=True)
class ExtendedSchema(SchemaABC):
    exposure: Sequence[MilliSecond, MilliSecond]
    capacity: Sequence[int, int]

    @property
    def duration_total(self) -> MilliSecond:
        """Длительность проведения одной схемы измерения."""
        return sum(
            tau*n
            for tau, n in zip(self.exposure, self.capacity)
        )

    @property
    def capacity_total(self) -> int:
        """Количество кадров для проведения одной схемы измерения."""
        return sum(self.capacity)

    @classmethod
    def create(
        cls,
        exposure: Sequence[MilliSecond, MilliSecond],
        capacity: Sequence[int, int],
    ) -> 'ExtendedSchema':

        if not len(exposure) == 2:
            raise SchemaExposureError('Время экспозиции должно быть последовательснотью длиною 2!')
        if not len(capacity) == 2:
            raise SchemaCapacityError('Количество накоплений должно быть последовательснотью длиною 2!')
        for tau, n in zip(exposure, capacity):
            _validate_exposure(tau)
            _validate_capacity(n)

        return cls(
            exposure=exposure,
            capacity=capacity,
        )

    def __iter__(self) -> Iterator:
        return itertools.chain(*[
            (to_microsecond(exposure), capacity)
            for exposure, capacity in zip(reversed(self.exposure), reversed(self.capacity))  # TODO: items are reversed for compatibility with `Atom`
        ])

    def __str__(self) -> str:
        return '; '.join([
            f'({exposure}, {capacity})'
            for exposure, capacity in zip(self.exposure, self.capacity)
        ])


Schema: TypeAlias = StandardSchema | ExtendedSchema


def _validate_exposure(exposure: MilliSecond) -> None:

    if not isinstance(exposure, (int, float)):
        raise SchemaExposureError('Время экспозиции должно быть числом!')
    if not exposure > 0:
        raise SchemaExposureError('Время экспозиции должно быть положительным числом!')
    if not to_microsecond(exposure) % 100 == 0:
        raise SchemaExposureError('Время экспозиции должно быть кратным 100 мкс!')


def _validate_capacity(capacity: int) -> None:

    if not isinstance(capacity, int):
        raise SchemaCapacityError('Количество накоплений должно быть целым числом!')
    if not (capacity > 0 and capacity < 2**24):
        raise SchemaCapacityError('Количество накоплений должно быть числом в диапазоне [1; 2**24 - 1]!')
