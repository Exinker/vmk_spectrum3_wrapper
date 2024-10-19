import numpy as np
import pytest

from vmk_spectrum3_wrapper.config import DEFAULT_DETECTOR
from vmk_spectrum3_wrapper.data.exceptions import ArrayShapeError
from vmk_spectrum3_wrapper.data.utils import reshape
from vmk_spectrum3_wrapper.types import Array, U


def test_reshape_none():
    value = None

    assert reshape(value) is None


@pytest.mark.parametrize(
    'value',
    [
        np.random.randn(2048),
        np.random.randn(1, 2048),
    ],
)
def test_reshape(value: Array[U]):
    value_reshaped = reshape(value)

    assert value_reshaped.ndim == 2
    assert value_reshaped.shape == (1, value.size)


@pytest.mark.parametrize(
    'value',
    [
        np.random.randn(2048),
        np.random.randn(1, 2048),
    ],
)
def test_reshape_flatten(value: Array[U]):
    value_reshaped = reshape(value, flatten=True)

    assert value_reshaped.ndim == 1
    assert value_reshaped.shape == (value.size, )


@pytest.mark.parametrize(
    'value',
    [
        np.random.randn(2, 2048),
    ],
)
def test_reshape_flatten_error(value: Array[U]):

    with pytest.raises(ArrayShapeError):
        reshape(value, flatten=True)


def test_reshape_high_dimention_error():
    value = np.random.randn(1, 1, 2048)

    with pytest.raises(ArrayShapeError):
        reshape(value, flatten=True)
