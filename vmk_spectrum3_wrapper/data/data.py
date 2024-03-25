import pickle
from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import overload

import matplotlib.pyplot as plt
import numpy as np

from vmk_spectrum3_wrapper.typing import Array, U
from vmk_spectrum3_wrapper.units import Units

from .meta import DataMeta
from .utils import crop, join, reshape


class BaseData(ABC):

    def __init__(self, intensity: Array[U], units: Units, clipped: Array[bool] | None = None, deviation: Array[bool] | None = None, meta: DataMeta | None = None):
        self.intensity = intensity
        self.units = units
        self.clipped = clipped
        self.deviation = deviation
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

    # --------        handler        --------
    @abstractmethod
    def show(self) -> None:
        raise NotImplementedError

    # --------        private        --------
    # def __add__(self, other: U | Array[U] | 'BaseData') -> 'BaseData':
    #     cls = self.__class__

    #     print(cls.__name__, cls)

    #     #
    #     if isinstance(other, float):
    #         intensity = np.full(other, (self.n_times, self.n_number))
    #         clipped = np.full(False, (self.n_times, self.n_number))

    #     if isinstance(other, np.ndarray):
    #         assert self.n_numbers == len(other)

    #         intensity = other
    #         clipped = np.full(False, other.shape)

    #     if isinstance(other, BaseData):
    #         # assert other.n_times == self.n_times
    #         assert other.n_numbers == self.n_numberss
    #         assert other.units == self.units

    #         intensity = other.intensity
    #         clipped = other.clipped

    #     #
    #     return cls(
    #         intensity=self.intensity + intensity,
    #         units=self.units,
    #         clipped=self.clipped & clipped,
    #         meta=self.meta,
    #     )

    # def __iadd__(self, other: U | Array[U] | 'BaseData') -> 'BaseData':
    #     return self + other

    # def __radd__(self, other: U | Array[U] | 'BaseData') -> 'BaseData':
    #     return self + other

    # def __sub__(self, other: U | Array[U] | 'BaseData') -> 'BaseData':
    #     cls = self.__class__

    #     #
    #     if isinstance(other, float):
    #         intensity = np.full(other, (self.n_times, self.n_number))
    #         clipped = np.full(False, (self.n_times, self.n_number))

    #     if isinstance(other, np.ndarray):
    #         assert self.n_numbers == len(other)

    #         intensity = other
    #         clipped = np.full(False, other.shape)

    #     if isinstance(other, BaseData):
    #         assert other.n_times == self.n_times
    #         assert other.n_numbers == self.n_numbers
    #         assert other.units == self.units

    #         intensity = reshape(other.intensity)
    #         clipped = reshape(other.clipped)

    #     #
    #     return cls(
    #         intensity=self.intensity - intensity,
    #         units=self.units,
    #         clipped=self.clipped & clipped,
    #         meta=self.meta,
    #     )

    # def __isub__(self, other: U | Array[U] | 'BaseData') -> 'BaseData':
    #     return self - other

    # def __rsub__(self, other: U | Array[U] | 'BaseData') -> 'BaseData':
    #     return self - other


class Datum(BaseData):

    def __init__(self, intensity: Array[U], units: Units, clipped: Array[bool] | None = None, deviation: Array[bool] | None = None):
        super().__init__(
            intensity=reshape(intensity),
            units=units,
            clipped=reshape(clipped),
            deviation=reshape(deviation),
        )

    # --------        handler        --------
    def show(self) -> None:
        fig, ax = plt.subplots(figsize=(6, 4), tight_layout=True)

        color = 'black' if self.n_times == 1 else None
        for t in range(self.n_times):
            plt.step(
                self.number, self.intensity[t, :],
                where='mid',
                color=color, linestyle='-', linewidth=1,
            )

            if self.clipped is not None:
                mask = self.clipped[t, :]
                plt.plot(
                    self.number[mask], self.intensity[t, mask],
                    color='red', linestyle='none', marker='.', markersize=2,
                )

        #
        plt.xlabel('Номер отсчета')
        plt.ylabel('Интенсивность, отн. ед.')

        plt.show()

    # --------        private        --------
    def __getitem__(self, index: tuple[int | Array[int] | slice, int | Array[int] | slice]) -> 'BaseData':
        """Итерировать по `index` вдоль времени и пространству."""
        cls = self.__class__

        return cls(
            intensity=crop(self.intensity, index),
            units=self.units,
            clipped=crop(self.clipped, index),
            deviation=crop(self.deviation, index),
        )


class Data(BaseData):

    def __init__(self, intensity: Array[U], units: Units, clipped: Array[bool] | None = None, deviation: Array[bool] | None = None, meta: DataMeta | None = None):
        super().__init__(
            intensity=reshape(intensity),
            units=units,
            clipped=reshape(clipped),
            deviation=reshape(deviation),
            meta=meta,
        )

    # --------        handler        --------
    def save(self, filepath: str | None = None) -> None:
        with open(filepath, 'bw') as file:
            pickle.dump(self, file)

    def show(self) -> None:
        fig, ax = plt.subplots(figsize=(6, 4), tight_layout=True)

        color = 'black' if self.n_times == 1 else None
        for t in range(self.n_times):
            plt.step(
                self.number, self.intensity[t, :],
                where='mid',
                color=color, linestyle='-', linewidth=1,
            )

            if self.clipped is not None:
                mask = self.clipped[t, :]
                plt.plot(
                    self.number[mask], self.intensity[t, mask],
                    color='red', linestyle='none', marker='.', markersize=2,
                )

        #
        plt.xlabel(r'Номер отсчета')
        plt.ylabel(r'Интенсивность, {units}'.format(
            units={
                Units.digit: 'бит',
                Units.electron: '$e^{-}$',
                Units.percent: 'отн. ед.',
            }[self.units],
        ))
        plt.show()

    # --------        fabric        --------
    @classmethod
    def load(cls, filepath: str) -> 'Data':
        with open(filepath, 'br') as file:
            data = pickle.load(file)

        return data

    @classmethod
    def squeeze(cls, __items: Sequence[Datum], meta: DataMeta) -> 'Data':
        for i, item in enumerate(__items):
            print(f'{i}: {item.intensity.shape}')

        return cls(
            intensity=join([item.intensity for item in __items]),
            units=__items[0].units,
            clipped=join([item.clipped for item in __items]),
            deviation=join([item.deviation for item in __items]),
            meta=meta,
        )

    # --------        private        --------
    def __getitem__(self, index: tuple[int | Array[int] | slice, int | Array[int] | slice]) -> 'BaseData':
        """Итерировать по `index` вдоль времени и пространству."""
        cls = self.__class__

        return cls(
            intensity=crop(self.intensity, index),
            units=self.units,
            clipped=crop(self.clipped, index),
            deviation=crop(self.deviation, index),
            meta=self.meta,
        )
