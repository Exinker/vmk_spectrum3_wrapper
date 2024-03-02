import time
from typing import Callable

import numpy as np

from vmk_spectrum3_wrapper.storage.storage import DeviceStorage
from vmk_spectrum3_wrapper.typing import Array, Digit, Second
from vmk_spectrum3_wrapper.units import Units, get_scale


class DeviceBufferStorage(DeviceStorage):

    def __init__(self, buffer_size: int, buffer_handler: Callable[[Array[int]], Array[int]] | None = None, units: Units = Units.percent) -> None:
        assert buffer_size > 1  # TODO: add message

        #
        super().__init__(units=units)

        self._started_at = None  # время начала измерения первого кадра
        self._finished_at = None  # время начала измерения последнего кадра

        self._buffer = []
        self._buffer_size = buffer_size
        self._buffer_handler = buffer_handler

        self._data = []

    # --------        buffer        --------
    @property
    def buffer(self) -> list[Array[int]]:
        return self._buffer

    @property
    def buffer_size(self) -> int:
        return self._buffer_size

    @property
    def buffer_handler(self) -> Callable[[Array[float]], Array[float]]:
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
        frame = self.scale * frame  # scaling data
        self._buffer.append(frame)

        # data
        if len(self.buffer) == self.buffer_size:  # если буфер заполнен, то ранные обрабатываются `handler`, передаются в `data` и буфер очищается

            try:
                # buffer
                buffer = np.array(self.buffer)
                if self.buffer_handler:
                    buffer = self.buffer_handler(buffer)

                #  data
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
