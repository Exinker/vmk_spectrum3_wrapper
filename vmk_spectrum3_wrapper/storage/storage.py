import time

import numpy as np

from vmk_spectrum3_wrapper.handler import PipeHandler
from vmk_spectrum3_wrapper.storage.base_storage import BaseStorage
from vmk_spectrum3_wrapper.typing import Array, Digit, Second
from vmk_spectrum3_wrapper.units import Units, get_scale


class Storage(BaseStorage):

    def __init__(self, handler: PipeHandler | None = None) -> None:
        super().__(handler=handler)

    def put(self, frame: Array[Digit]) -> None:
        """Add the frame to storage."""

        # time
        time_at = time.perf_counter()

        if self._started_at is None:
            self._started_at = time_at

        self._finished_at = time_at

        # data
        frame = frame.reshape(1, -1)
        frame = self.handler(frame) if self.handler else frame

        self._data.append(frame)

    def clear(self) -> None:
        """Clear storage."""
        self._data.clear()
