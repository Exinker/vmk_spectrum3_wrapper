from collections.abc import Sequence

from vmk_spectrum3_wrapper.data import Datum
from vmk_spectrum3_wrapper.handler.base_handler import BaseHandler
from vmk_spectrum3_wrapper.handler.buffer_handler import BufferHandler
from vmk_spectrum3_wrapper.handler.frame_handler import ClipHandler, FrameHandler, ScaleHandler, SwapHandler
from vmk_spectrum3_wrapper.units import Units


class PipeHandler(BaseHandler):

    def __init__(self, __handlers: Sequence[FrameHandler | BufferHandler] | None = None):
        if __handlers:
            assert isinstance(__handlers[0], SwapHandler), '`SwapHandler` have to be the first in a sequence!'
            assert isinstance(__handlers[1], ClipHandler), '`ClipHandler` have to be the second in a sequence!'
            assert isinstance(__handlers[2], ScaleHandler), '`ScaleHandler` have to be the third in a sequence!'

        self._handlers = __handlers or [
            SwapHandler(),
            ClipHandler(),
            ScaleHandler(),
        ]

    @property
    def handlers(self) -> Sequence[FrameHandler]:
        return self._handlers

    @property
    def units(self) -> Units:
        return self.handlers[0].units

    # --------        private        --------
    def __call__(self, datum: Datum, *args, **kwargs) -> Datum:
        for handler in self.handlers:
            datum = handler(datum, *args, **kwargs)

        return datum

    def __getitem__(self, index: int) -> FrameHandler:
        return self._handlers[index]
