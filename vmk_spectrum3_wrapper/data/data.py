from abc import ABC, abstractmethod
from collections.abc import Sequence

import matplotlib.pyplot as plt
import numpy as np

from vmk_spectrum3_wrapper.data.meta import Meta
from vmk_spectrum3_wrapper.typing import Array, T
from vmk_spectrum3_wrapper.units import Units


class BaseData(ABC):

    intensity: Array[T]
    units: Units

    clipped: Array[bool] | None = None
    meta: Meta | None = None

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

    # --------        handlers        --------
    @abstractmethod
    def show(self) -> None:
        raise NotImplementedError


class Datum(BaseData):

    def __init__(self, intensity: Array[T], units: Units, clipped: Array[bool] | None = None, meta: Meta | None = None):
        self.intensity = intensity
        self.units = units

        self.clipped = clipped
        self.meta = meta

    # --------        handlers        --------
    def show(self) -> None:
        fig, ax = plt.subplots(figsize=(6, 4), tight_layout=True)

        # intensity
        plt.step(
            self.number, self.intensity,
            where='mid',
            color='black', linestyle='-', linewidth=1,
        )

        # mask
        if self.clipped is not None:
            mask = self.clipped
            plt.plot(
                self.number[mask], self.intensity[mask],
                color='red', linestyle='none', marker='.', markersize=.5,
            )

        #
        plt.xlabel('Номер отсчета')
        plt.ylabel('Интенсивность, отн. ед.')

        plt.show()


class Data(BaseData):

    def __init__(self, data: Sequence[Datum]):
        self.intensity = np.array([datum.intensity for datum in data])
        self.units = data[0].units

        self.clipped = np.array([datum.clipped for datum in data]) if isinstance(data[0].clipped, np.ndarray) else None
        self.meta = Meta(
            capacity=data[0].meta.capacity,
            exposure=data[0].meta.exposure,
            started_at=data[0].meta.finished_at,
            finished_at=data[-1].meta.finished_at,
        )

    # --------        handlers        --------
    def show(self) -> None:
        fig, ax = plt.subplots(figsize=(6, 4), tight_layout=True)

        # intensity
        intensity = np.mean(self.intensity, axis=0)
        plt.step(
            self.number, intensity,
            where='mid',
            color='black', linestyle='-', linewidth=1,
        )

        # mask
        if self.clipped is not None:
            mask = np.max(self.clipped, axis=0)
            plt.plot(
                self.number[mask], intensity[mask],
                color='red', linestyle='none', marker='.', markersize=.5,
            )

        #
        plt.xlabel('Номер отсчета')
        plt.ylabel('Интенсивность, отн. ед.')
        plt.show()
