import itertools
from abc import ABC, abstractmethod, abstractproperty
from dataclasses import dataclass
from typing import Iterator, TypeAlias, overload

import numpy as np

from vmk_spectrum3_wrapper.typing import MicroSecond, MilliSecond


def to_microsecond(__exposure: MilliSecond) -> MicroSecond:
    value = int(np.round(1000 * __exposure).astype(int))

    assert value % 100 == 0, 'Invalid exposure: {value} mks!'.format(
        value=value,
    )

    return value


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
        assert isinstance(self.exposure, (int, float))
        assert isinstance(self.capacity, int)

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
    exposure: tuple[MilliSecond, MilliSecond]
    capacity: tuple[int, int]

    def __post_init__(self):
        assert isinstance(self.exposure, tuple)
        assert isinstance(self.capacity, tuple)
        assert len(self.exposure) == len(self.capacity)

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
            for exposure, capacity in zip(reversed(self.exposure), reversed(self.capacity))  # TODO: reverse items for compatibility with Atom
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
def fetch_schema(exposure: tuple[MilliSecond, MilliSecond], capacity: tuple[int, int]) -> ExtendedSchema: ...
def fetch_schema(exposure, capacity):

    if isinstance(exposure, (int, float)):
        return StandardSchema(exposure, capacity)

    if isinstance(exposure, tuple):
        return ExtendedSchema(exposure, capacity)

    raise ValueError
