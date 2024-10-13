from typing import Callable

import numpy as np
import pytest

from tests.utils import calculate_clipped, calculate_deviation
from vmk_spectrum3_wrapper.config import DEFAULT_ADC, DEFAULT_DETECTOR
from vmk_spectrum3_wrapper.data import Data
from vmk_spectrum3_wrapper.types import Array, Digit, U
from vmk_spectrum3_wrapper.units import Units


@pytest.fixture
def fake_digit_intensity() -> Array[Digit]:

    def inner() -> Array[Digit]:  # TODO: add random generator
        intensity = np.linspace(0, DEFAULT_ADC.value_max, DEFAULT_DETECTOR.config.n_pixels)

        return intensity

    intensity = inner()
    assert np.all((intensity >= 0) & (intensity <= DEFAULT_ADC.value_max))

    return intensity


@pytest.fixture
def fake_offset_factory() -> Callable:

    def inner(__value: U) -> Array[U]:
        return np.full(DEFAULT_DETECTOR.config.n_pixels, fill_value=__value)

    return inner



@pytest.fixture
def fake_offset() -> Data:
    units = Units.percent
    intensity = np.full(DEFAULT_DETECTOR.config.n_pixels, 5)

    return Data(
        units=units,
        intensity=intensity,
        clipped=calculate_clipped(intensity, units=units),
        deviation=calculate_deviation(intensity, units=units),
    )
