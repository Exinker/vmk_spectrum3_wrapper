import itertools
from abc import ABC, abstractmethod, abstractproperty
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Iterator, TypeAlias, overload

import numpy as np

from vmk_spectrum3_wrapper.exception import SetupDeviceError
from vmk_spectrum3_wrapper.types import MicroSecond, MilliSecond

from .utils import to_microsecond
from .validators import validate_capacity, validate_exposure


@overload
def schema_factory(exposure: MilliSecond, capacity: int) -> 'StandardSchema': ...
@overload
def schema_factory(exposure: Sequence[MilliSecond, MilliSecond], capacity: Sequence[int, int]) -> 'ExtendedSchema': ...
def schema_factory(exposure, capacity):

    if isinstance(exposure, (int, float)):
        return StandardSchema(exposure, capacity)

    if isinstance(exposure, Sequence):
        return ExtendedSchema(exposure, capacity)

    raise ValueError


class BaseSchema(ABC):

    create = schema_factory

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
        return f'({self.exposure}, {self.capacity})'


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
