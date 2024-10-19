import pytest

from vmk_spectrum3_wrapper.measurement_manager import ExtendedSchema, to_microsecond
from vmk_spectrum3_wrapper.types import MilliSecond


@pytest.mark.parametrize('exposure', [(1, 1_000)])
@pytest.mark.parametrize('capacity', [(1_000, 1)])
def test_extended_schema(exposure: tuple[MilliSecond, MilliSecond], capacity: tuple[int, int]):
    schema = ExtendedSchema.create(
        exposure=exposure,
        capacity=capacity,
    )

    assert schema.duration_total == exposure[0]*capacity[0] + exposure[1]*capacity[1]
    assert schema.capacity_total == capacity[0] + capacity[1]
    assert list(schema) == [to_microsecond(exposure[1]), capacity[1], to_microsecond(exposure[0]), capacity[0]]
