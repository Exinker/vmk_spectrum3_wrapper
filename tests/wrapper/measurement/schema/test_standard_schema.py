import pytest

from vmk_spectrum3_wrapper.exception import SetupDeviceError
from vmk_spectrum3_wrapper.measurement import StandardSchema, to_microsecond
from vmk_spectrum3_wrapper.types import MilliSecond


@pytest.fixture(params=[
        dict(exposure=1, capacity=1),
        dict(exposure=2, capacity=4),
])
def schema(request) -> StandardSchema:
    return StandardSchema(**request.param)


def test_duration_total(schema: StandardSchema):
    assert schema.duration_total == schema.exposure * schema.capacity


def test_capacity_total(schema: StandardSchema):
    assert schema.capacity_total == schema.capacity


def test_schema_unpacking(schema: StandardSchema):
    assert [*schema] == [to_microsecond(schema.exposure)]


@pytest.mark.parametrize(
    ['exposure', 'capacity', 'expected'],
    [
        ('1', 1, SetupDeviceError),
        (0, 1, SetupDeviceError),
        (1, 1., SetupDeviceError),
        (1, 0, SetupDeviceError),
        (1, 2**24, SetupDeviceError),
    ],
)
def test_schema_fail(exposure: MilliSecond, capacity: int, expected: SetupDeviceError):

    with pytest.raises(expected):
        StandardSchema(exposure, capacity)
