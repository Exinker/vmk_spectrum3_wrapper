import numpy as np
import pytest

from vmk_spectrum3_wrapper.data.exceptions import ArrayShapeError
from vmk_spectrum3_wrapper.data.utils import join
from vmk_spectrum3_wrapper.types import Array, U


@pytest.mark.parametrize(
    'n_values',
    [1, 2, 42],
)
def test_reshape_none(n_values: int):
    values = [None for _ in range(n_values)]

    values_joined = join(values)

    assert values_joined is None


@pytest.mark.parametrize(
    'n_times',
    [1, 2, 42],
)
@pytest.mark.parametrize(
    'n_numbers',
    [1, 2, 42],
)
@pytest.mark.parametrize(
    'n_values',
    [1, 2, 42],
)
def test_reshape(
    n_times: int,
    n_numbers: int,
    n_values: int,
):
    values = [np.random.randn(n_times, n_numbers) for _ in range(n_values)]

    values_joined = join(values)

    assert values_joined.shape == (n_times * n_values, n_numbers)
