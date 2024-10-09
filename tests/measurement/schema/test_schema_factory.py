import pytest

from vmk_spectrum3_wrapper.measurement.exceptions import SchemaError
from vmk_spectrum3_wrapper.measurement.schema import ExtendedSchema, StandardSchema, schema_factory
from vmk_spectrum3_wrapper.types import MilliSecond


@pytest.mark.parametrize(
    ['exposure', 'capacity'],
    [
        (1, 1_000),
    ],
)
def test_standart_schema(exposure: MilliSecond, capacity: int):
    schema = schema_factory(
        exposure=exposure,
        capacity=capacity,
    )

    assert isinstance(schema, StandardSchema)


@pytest.mark.parametrize(
    ['exposure', 'capacity'],
    [
        ((1, 1_000), (1_000, 1)),
    ],
)
def test_extended_schema(exposure: tuple[MilliSecond, MilliSecond], capacity: tuple[int, int]):
    schema = schema_factory(
        exposure=exposure,
        capacity=capacity,
    )

    assert isinstance(schema, ExtendedSchema)


@pytest.mark.parametrize(
    ['exposure', 'capacity'],
    [
        ((1, 1_000), 1),
        (1, (1, 1_000)),
    ],
)
def test_not_supported_schema(exposure: tuple[MilliSecond, MilliSecond] | MilliSecond, capacity: tuple[int, int] | int):

    with pytest.raises(SchemaError):
        schema_factory(
            exposure=exposure,
            capacity=capacity,
        )
