from abc import ABC, abstractmethod
from typing import Callable

import numpy as np

from vmk_spectrum3_wrapper.typing import Array, Digit, T
from vmk_spectrum3_wrapper.units import Units, get_scale


class Handler(ABC):

    @abstractmethod
    def __call__(self, data: Array[T]) -> Array[T]:
        raise NotImplementedError


class Averager(Handler):

    def __call__(self, data: Array[T]) -> Array[T]:
        return np.mean(data, axis=0)


class Scaler(Handler):
    """Handler to scale a data from `Units.digit` to `units`"""

    def __init__(self, units: Units):
        self.units = units
        self.scale = get_scale(units)

    def __call__(self, data: Array[Digit]) -> Array[T]:
        return self.scale*data
