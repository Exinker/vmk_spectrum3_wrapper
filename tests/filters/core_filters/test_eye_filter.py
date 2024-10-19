import numpy as np
import pytest

from tests.utils import calculate_clipped, calculate_deviation
from vmk_spectrum3_wrapper.config import DEFAULT_DETECTOR
from vmk_spectrum3_wrapper.data import Datum
from vmk_spectrum3_wrapper.measurement_manager.filters.core_filters import EyeFilter
from vmk_spectrum3_wrapper.types import Array, Percent
from vmk_spectrum3_wrapper.units import Units


@pytest.mark.parametrize(
    'intensity',
    [
        np.random.randn(DEFAULT_DETECTOR.config.n_pixels),
        np.random.randn(DEFAULT_DETECTOR.config.n_pixels) + 100,
        np.linspace(0, 100, DEFAULT_DETECTOR.config.n_pixels),
    ],
)
def test_eye_filter_call(
    intensity: Array[Percent],
):
    units = Units.percent
    datum = Datum(
        units=units,
        intensity=intensity,
        clipped=calculate_clipped(intensity, units=units),
        deviation=calculate_deviation(intensity, units=units),
    )
    filter = EyeFilter()

    datum_filtrated = filter(
        datum=datum,
    )

    assert datum_filtrated.units == datum.units
    assert datum_filtrated.n_times == datum.n_times
    assert datum_filtrated.n_numbers == datum.n_numbers
    assert np.all(np.isclose(
        datum_filtrated.intensity,
        datum.intensity,
    ))
    assert np.all(np.isclose(
        datum_filtrated.clipped,
        datum.clipped,
    ))
    assert np.all(np.isclose(
        datum_filtrated.deviation,
        datum.deviation,
    ))
