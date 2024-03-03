import time
from typing import Callable

import numpy as np

from vmk_spectrum3_wrapper.handler import BufferHandler, PipeHandler
from vmk_spectrum3_wrapper.storage.storage.base_storage import BaseStorage
from vmk_spectrum3_wrapper.typing import Array, Digit, Second
from vmk_spectrum3_wrapper.units import Units, get_scale


class BufferStorage(Storage):

    def __init__(self, buffer_handler: PipeHandler, buffer_size: int) -> None:
        if isinstance(buffer_handler, PipeHandler):
            assert any(isinstance(h, BufferHandler) for h in buffer_handler), 'PipeHandler should contains one BufferHandler at least!'

        assert buffer_size > 1  # TODO: add message

        #
        super().__init__(handler=buffer_handler)

        self._buffer = []
        self._buffer_handler = buffer_handler
        self._buffer_size = buffer_size

    # --------        buffer        --------
    @property
    def buffer(self) -> list[Array[int]]:
        return self._buffer

    @property
    def buffer_size(self) -> int:
        return self._buffer_size

    @property
    def buffer_handler(self) -> BufferHandler | PipeHandler:
        return self._buffer_handler

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
        if len(self.buffer) == self.buffer_size:  # если буфер заполнен, то ранные обрабатываются `handler`, передаются в `data` и буфер очищается

            try:
                buffer = np.array(self.buffer)
                buffer = self.buffer_handler(buffer)

                self._data.append(buffer)

            finally:
                self._buffer.clear()

    def clear(self) -> None:
        """Clear buffer and data."""
        self._buffer.clear()
        self._data.clear()

    # --------        private        --------
    def __len__(self) -> int:
        return len(self._data)
