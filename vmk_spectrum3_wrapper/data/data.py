import numpy as np

from vmk_spectrum3_wrapper.data.meta import Meta
from vmk_spectrum3_wrapper.typing import Array, T
from vmk_spectrum3_wrapper.units import Units


class Data:

    def __init__(self, intensity: Array[T], mask: Array[bool], units: Units, meta: Meta | None = None):
        self.intensity = intensity
        self.mask = mask

        self.units = units
        self.meta = meta

    @property
    def n_times(self) -> int:
        if self.intensity.ndim == 1:
            return 1
        return self.intensity.shape[0]

    @property
    def time(self) -> Array[int]:
        return np.arange(self.n_times)

    @property
    def n_numbers(self) -> int:
        if self.intensity.ndim == 1:
            return self.intensity.shape[0]
        return self.intensity.shape[1]

    @property
    def number(self) -> Array[int]:
        """external index of spectrum."""
        return np.arange(self.n_numbers)
