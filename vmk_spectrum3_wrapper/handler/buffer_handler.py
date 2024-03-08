import numpy as np

from vmk_spectrum3_wrapper.data import Datum, Meta
from vmk_spectrum3_wrapper.handler.base_handler import BaseHandler


class BufferHandler(BaseHandler):
    """Reduce dimension handlers."""


class IntegralHandler(BufferHandler):

    # --------        private        --------
    def __call__(self, datum: Datum, *args, **kwargs) -> Datum:
        assert datum.n_times > 1, 'Buffered datum are supported only!'

        intensity = np.sum(datum.intensity, axis=0)
        clipped = np.max(datum.clipped, axis=0) if isinstance(datum.clipped, np.ndarray) else None

        return Datum(
            intensity=intensity,
            units=datum.units,
            clipped=clipped,
            meta=Meta(
                capacity=datum.n_times,
                exposure=datum.meta.exposure,
                started_at=datum.meta.started_at,
                finished_at=datum.meta.finished_at,
            ),
        )


class AverageHandler(BufferHandler):

    # --------        private        --------
    def __call__(self, datum: Datum, *args, **kwargs) -> Datum:
        assert datum.n_times > 1, 'Buffered datum are supported only!'

        intensity = np.mean(datum.intensity, axis=0)
        clipped = np.max(datum.clipped, axis=0) if isinstance(datum.clipped, np.ndarray) else None

        return Datum(
            intensity=intensity,
            units=datum.units,
            clipped=clipped,
            meta=Meta(
                capacity=datum.n_times,
                exposure=datum.meta.exposure,
                started_at=datum.meta.started_at,
                finished_at=datum.meta.finished_at,
            ),
        )


# --------        high dynamic range (HDR) handlers        --------
class HighDynamicRangeHandler(BufferHandler):

    def __init__(self, is_naive: bool = True):
        self.is_naive = is_naive

    # --------        private        --------
    def __call__(self, datum: Datum, *args, **kwargs) -> Datum:
        assert datum.n_times > 1, 'Buffered datum are supported only!'
        assert isinstance(datum.capacity, tuple), ''  # FIXME: add custom assertion!

        raise NotImplementedError

        # exposure_max = max(exposure)

        # datum[datum >= 100] = np.nan  # FIXME: remove it!
        # lelic = (exposure_max / exposure[1]) * np.mean(datum[capacity[0]:,:], axis=0)
        # bolic = (exposure_max / exposure[0]) * np.mean(datum[:capacity[0],:], axis=0)

        # return np.nanmean([lelic, bolic], axis=0)
