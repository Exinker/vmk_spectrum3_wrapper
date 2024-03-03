from collections.abc import Sequence
import time

import numpy as np

from vmk_spectrum3_wrapper.handler.base_handler import BaseHandler
from vmk_spectrum3_wrapper.handler import BufferHandler, Handler, ScaleHandler
from vmk_spectrum3_wrapper.typing import Array, Digit, Second, T


class PipeHandler(BaseHandler):

    def __init__(self, __handlers: Sequence[Handler | BufferHandler] | None = None):
        if __handlers:
            assert isinstance(__handlers[0], ScaleHandler), '`ScaleHandler` have to be the first in sequence!'

        self._handlers = __handlers or [
            ScaleHandler(),
        ]

    @property
    def handlers(self) -> Sequence[Handler]:
        return self._handlers

    @property
    def units(self) -> Units:
        return self.handlers[0].units

    # --------        private        --------
    def __call__(self, data: Array[Digit], *args, **kwargs) -> Array[T]:
        data = data.copy()

        for handler in self.handlers:
            data = handler(data, *args, **kwargs)

        return data

    def __getitem__(self, index: int) -> Handler:
        return self._handlers[index]
