import pickle

import numpy as np

from vmk_spectrum3_wrapper.data import Datum
from vmk_spectrum3_wrapper.typing import MilliSecond

from .base_filter import BaseFilter


class BufferFilter(BaseFilter):
    """Снижающий размерность фильтр."""


# --------        standard integration filters        --------
class IntegrationFilter(BufferFilter):
    """Интегральный фильтр."""

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
        )


# --------        high dynamic range (HDR) integration filter        --------
class HighDynamicRangeIntegrationFilter(BufferFilter):
    """Интегральный в расширенном динамическом диапазоне фильтр."""

    # --------        private        --------
    def __call__(self, datum: Datum, *args, exposure: MilliSecond | tuple[MilliSecond, MilliSecond], capacity: int | tuple[int, int], save: bool = True, **kwargs) -> Datum:
        assert datum.n_times == 2

        if save:
            with open('spam.pkl', 'wb') as file:
                pickle.dump(datum, file)

        #
        lelic, bolic = [
            datum.intensity[i, :] * (max(exposure)/exposure[i])
            for i in range(datum.n_times)
        ]

        #
        return Datum(
            intensity=np.nanmean([lelic, bolic], axis=0),
            units=datum.units,
            clipped=np.min(datum.clipped, axis=0),
        )
