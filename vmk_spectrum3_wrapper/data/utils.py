from collections.abc import Sequence
from typing import overload

import numpy as np

from vmk_spectrum3_wrapper.data.exceptions import ArrayShapeError
from vmk_spectrum3_wrapper.types import Array, U


@overload
def crop(
    __value: None,
    index: tuple[int | Array[int] | slice, int | Array[int] | slice],
) -> None: ...
@overload
def crop(
    __value: Array[U],
    index: tuple[int | Array[int] | slice, int | Array[int] | slice],
) -> Array[U]: ...
@overload
def crop(
    __value: Array[bool],
    index: tuple[int | Array[int] | slice, int | Array[int] | slice],
) -> Array[bool]: ...
def crop(__value, index):

    if __value is None:
        return None

    time, number = index
    return __value[time, number]


@overload
def reshape(__value: Array[U], flatten: bool = False) -> Array[U]: ...
@overload
def reshape(__value: None, flatten) -> None: ...
def reshape(__value, flatten=False):

    if __value is None:
        return None

    if __value.ndim == 1:
        if flatten:
            return __value

        return __value.reshape(1, -1)

    if __value.ndim == 2:
        if flatten:
            if __value.shape[0] == 1:
                return __value.reshape(-1)

            raise ArrayShapeError(f'Array with shape: {__value.shape} could not be flattened!')

        return __value

    raise ArrayShapeError(f'Array with shape: {__value.shape} is not supported!')


@overload
def join(__values: Sequence[Array[U]]) -> Array[U]: ...
@overload
def join(__values: Sequence[Array[bool]]) -> Array[bool]: ...
@overload
def join(__values: Sequence[None]) -> None: ...
def join(__values):

    if __values[0] is None:
        return None

    return np.concatenate(__values)
