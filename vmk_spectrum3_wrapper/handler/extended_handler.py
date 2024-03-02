from typing import Callable

import numpy as np

from vmk_spectrum3_wrapper.handler.base_handler import BaseHandler
from vmk_spectrum3_wrapper.typing import Array, Digit, T


class ExtendedHandler(BaseHandler):
    """Reduce dimension handlers."""


class NaiveHandler(ExtendedHandler):

    # --------        private        --------
    def __call__(self, data: Array[T]) -> Array[T]:
        return np.sum(data, axis=0)


class WeightedHandler(ExtendedHandler):

    # --------        private        --------
    def __call__(self, data: Array[T]) -> Array[T]:
        return np.mean(data, axis=0)
