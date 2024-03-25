import pytest

from vmk_spectrum3_wrapper.measurement.schema import Schema, StandardSchema, ExtendedSchema, fetch_schema
from vmk_spectrum3_wrapper.typing import MilliSecond


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
