import numpy as np

from vmk_spectrum3_wrapper.data import Data, Meta
from vmk_spectrum3_wrapper.handler.base_handler import BaseHandler


class BufferHandler(BaseHandler):
    """Reduce dimension handlers."""


class IntegralHandler(BufferHandler):

    # --------        private        --------
    def __call__(self, data: Data, *args, **kwargs) -> Data:
        assert data.n_times > 1, 'Buffered data are supported only!'

        intensity = np.sum(data.intensity, axis=0)
        clipped = np.max(data.clipped, axis=0) if isinstance(data.clipped, np.ndarray) else None

        return Data(
            intensity=intensity,
            units=data.units,
            clipped=clipped,
            meta=Meta(
                capacity=data.n_times,
                exposure=data.meta.exposure,
                started_at=data.meta.started_at,
                finished_at=data.meta.finished_at,
            ),
        )


class AverageHandler(BufferHandler):

    # --------        private        --------
    def __call__(self, data: Data, *args, **kwargs) -> Data:
        assert data.n_times > 1, 'Buffered data are supported only!'

        intensity = np.mean(data.intensity, axis=0)
        clipped = np.max(data.clipped, axis=0) if isinstance(data.clipped, np.ndarray) else None

        return Data(
            intensity=intensity,
            units=data.units,
            clipped=clipped,
            meta=Meta(
                capacity=data.n_times,
                exposure=data.meta.exposure,
                started_at=data.meta.started_at,
                finished_at=data.meta.finished_at,
            ),
        )


# --------        high dynamic range (HDR) handlers        --------
class HighDynamicRangeHandler(BufferHandler):

    def __init__(self, is_naive: bool = True):
        self.is_naive = is_naive

    # --------        private        --------
    def __call__(self, data: Data, *args, **kwargs) -> Data:
        assert data.n_times > 1, 'Buffered data are supported only!'
        assert isinstance(data.capacity, tuple), ''  # FIXME: add custom assertion!

        raise NotImplementedError

        # exposure_max = max(exposure)

        # data[data >= 100] = np.nan  # FIXME: remove it!
        # lelic = (exposure_max / exposure[1]) * np.mean(data[capacity[0]:,:], axis=0)
        # bolic = (exposure_max / exposure[0]) * np.mean(data[:capacity[0],:], axis=0)

        # return np.nanmean([lelic, bolic], axis=0)
