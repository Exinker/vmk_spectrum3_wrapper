import pytest

from vmk_spectrum3_wrapper.exception import SetupDeviceError
from vmk_spectrum3_wrapper.measurement.schema import Schema, StandardSchema, ExtendedSchema, fetch_schema, to_microsecond
from vmk_spectrum3_wrapper.typing import MicroSecond, MilliSecond


# --------        to_microsecond        --------
@pytest.mark.parametrize(
    ['exposure', 'expected'],
    [
        (0, 0),
        (0.4, 400),
        (1., 1_000),
        (1, 1_000),
        (10, 10_000),
    ],
)
def test_to_microsecond(exposure: MilliSecond, expected: MicroSecond):
    assert to_microsecond(exposure) == expected


@pytest.mark.parametrize(
    ['exposure', 'expected'],
    [
        (-1, SetupDeviceError),
        (0.42, SetupDeviceError),
    ],
)
def test_to_microsecond_fail(exposure: MilliSecond, expected: SetupDeviceError):
    with pytest.raises(expected):
        to_microsecond(exposure)


# --------        standard schema        --------
@pytest.mark.parametrize(
    ['exposure', 'capacity'],
    [
        (1, 1),
        (10, 10),
    ],
)
def test_standard_schema(exposure: MilliSecond, capacity: int):
    schema = StandardSchema(exposure, capacity)

    assert schema.duration_total == exposure * capacity
    assert schema.capacity_total == capacity
