import time
from collections.abc import Sequence

import numpy as np

from vmk_spectrum3_wrapper.handler import BufferHandler, PipeHandler
from vmk_spectrum3_wrapper.storage.base_storage import BaseStorage
from vmk_spectrum3_wrapper.typing import Array


class BufferStorage(BaseStorage):

    def __init__(self, handler: PipeHandler, capacity: int | tuple[int, int]) -> None:
        if isinstance(handler, PipeHandler):
            assert any(isinstance(h, BufferHandler) for h in handler), 'PipeHandler should contains one BufferHandler at least!'
        if isinstance(capacity, int):
            assert capacity > 1  # TODO: add message

        #
        super().__init__(handler=handler)

        self._buffer = []
        self._capacity = capacity

    # --------        buffer        --------
    @property
    def buffer(self) -> list[Array[int]]:
        return self._buffer

    @property
    def capacity(self) -> int:
        """"Required `n_frames` to iteration."""

        if isinstance(self._capacity, int):
            return self._capacity
        if isinstance(self._capacity, Sequence):
            return sum(self._capacity)

        raise TypeError(f'Capacity: {type(self._capacity)} is not supported yet!')

    # --------        data        --------
    def put(self, frame: Array[int]) -> None:
        """Добавить новый кадр `frame` в буфер."""

        # time
        time_at = time.perf_counter()

        if self._started_at is None:
            self._started_at = time_at

        self._finished_at = time_at

        # buffer
        self._buffer.append(frame.reshape(1, -1))

        # data
        if len(self.buffer) == self.capacity:  # если буфер заполнен, то ранные обрабатываются `handler`, передаются в `data` и буфер очищается

            try:
                datum = self.handler(data=np.array(self.buffer), capacity=self._capacity, exposure=self._exposure)
                self._data.append(datum.flatten())

            finally:
                self._buffer.clear()

    def clear(self) -> None:
        """Clear buffer and data."""
        self._buffer.clear()
        self._data.clear()

    # --------        private        --------
    def __len__(self) -> int:
        return len(self._data)
