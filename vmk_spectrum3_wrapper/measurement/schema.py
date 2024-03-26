import itertools
from abc import ABC, abstractmethod, abstractproperty
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Iterator, TypeAlias, overload

import numpy as np

from vmk_spectrum3_wrapper.exception import SetupDeviceError
from vmk_spectrum3_wrapper.typing import MicroSecond, MilliSecond


class BaseSchema(ABC):

    @abstractproperty
    def duration_total(self) -> MilliSecond:
        """Длительность проведения одной схемы измерения."""
        raise NotImplementedError

    @abstractproperty
    def capacity_total(self) -> int:
        """Количество кадров для проведения одной схемы измерения."""
        raise NotImplementedError

    # --------        private        --------
    @abstractmethod
    def __iter__(self) -> Iterator:
        """ """
        raise NotImplementedError

    @abstractmethod
    def __str__(self) -> str:
        raise NotImplementedError


@dataclass(frozen=True)
class StandardSchema(BaseSchema):
    exposure: MilliSecond
    capacity: int

    def __post_init__(self):
        validate_exposure(self.exposure)
        validate_capacity(self.capacity)

    @property
    def duration_total(self) -> MilliSecond:
        """Длительность проведения одной схемы измерения."""
        return self.exposure * self.capacity

    @property
    def capacity_total(self) -> int:
        """Количество кадров для проведения одной схемы измерения."""
        return self.capacity

    # --------        private        --------
    def __iter__(self) -> Iterator:
        return iter([
            to_microsecond(self.exposure),
        ])

    def __str__(self) -> str:
        return f'{self.exposure}'


@dataclass(frozen=True)
class ExtendedSchema(BaseSchema):
    exposure: Sequence[MilliSecond, MilliSecond]
    capacity: Sequence[int, int]

    def __post_init__(self):

        if not isinstance(self.exposure, Sequence):
            raise SetupDeviceError('Время экспозиции должно быть последовательснотью: Sequence[MilliSecond, MilliSecond]!')
        if not isinstance(self.capacity, Sequence):
            raise SetupDeviceError('Количество накоплений должно быть последовательснотью: Sequence[int, int]!')
        if not len(self.exposure) == len(self.capacity):
            raise SetupDeviceError('Длина последовательностей должна совпадать!')

        for exposure, capacity in zip(self.exposure, self.capacity):
            validate_exposure(exposure)
            validate_capacity(capacity)

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

    # --------        private        --------
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


# --------        factory        --------
@overload
def fetch_schema(exposure: MilliSecond, capacity: int) -> StandardSchema: ...
@overload
def fetch_schema(exposure: Sequence[MilliSecond, MilliSecond], capacity: Sequence[int, int]) -> ExtendedSchema: ...
def fetch_schema(exposure, capacity):

    if isinstance(exposure, (int, float)):
        return StandardSchema(exposure, capacity)

    if isinstance(exposure, Sequence):
        return ExtendedSchema(exposure, capacity)

    raise ValueError


# --------        utils        --------
def to_microsecond(__exposure: MilliSecond) -> MicroSecond:
    return int(np.round(1000 * __exposure).astype(int))


# --------        validators        --------
def validate_exposure(exposure: MilliSecond) -> None:

    if not isinstance(exposure, (int, float)):
        raise SetupDeviceError('Время экспозиции должно быть числом!')
    if not exposure > 0:
        raise SetupDeviceError('Время экспозиции должно быть положительным числом!')
    if not to_microsecond(exposure) % 100 == 0:
        raise SetupDeviceError('Время экспозиции должно быть кратным 100 мкс!')


def validate_capacity(capacity: int) -> None:

    if not isinstance(capacity, int):
        raise SetupDeviceError('Количество накоплений должно быть целым числом!')
    if not (capacity > 0 and capacity < 2**24):
        raise SetupDeviceError('Количество накоплений должно быть числом с диапазоне [1; 2**24 - 1]!')
