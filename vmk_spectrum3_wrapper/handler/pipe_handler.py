from collections.abc import Sequence
import time

import numpy as np

from vmk_spectrum3_wrapper.typing import Array, Digit, Second, T
from vmk_spectrum3_wrapper.handler import Handler


class PipeHandler(Handler):

    def __init__(self, __handlers: Sequence[Handler]):
        self._handlers = __handlers

    @property
    def handlers(self) -> Sequence[Handler]:
        return self._handlers

    # --------        private        --------
    def __call__(self, data: Array[Digit]) -> Array[T]:
        data = data.copy()

        for handler in self.handlers:
            data = handler(data)

        return data

    def __getitem__(self, index: int) -> Handler:
        return self._handlers[index]
