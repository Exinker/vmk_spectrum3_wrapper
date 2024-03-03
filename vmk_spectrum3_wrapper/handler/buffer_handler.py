from typing import Callable

import numpy as np

from vmk_spectrum3_wrapper.handler.base_handler import BaseHandler
from vmk_spectrum3_wrapper.typing import Array, Digit, T


class BufferHandler(BaseHandler):
    """Reduce dimension handlers."""


class IntegralHandler(BufferHandler):

    # --------        private        --------
    def __call__(self, data: Array[T], *args, **kwargs) -> Array[T]:
        return np.sum(data, axis=0)


class AverageHandler(BufferHandler):

    # --------        private        --------
    def __call__(self, data: Array[T], *args, **kwargs) -> Array[T]:
        return np.mean(data, axis=0)
