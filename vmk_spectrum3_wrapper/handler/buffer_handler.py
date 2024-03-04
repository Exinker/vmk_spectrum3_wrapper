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
class HighDynamicRangeHandler(BufferHandler):

    def __init__(self, is_naive: bool = True):
        self.is_naive = is_naive

    # --------        private        --------
    def __call__(self, data: Array[T], capacity: tuple[int, int], exposure: tuple[MilliSecond, MilliSecond], *args, **kwargs) -> Array[T]:
        exposure_max = max(exposure)

        data[data >= 100] = np.nan  # FIXME: remove it!
        lelic = (exposure_max / exposure[1]) * np.mean(data[capacity[0]:,:], axis=0)
        bolic = (exposure_max / exposure[0]) * np.mean(data[:capacity[0],:], axis=0)

        return np.nanmean([lelic, bolic], axis=0)
