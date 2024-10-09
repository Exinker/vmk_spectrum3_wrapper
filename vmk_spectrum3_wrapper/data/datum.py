import matplotlib.pyplot as plt

from vmk_spectrum3_wrapper.types import Array, U
from vmk_spectrum3_wrapper.units import Units

from .base_data import BaseData
from .utils import crop, reshape


class Datum(BaseData):

    def __init__(self, intensity: Array[U], units: Units, clipped: Array[bool] | None = None, deviation: Array[bool] | None = None):
        super().__init__(
            units=units,
            intensity=reshape(intensity),
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
            units=self.units,
            intensity=crop(self.intensity, index),
            clipped=crop(self.clipped, index),
            deviation=crop(self.deviation, index),
        )
