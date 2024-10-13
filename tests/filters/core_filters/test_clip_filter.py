import numpy as np
import pytest

from vmk_spectrum3_wrapper.adc import ADC
from vmk_spectrum3_wrapper.config import DEFAULT_ADC
from vmk_spectrum3_wrapper.data import Datum
from vmk_spectrum3_wrapper.filters.core_filters import ClipFilter
from vmk_spectrum3_wrapper.filters.exceptions import DatumFilterError, FilterError
from vmk_spectrum3_wrapper.types import Array, Digit, U
from vmk_spectrum3_wrapper.units import Units


def test_clip_filter_default():
    filter = ClipFilter()

    assert filter.adc == DEFAULT_ADC
    assert filter.value_max == DEFAULT_ADC.value_max


@pytest.mark.parametrize(
    'adc',
    [adc for adc in ADC if adc != DEFAULT_ADC],
)
def test_clip_filter_non_default(
    adc: ADC,
):
    with pytest.raises(FilterError):
        ClipFilter(
            adc=adc,
        )


@pytest.mark.parametrize(
    'units',
    [units for units in Units if units != Units.digit],
)
def test_clip_filter_call_with_units_error(
    fake_digit_intensity: Array[Digit],
    units: Units,
):
    datum = Datum(
        units=units,
        intensity=fake_digit_intensity,
    )

    filter = ClipFilter()

    with pytest.raises(DatumFilterError):
        filter(
            datum=datum,
        )


@pytest.mark.parametrize(
    'intensity',
    [
        (np.random.randn(2048) > 0),
        (np.random.randn(2048) > 0) + DEFAULT_ADC.value_max-1,
        np.linspace(0, DEFAULT_ADC.value_max, 2048),
    ],
)
def test_clip_filter_call(
    intensity: Array[U],
):
    assert np.all((intensity >= 0) & (intensity <= DEFAULT_ADC.value_max))

    datum = Datum(
        units=Units.digit,
        intensity=intensity,
    )
    filter = ClipFilter()

    filtrated_datum = filter(
        datum=datum,
    )

    assert isinstance(filtrated_datum, Datum)
    assert np.all(np.isclose(
        intensity >= filter.value_max,
        filtrated_datum.clipped,
    ))
