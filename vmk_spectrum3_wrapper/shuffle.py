from typing import overload

from vmk_spectrum3_wrapper.typing import Array, Digit


class Shuffle:

    def __init__(self):
        pass

    # --------        private        --------
    @overload
    def __call__(self, value: Array[Digit]) -> Array[Digit]: ...
    @overload
    def __call__(self, value: Array[bool]) -> Array[bool]: ...
    def __call__(self, value):
        raise NotImplementedError
