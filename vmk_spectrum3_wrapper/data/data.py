from abc import ABC, abstractmethod
from collections.abc import Sequence
import pickle
from typing import Any, Mapping

import matplotlib.pyplot as plt
import numpy as np

from vmk_spectrum3_wrapper.types import Array, U
from vmk_spectrum3_wrapper.units import Units

from .meta import Meta
from .utils import crop, join, reshape


class BaseData(ABC):

    def __init__(
        self,
        units: Units,
        intensity: Array[U],
        clipped: Array[bool] | None = None,
        deviation: Array[bool] | None = None,
        meta: Meta | None = None,
    ):
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

    @abstractmethod
    def show(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def dumps(self) -> Mapping[str, Any]:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def loads(cls, __dump: Mapping[str, Any]) -> 'BaseData':
        raise NotImplementedError


class Datum(BaseData):

    def __init__(
        self,
        units: Units,
        intensity: Array[U],
        clipped: Array[bool] | None = None,
        deviation: Array[bool] | None = None,
    ):
        super().__init__(
            units=units,
            intensity=reshape(intensity),
            clipped=reshape(clipped),
            deviation=reshape(deviation),
        )

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

        plt.xlabel('Номер отсчета')
        plt.ylabel('Интенсивность, отн. ед.')

        plt.show()

    def dumps(self) -> Mapping[str, Any]:

        dat = {
            'units': str(self.units),
            'intensity': pickle.dumps(self.intensity),
            'clipped': pickle.dumps(self.clipped),
            'deviation': pickle.dumps(self.deviation),
        }
        return dat

    @classmethod
    def loads(cls, __dump: Mapping[str, Any]) -> 'Datum':

        units = {
            'Units.digit': Units.digit,
            'Units.percent': Units.percent,
            'Units.electron': Units.electron,
        }.get(__dump.get('units'), Units.percent)

        datum = cls(
            units=units,
            intensity=pickle.loads(__dump.get('intensity')),
            clipped=pickle.loads(__dump.get('clipped')),
            deviation=pickle.loads(__dump.get('deviation')),
        )
        return datum

    def __getitem__(
        self,
        index: tuple[int | Array[int] | slice, int | Array[int] | slice],
    ) -> 'BaseData':
        """Итерировать по `index` вдоль времени и пространству."""
        cls = self.__class__

        return cls(
            units=self.units,
            intensity=crop(self.intensity, index),
            clipped=crop(self.clipped, index),
            deviation=crop(self.deviation, index),
        )


class Data(BaseData):

    def __init__(
        self,
        units: Units,
        intensity: Array[U],
        clipped: Array[bool] | None = None,
        deviation: Array[bool] | None = None,
        meta: Meta | None = None,
    ):
        super().__init__(
            units=units,
            intensity=reshape(intensity),
            clipped=reshape(clipped),
            deviation=reshape(deviation),
            meta=meta,
        )

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

        plt.xlabel(r'Номер отсчета')
        plt.ylabel(r'Интенсивность, {units}'.format(
            units={
                Units.digit: 'бит',
                Units.electron: '$e^{-}$',
                Units.percent: 'отн. ед.',
            }[self.units],
        ))
        plt.show()

    @classmethod
    def squeeze(
        cls,
        __items: Sequence[Datum],
        meta: Meta,
    ) -> 'Data':

        return cls(
            units=__items[0].units,
            intensity=join([item.intensity for item in __items]),
            clipped=join([item.clipped for item in __items]),
            deviation=join([item.deviation for item in __items]),
            meta=meta,
        )

    def dumps(self) -> Mapping[str, Any]:

        dat = {
            'units': str(self.units),
            'intensity': pickle.dumps(self.intensity),
            'clipped': pickle.dumps(self.clipped),
            'deviation': pickle.dumps(self.deviation),
            'meta': self.meta.dumps() if self.meta else None,
        }
        return dat

    def save(self, filepath: str | None = None) -> None:
        dat = self.dumps()

        with open(filepath, 'bw') as file:
            pickle.dump(dat, file)

    @classmethod
    def loads(cls, _dump: Mapping[str, Any]) -> 'Data':

        units = {
            'Units.digit': Units.digit,
            'Units.percent': Units.percent,
            'Units.electron': Units.electron,
        }.get(_dump.get('units'), Units.percent)

        datum = cls(
            units=units,
            intensity=pickle.loads(_dump.get('intensity')),
            clipped=pickle.loads(_dump.get('clipped')),
            deviation=pickle.loads(_dump.get('deviation')),
            meta=Meta.loads(_dump.get('meta')) if _dump.get('meta') else None,
        )
        return datum

    @classmethod
    def load(cls, filepath: str) -> 'Data':
        with open(filepath, 'br') as file:
            dat = pickle.load(file)

        data = cls.loads(dat)
        return data

    def __getitem__(
        self,
        index: tuple[int | Array[int] | slice, int | Array[int] | slice],
    ) -> 'BaseData':
        """Итерировать по `index` вдоль времени и пространству."""
        cls = self.__class__

        return cls(
            units=self.units,
            intensity=crop(self.intensity, index),
            clipped=crop(self.clipped, index),
            deviation=crop(self.deviation, index),
            meta=self.meta,
        )
