import time

from vmk_spectrum3_wrapper.data import Datum, Meta
from vmk_spectrum3_wrapper.handler import ClipHandler, PipeHandler, ScaleHandler, SwapHandler
from vmk_spectrum3_wrapper.storage.base_storage import BaseStorage
from vmk_spectrum3_wrapper.typing import Array, Digit
from vmk_spectrum3_wrapper.units import Units


class FrameStorage(BaseStorage):

    def __init__(self, handler: PipeHandler | None = None) -> None:
        super().__init__(handler=handler or PipeHandler([SwapHandler(), ClipHandler(), ScaleHandler()]))

    # --------        handlers        --------
    def put(self, frame: Array[Digit]) -> None:
        """Add the frame to storage."""

        # time
        time_at = time.perf_counter()

        if self._started_at is None:
            self._started_at = time_at

        self._finished_at = time_at

        # data
        datum = Datum(
            intensity=frame,
            units=Units.digit,
            meta=Meta(
                capacity=self._capacity,
                exposure=self._exposure,
                started_at=None,
                finished_at=time_at,
            ),
        )
        datum = self.handler(datum)

        self.data.append(datum)

    def clear(self) -> None:
        """Clear storage."""
        self.data.clear()
