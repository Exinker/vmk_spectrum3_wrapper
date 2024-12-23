from typing import overload

from vmk_spectrum3_wrapper.types import Array, Digit


class Shuffle:
    """Смещения и перестановок объект."""

    def __init__(self):
        pass

    @overload
    def __call__(self, value: Array[Digit]) -> Array[Digit]: ...
    @overload
    def __call__(self, value: Array[bool]) -> Array[bool]: ...
    def __call__(self, value):
        raise NotImplementedError
