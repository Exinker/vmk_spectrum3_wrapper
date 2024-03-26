import pytest

from vmk_spectrum3_wrapper.measurement.schema import to_microsecond
from vmk_spectrum3_wrapper.typing import MicroSecond, MilliSecond


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
