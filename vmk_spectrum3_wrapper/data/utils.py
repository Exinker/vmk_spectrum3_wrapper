from collections.abc import Sequence
from typing import overload

import numpy as np

from vmk_spectrum3_wrapper.typing import Array, U


@overload
def reshape(value: Array[U]) -> Array[U]: ...
@overload
def reshape(value: None) -> None: ...
def reshape(value):

    if value is None:
        return None
    if (value.ndim == 2) and (value.shape[0] == 1):
        return value.flatten()

    return value


@overload
def crop(value: Array[U], index: Array[int]) -> Array[U]: ...
@overload
def crop(value: Array[bool], index: Array[int]) -> Array[bool]: ...
@overload
def crop(value: None, index: Array[int]) -> None: ...
def crop(value, index):
    if value is None:
        return None

    return value[index, :]


@overload
def collapse(values: Sequence[Array[U]]) -> Array[U]: ...
@overload
def collapse(values: Sequence[Array[bool]]) -> Array[bool]: ...
def collapse(values):
    if values[0] is None:
        return None

    return np.array(values)
