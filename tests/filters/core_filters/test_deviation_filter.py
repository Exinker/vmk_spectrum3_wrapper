import numpy as np
import pytest

from tests.utils import calculate_deviation
from vmk_spectrum3_wrapper.config import DEFAULT_ADC, DEFAULT_DETECTOR
from vmk_spectrum3_wrapper.data import Data, Datum
from vmk_spectrum3_wrapper.measurement_manager.filters.core_filters import DeviationFilter
from vmk_spectrum3_wrapper.noise import Noise
from vmk_spectrum3_wrapper.types import Array, Digit
from vmk_spectrum3_wrapper.units import Units


def test_deviation_filter_skip():
    filter = DeviationFilter(
        offset=None,
    )

    assert filter is None


@pytest.mark.parametrize(
    'units',
    [units for units in Units],
)
def test_deviation_filter_default(
    fake_offset: Data,
    units: Units,
):
    filter = DeviationFilter(
        offset=fake_offset,
        units=units,
    )

    assert filter.units == units
    assert filter.noise == Noise(
        detector=DEFAULT_DETECTOR,
        adc=DEFAULT_ADC,
        units=units,
        n_frames=1,
    )


@pytest.mark.parametrize(
    ['units', 'intensity'],
    [
        (Units.digit, np.linspace(0, DEFAULT_ADC.value_max, DEFAULT_DETECTOR.config.n_pixels)),
        (Units.electron, np.linspace(0, DEFAULT_ADC.value_max, DEFAULT_DETECTOR.config.n_pixels)*DEFAULT_DETECTOR.config.capacity/DEFAULT_ADC.value_max),
        (Units.percent, np.linspace(0, DEFAULT_ADC.value_max, DEFAULT_DETECTOR.config.n_pixels)*100/DEFAULT_ADC.value_max),
    ],
)
def test_deviation_filter_call(
    units: Units,
    intensity: Array[Digit],
    fake_offset: Data,
):
    datum = Datum(
        units=units,
        intensity=intensity,
    )
    filter = DeviationFilter(
        offset=fake_offset,
        units=units,
    )

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
        datum_filtrated.deviation,
        calculate_deviation(datum.intensity, units=units),
    ))
