import numpy as np

from vmk_spectrum3_wrapper.config import DEFAULT_ADC, DEFAULT_DETECTOR
from vmk_spectrum3_wrapper.types import Array, U
from vmk_spectrum3_wrapper.units import Units


def calculate_clipped(__value: Array[U], units: Units) -> Array[U]:

    if units == Units.digit:
        return __value >= DEFAULT_ADC.value_max

    if units == Units.electron:
        return __value >= DEFAULT_DETECTOR.config.capacity

    if units == Units.percent:
        return __value >= 100

    raise ValueError(f'{units} units is not supported!')


def calculate_deviation(__value: Array[U], units: Units) -> Array[U]:

    if units == Units.digit:
        read_noise = DEFAULT_DETECTOR.config.read_noise
        k = DEFAULT_ADC.value_max / DEFAULT_DETECTOR.config.capacity
        return k * np.sqrt(read_noise**2 + abs(__value)/k)

    if units == Units.electron:
        read_noise = DEFAULT_DETECTOR.config.read_noise
        return np.sqrt(read_noise**2 + abs(__value))

    if units == Units.percent:
        read_noise = DEFAULT_DETECTOR.config.read_noise
        k = 100 / DEFAULT_DETECTOR.config.capacity
        return k * np.sqrt(read_noise**2 + abs(__value)/k)

    raise ValueError(f'{units} units is not supported!')
