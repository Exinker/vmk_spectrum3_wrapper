import numpy as np
import pytest

from tests.utils import calculate_clipped, calculate_deviation
from vmk_spectrum3_wrapper.config import DEFAULT_DETECTOR
from vmk_spectrum3_wrapper.data import Data, Datum
from vmk_spectrum3_wrapper.measurement_manager.filters.core_filters import OffsetFilter
from vmk_spectrum3_wrapper.types import Array, Percent
from vmk_spectrum3_wrapper.units import Units


def test_offset_filter_skip():
    filter = OffsetFilter(
        offset=None,
    )

    assert filter is None


def test_offset_filter_default(
    fake_offset: Data,
):
    filter = OffsetFilter(
        offset=fake_offset,
    )

    assert filter.offset == fake_offset


@pytest.mark.parametrize(
    'intensity',
    [
        np.random.randn(DEFAULT_DETECTOR.config.n_pixels),
        np.random.randn(DEFAULT_DETECTOR.config.n_pixels) + 100,
        np.linspace(0, 100, DEFAULT_DETECTOR.config.n_pixels),
    ],
)
def test_offset_filter_call(
    intensity: Array[Percent],
    fake_offset: Data,
):
    units = Units.percent
    datum = Datum(
        units=units,
        intensity=intensity,
        clipped=calculate_clipped(intensity, units=units),
        deviation=calculate_deviation(intensity, units=units),
    )
    filter = OffsetFilter(
        offset=fake_offset,
    )

    datum_filtrated = filter(
        datum=datum,
    )

    assert datum_filtrated.units == datum.units
    assert datum_filtrated.n_times == datum.n_times
    assert datum_filtrated.n_numbers == datum.n_numbers
    assert np.all(np.isclose(
        datum_filtrated.intensity,
        datum.intensity - fake_offset.intensity,
    ))
    assert np.all(np.isclose(
        datum_filtrated.clipped,
        datum.clipped | fake_offset.clipped,
    ))
    assert np.all(np.isclose(
        datum_filtrated.deviation,
        np.sqrt(datum.deviation**2 + fake_offset.deviation**2),
    ))
