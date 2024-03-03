import numpy as np

from vmk_spectrum3_wrapper.detector import Detector
from vmk_spectrum3_wrapper.handler.base_handler import BaseHandler
from vmk_spectrum3_wrapper.typing import Array, MilliSecond, T


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


# --------        high dynamic range (HDR) handlers        --------
class HighDynamicRangeHandler(BufferError):

    def __init__(self, is_naive: bool = True):
        self.is_naive = is_naive

    # --------        private        --------
    def __call__(self, data: Array[T], capacity: tuple[int, int], exposure: tuple[MilliSecond, MilliSecond], detector: Detector, *args, **kwargs) -> Array[T]:
        raise NotImplementedError
