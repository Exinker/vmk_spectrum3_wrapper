import numpy as np
import pytest

from vmk_spectrum3_wrapper.data import Datum
from vmk_spectrum3_wrapper.filters.core_filters import ScaleFilter
from vmk_spectrum3_wrapper.filters.exceptions import DatumFilterError
from vmk_spectrum3_wrapper.types import Array, Digit
from vmk_spectrum3_wrapper.units import Units


def test_scale_filter_default():
    filter = ScaleFilter()

    assert filter.units == Units.percent
    assert filter.scale == Units.percent.scale


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

    filter = ScaleFilter()

    with pytest.raises(DatumFilterError):
        filter(
            datum=datum,
        )


@pytest.mark.parametrize(
    'units',
    [units for units in Units],
)
def test_scale_filter_call(
    fake_digit_intensity: Array[Digit],
    units: Units,
):
    datum = Datum(
        units=Units.digit,
        intensity=fake_digit_intensity,
    )
    filter = ScaleFilter(
        units=units,
    )

    datum_filtrated = filter(
        datum=datum,
    )

    assert np.all(np.isclose(
        datum_filtrated.intensity,
        fake_digit_intensity * units.scale,
    ))
