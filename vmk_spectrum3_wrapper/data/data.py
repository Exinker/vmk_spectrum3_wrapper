import matplotlib.pyplot as plt
import numpy as np

from vmk_spectrum3_wrapper.data.meta import Meta
from vmk_spectrum3_wrapper.typing import Array, T
from vmk_spectrum3_wrapper.units import Units


class Data:

    def __init__(self, intensity: Array[T], units: Units, clipped: Array[bool] | None = None, meta: Meta | None = None):
        self.intensity = intensity
        self.units = units

        self.clipped = clipped
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
        return np.arange(self.n_numbers)

    #
    def show(self) -> None:
        fig, ax = plt.subplots(figsize=(6, 4), tight_layout=True)

        plt.step(
            self.number, self.intensity,
            where='mid',
            color='black', linestyle='-', linewidth=1,
        )

        if self.clipped is not None:
            plt.plot(
                self.number[self.clipped], self.intensity[self.clipped],
                color='red', linestyle='none', marker='.', markersize=.5,
            )

        plt.xlabel('Номер отсчета')
        plt.ylabel('Интенсивность, отн. ед.')
        plt.show()