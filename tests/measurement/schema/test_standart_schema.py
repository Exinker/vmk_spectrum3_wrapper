import pytest

from vmk_spectrum3_wrapper.measurement_manager import StandardSchema, to_microsecond
from vmk_spectrum3_wrapper.types import MilliSecond


@pytest.mark.parametrize('exposure', [.4, 1, 10, 100])
@pytest.mark.parametrize('capacity', [1, 10, 100])
def test_standart_schema(exposure: MilliSecond, capacity: int):
    schema = StandardSchema.create(
        exposure=exposure,
        capacity=capacity,
    )

    assert schema.duration_total == exposure * capacity
    assert schema.capacity_total == capacity
    assert list(schema) == [to_microsecond(exposure)]
