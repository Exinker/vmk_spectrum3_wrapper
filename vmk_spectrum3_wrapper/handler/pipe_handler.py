from collections.abc import Sequence

from vmk_spectrum3_wrapper.data import Datum
from vmk_spectrum3_wrapper.handler.base_handler import BaseHandler
from vmk_spectrum3_wrapper.handler.buffer_handler import BufferHandler
from vmk_spectrum3_wrapper.handler.handler import Handler, ScaleHandler
from vmk_spectrum3_wrapper.units import Units


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
    def __call__(self, data: Datum, *args, **kwargs) -> Datum:

        for handler in self.handlers:
            data = handler(data, *args, **kwargs)

        return data

    def __getitem__(self, index: int) -> Handler:
        return self._handlers[index]
