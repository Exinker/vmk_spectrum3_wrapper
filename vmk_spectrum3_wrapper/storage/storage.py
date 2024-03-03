import time

from vmk_spectrum3_wrapper.handler import PipeHandler
from vmk_spectrum3_wrapper.storage.base_storage import BaseStorage
from vmk_spectrum3_wrapper.typing import Array, Digit


class Storage(BaseStorage):

    def __init__(self, handler: PipeHandler | None = None) -> None:
        super().__init__(handler=handler)

        self._capacity = 1

    @property
    def capacity(self) -> int:
        """"Required `n_frames` to iteration."""

        return self._capacity

    def put(self, frame: Array[Digit]) -> None:
        """Add the frame to storage."""

        # time
        time_at = time.perf_counter()

        if self._started_at is None:
            self._started_at = time_at

        self._finished_at = time_at

        # data
        datum = self.handler(frame.reshape(1, -1))
        self._data.append(datum.flatten())

    def clear(self) -> None:
        """Clear storage."""
        self._data.clear()
