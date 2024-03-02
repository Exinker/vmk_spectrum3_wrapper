from abc import ABC, abstractmethod
from typing import Callable

import numpy as np

from vmk_spectrum3_wrapper.typing import Array, Digit, T
from vmk_spectrum3_wrapper.handler import Handler


class BufferHandler(ABC, Handler):
    """Reduce dimension handlers."""


class IntegralHandler(BufferHandler):

    # --------        private        --------
    def __call__(self, data: Array[T]) -> Array[T]:
        return np.sum(data, axis=0)


class AverageHandler(BufferHandler):

    # --------        private        --------
    def __call__(self, data: Array[T]) -> Array[T]:
        return np.mean(data, axis=0)
