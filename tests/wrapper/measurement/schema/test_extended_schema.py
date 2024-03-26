import pytest

from vmk_spectrum3_wrapper.exception import SetupDeviceError
from vmk_spectrum3_wrapper.measurement.schema import ExtendedSchema, to_microsecond
from vmk_spectrum3_wrapper.typing import MilliSecond


@pytest.fixture(params=[
        dict(exposure=(1, 1), capacity=(1, 1)),
        dict(exposure=(1, 2), capacity=(2, 1)),
])
def schema(request) -> ExtendedSchema:
    return ExtendedSchema(**request.param)


def test_duration_total(schema: ExtendedSchema):
    assert schema.duration_total == sum(
        exposure * capacity
        for exposure, capacity in zip(schema.exposure, schema.capacity)
    )


def test_capacity_total(schema: ExtendedSchema):
    assert schema.capacity_total == sum(schema.capacity)


def test_schema_unpacking(schema: ExtendedSchema):
    assert [*schema] == [
        to_microsecond(schema.exposure[1]), schema.capacity[1],
        to_microsecond(schema.exposure[0]), schema.capacity[0],
    ]  # TODO: items are reversed for compatibility with `Atom`


@pytest.mark.parametrize(
    ['exposure', 'capacity', 'expected'],
    [
        (1, (100, 1), SetupDeviceError),
        ((1, 100), 1, SetupDeviceError),
        ((1, ), (100, 1), SetupDeviceError),
        ((1, 100), (100, ), SetupDeviceError),
    ],
)
def test_schema_fail(exposure: MilliSecond, capacity: int, expected: SetupDeviceError):
    with pytest.raises(expected):
        ExtendedSchema(exposure, capacity)
