import pickle
from collections.abc import Sequence
from dataclasses import dataclass

import matplotlib.pyplot as plt

from vmk_spectrum3_wrapper.typing import Array, MilliSecond, U
from vmk_spectrum3_wrapper.units import Units

from .base_data import BaseData
from .datum import Datum
from .utils import crop, join, reshape


@dataclass(frozen=True, slots=True)
class DataMeta:
    exposure: MilliSecond | tuple[MilliSecond, MilliSecond]
    capacity: int | tuple[int, int]
    started_at: float
    finished_at: float


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
