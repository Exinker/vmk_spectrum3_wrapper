import time
from typing import Callable

import numpy as np

from vmk_spectrum3_wrapper.handler import ExtendedHandler, PipeHandler
from vmk_spectrum3_wrapper.storage.storage import Storage
from vmk_spectrum3_wrapper.typing import Array, Digit, Second
from vmk_spectrum3_wrapper.units import Units, get_scale


class ExtendedStorage(Storage):

    def __init__(self, handler: ExtendedHandler | PipeHandler, capacity: tuple[int, int]) -> None:
        if isinstance(handler, PipeHandler):
            assert any(isinstance(h, ExtendedHandler) for h in handler), 'PipeHandler should contains one ExtendedHandler at least!'

        #
        self._handler = handler
        self._capacity = capacity

        self._started_at = None  # время начала измерения первого кадра
        self._finished_at = None  # время начала измерения последнего кадра
        self._data = []
        self._buffer = []

    @property
    def handler(self) -> PipeHandler | ExtendedHandler:
        return self._handler

    @property
    def buffer(self) -> list[Array[int]]:
        return self._buffer

    @property
    def capacity(self) -> int:
        return sum(self._capacity)

    # --------        data        --------
    def put(self, frame: Array[int]) -> None:
        """Добавить новый кадр `frame` в буфер."""

        # time
        time_at = time.perf_counter()

        if self._started_at is None:
            self._started_at = time_at

        self._finished_at = time_at

        # buffer
        frame = frame.reshape(1, -1)
        self._buffer.append(frame)

        # data
        if len(self.buffer) == self.capacity:  # если буфер заполнен, то ранные обрабатываются `handler`, передаются в `data` и буфер очищается

            try:
                buffer = np.array(self.buffer)
                buffer = self.handler(buffer)

                self._data.append(buffer)

            finally:
                self._buffer.clear()

    def pull(self, clear: bool = True) -> Array[float]:
        """Pull data from storage."""

        try:
            return np.array(self.data)

        finally:
            if clear:
                self.clear()

    def clear(self) -> None:
        """Clear buffer and data."""
        self._buffer.clear()
        self._data.clear()

    # --------        private        --------
    def __len__(self) -> int:
        return len(self._data)
