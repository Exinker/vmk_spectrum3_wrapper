from collections.abc import Sequence
from typing import overload

import numpy as np

from vmk_spectrum3_wrapper.types import Array, U


@overload
def reshape(value: Array[U], flatten: bool = False) -> Array[U]: ...
@overload
def reshape(value: None, flatten: bool = False) -> None: ...
def reshape(value, flatten=False):

    if value is None:
        return None

    if value.ndim == 1:
        if flatten:
            return value

        return value.reshape(1, -1)

    if value.ndim == 2:
        if flatten and (value.shape[0] == 1):
            return value.reshape(-1)

        return value

    raise ValueError


@overload
def crop(value: None, index: tuple) -> None: ...
@overload
def crop(value: Array[U], index) -> Array[U]: ...
@overload
def crop(value: Array[bool], index) -> Array[bool]: ...
def crop(value, index):
    if value is None:
        return None

    time, number = index
    return value[time, number]


@overload
def split(value: Array[U], index: Array[int]) -> Array[U]: ...
@overload
def split(value: Array[bool], index: Array[int]) -> Array[bool]: ...
@overload
def split(value: None, index: Array[int]) -> None: ...
def split(value, index):
    if value is None:
        return None

    if value.ndim == 1:
        return value

    return value[index, :]


@overload
def join(values: Sequence[Array[U]]) -> Array[U]: ...
@overload
def join(values: Sequence[Array[bool]]) -> Array[bool]: ...
def join(values):
    if values[0] is None:
        return None

    return np.concatenate(values)
