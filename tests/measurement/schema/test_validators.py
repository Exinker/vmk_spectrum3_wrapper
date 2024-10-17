import pytest

from vmk_spectrum3_wrapper.measurement_manager.exceptions import SchemaCapacityError, SchemaExposureError
from vmk_spectrum3_wrapper.measurement_manager.schemas import ExtendedSchema, StandardSchema
from vmk_spectrum3_wrapper.types import MilliSecond


@pytest.mark.parametrize('exposure', ['.4', 0, 0.999, 1.001])
def test_standart_schema_exposure_error(exposure: MilliSecond):
    capacity = 1

    with pytest.raises(SchemaExposureError):
        StandardSchema.create(
            exposure=exposure,
            capacity=capacity,
        )


@pytest.mark.parametrize('capacity', [1., 0, 2**24])
def test_standart_schema_capacity_error(capacity: int):
    exposure = 1

    with pytest.raises(SchemaCapacityError):
        StandardSchema.create(
            exposure=exposure,
            capacity=capacity,
        )


@pytest.mark.parametrize('exposure', [(1, ), (1, 1, 1)])
def test_extended_schema_exposure_error(exposure: tuple[MilliSecond, MilliSecond]):
    capacity = [1, 1]

    with pytest.raises(SchemaExposureError):
        ExtendedSchema.create(
            exposure=exposure,
            capacity=capacity,
        )


@pytest.mark.parametrize('capacity', [(1, ), (1, 1, 1)])
def test_extended_schema_capacity_error(capacity: tuple[int, int]):
    exposure = [1, 1]

    with pytest.raises(SchemaCapacityError):
        ExtendedSchema.create(
            exposure=exposure,
            capacity=capacity,
        )
