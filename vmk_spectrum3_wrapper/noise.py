from dataclasses import dataclass, field
from typing import overload

import numpy as np

from vmk_spectrum3_wrapper.detector import Detector
from vmk_spectrum3_wrapper.typing import Array, Electron, Percent, U


@dataclass(frozen=True)
class Noise():
    """Detector's noise dependence."""
    detector: Detector
    n_frames: int
    units: U = field(default=Percent)

    @overload
    def __call__(self, value: U) -> U: ...
    @overload
    def __call__(self, value: Array[U]) -> Array[U]: ...
    @overload
    def __call__(self, value):
        detector = self.detector
        n_frames = self.n_frames

        if self.units == Electron:
            read_noise = detector.config.read_noise

            return np.sqrt(read_noise**2 + value) / np.sqrt(n_frames)

        if self.units == Percent:
            read_noise = detector.config.read_noise
            kc = detector.config.capacity / 100

            return (1/kc) * np.sqrt(read_noise**2 + value*kc) / np.sqrt(n_frames)

        raise TypeError(f'{self.units} units is not supported!')
