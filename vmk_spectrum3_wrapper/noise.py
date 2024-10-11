from dataclasses import dataclass, field
from typing import overload

import numpy as np

from vmk_spectrum3_wrapper.adc import ADC
from vmk_spectrum3_wrapper.detector import Detector
from vmk_spectrum3_wrapper.types import Array, U
from vmk_spectrum3_wrapper.units import Units


@dataclass(frozen=True)
class Noise():
    """Detector's noise dependence."""
    detector: Detector
    adc: ADC = field(default=ADC._16bit)
    units: U = field(default=Units.percent)
    n_frames: int = field(default=1)

    @overload
    def __call__(self, value: U) -> U: ...
    @overload
    def __call__(self, value: Array[U]) -> Array[U]: ...
    def __call__(self, value):
        adc = self.adc
        detector = self.detector
        n_frames = self.n_frames

        if self.units == Units.digit:
            read_noise = detector.config.read_noise
            k = adc.value_max / detector.config.capacity

            return k * np.sqrt(read_noise**2 + value/k) / np.sqrt(n_frames)

        if self.units == Units.electron:
            read_noise = detector.config.read_noise

            return np.sqrt(read_noise**2 + value) / np.sqrt(n_frames)

        if self.units == Units.percent:
            read_noise = detector.config.read_noise
            k = 100 / detector.config.capacity

            return k * np.sqrt(read_noise**2 + value/k) / np.sqrt(n_frames)

        raise ValueError(f'{self.units} units is not supported!')
