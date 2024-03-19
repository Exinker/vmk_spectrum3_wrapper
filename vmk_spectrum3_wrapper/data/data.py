from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import overload

import matplotlib.pyplot as plt
import numpy as np

from vmk_spectrum3_wrapper.data.meta import Meta
from vmk_spectrum3_wrapper.typing import Array, U
from vmk_spectrum3_wrapper.units import Units


@overload
def reshape(values: Array[U]) -> Array[U]: ...
@overload
def reshape(values: None) -> None: ...
def reshape(values):

    if values is None:
        return None
    if (values.ndim == 2) and (values.shape[0] == 1):
        return values.flatten()

    return values


@overload
def crop(values: Array[U]) -> Array[U]: ...
@overload
def crop(values: Array[bool]) -> Array[bool]: ...
@overload
def crop(values: None) -> None: ...
def crop(value, index):
    if value is None:
        return None

    return value[index, :]


class BaseData(ABC):

    def __init__(self, intensity: Array[U], units: Units, clipped: Array[bool] | None = None, deviation: Array[bool] | None = None, meta: Meta | None = None):
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

    # --------        handlers        --------
    @abstractmethod
    def show(self) -> None:
        raise NotImplementedError

    # --------        private        --------
    def __getitem__(self, index: int | slice) -> 'BaseData':
        assert self.n_times > 1, 'Only 2d data is supported!'

        cls = self.__class__
        return cls(
            intensity=crop(self.intensity, index),
            units=self.units,
            clipped=crop(self.clipped, index),
            deviation=crop(self.deviation, index),
            meta=self.meta,
        )

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

    def __init__(self, intensity: Array[U], units: Units, clipped: Array[bool] | None = None, deviation: Array[bool] | None = None, meta: Meta | None = None):
        super().__init__(intensity=intensity, units=units, clipped=clipped, deviation=deviation, meta=meta)

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

    def __init__(self, intensity: Array[U], units: Units, clipped: Array[bool] | None = None, deviation: Array[bool] | None = None, meta: Meta | None = None):
        super().__init__(intensity=intensity, units=units, clipped=clipped, deviation=deviation, meta=meta)

    # --------        handlers        --------
    @classmethod
    def squeeze(cls, data: Sequence[Datum]) -> 'Data':

        def collapse(data: Sequence[Datum], name: str) -> Array | None:
            try:
                return np.array([getattr(datum, name) for datum in data])

            except AttributeError:
                return None

        return cls(
            intensity=np.array([datum.intensity for datum in data]),
            units=data[0].units,
            clipped=collapse(data, name='clipped'),
            deviation=collapse(data, name='deviation'),
            meta=Meta(
                capacity=data[0].meta.capacity,
                exposure=data[0].meta.exposure,
                started_at=data[0].meta.finished_at,
                finished_at=data[-1].meta.finished_at,
            ),
        )

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
        plt.xlabel(r'Номер отсчета')
        plt.ylabel(r'Интенсивность, {units}'.format(
            units={
                Units.digit: 'бит',
                Units.electron: '$e^{-}$',
                Units.percent: 'отн. ед.',
            }[self.units],
        ))
        plt.show()
