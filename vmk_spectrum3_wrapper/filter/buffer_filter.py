import numpy as np

from vmk_spectrum3_wrapper.data import Datum, Meta
from vmk_spectrum3_wrapper.filter.base_filter import BaseFilter


class BufferFilter(BaseFilter):
    """Buffer or reduce dimension filters."""


# --------        standard integration filters        --------
class IntegrationFilter(BufferFilter):

    def __init__(self, is_averaging: bool = True):
        self.is_averaging = is_averaging

    # --------        private        --------
    def __call__(self, datum: Datum, *args, **kwargs) -> Datum:
        factor = datum.n_times if self.is_averaging else False

        intensity = np.sum(datum.intensity, axis=0)/factor
        clipped = np.max(datum.clipped, axis=0) if isinstance(datum.clipped, np.ndarray) else None
        deviation = np.sqrt(np.sum(datum.deviation**2, axis=0)/factor) if isinstance(datum.deviation, np.ndarray) else None

        return Datum(
            intensity=intensity,
            units=datum.units,
            clipped=clipped,
            deviation=deviation,
            meta=Meta(
                capacity=datum.n_times,
                exposure=datum.meta.exposure,
                started_at=datum.meta.started_at,
                finished_at=datum.meta.finished_at,
            ),
        )


# --------        high dynamic range (HDR) integration filter        --------
class HighDynamicRangeIntegrationFilter(BufferFilter):

    # --------        private        --------
    def __call__(self, datum: Datum, *args, **kwargs) -> Datum:
        # assert datum.n_times > 1, 'Buffered datum are supported only!'
        # assert isinstance(datum.capacity, tuple), ''  # FIXME: add custom assertion!
        import pickle

        with open('datum.pkl', 'wb') as file:
            pickle.dump(datum, file)

        return datum

        # intensity = datum.intensity.copy()
        # intensity[datum.clipped] = np.nan

        # t1, t2 = datum.meta.exposure
        # n1, n2 = datum.meta.capacity

        # lelic = np.mean(intensity[:n1, :], axis=0) * (max(t1, t2)/t1)
        # bolic = np.mean(intensity[-n2:, :], axis=0) * (max(t1, t2)/t2)

        # return Datum(
        #     intensity=np.nanmean([lelic, bolic], axis=0),
        #     units=datum.units,
        #     clipped=np.max(datum.clipped, axis=0),  # FIXME: calculate clipped!
        #     meta=Meta(
        #         capacity=datum.n_times,
        #         exposure=datum.meta.exposure,
        #         started_at=datum.meta.started_at,
        #         finished_at=datum.meta.finished_at,
        #     ),
        # )