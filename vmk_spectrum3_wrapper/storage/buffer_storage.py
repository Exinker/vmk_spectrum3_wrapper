import time

import numpy as np

from vmk_spectrum3_wrapper.data import Datum, Meta
from vmk_spectrum3_wrapper.device import ADC_RESOLUTION
from vmk_spectrum3_wrapper.handler import BufferHandler, PipeHandler
from vmk_spectrum3_wrapper.storage.base_storage import BaseStorage
from vmk_spectrum3_wrapper.typing import Array
from vmk_spectrum3_wrapper.units import Units


class BufferStorage(BaseStorage):

    def __init__(self, handler: PipeHandler | None = None) -> None:
        if isinstance(handler, PipeHandler):
            assert any(isinstance(h, BufferHandler) for h in handler), 'PipeHandler should contains one BufferHandler at least!'

        #
        super().__init__(handler=handler)

        self._buffer = []

    @property
    def buffer(self) -> list[Array[int]]:
        return self._buffer

    # @property
    # def capacity(self) -> int | tuple[int, int]:
    #     """"Required `n_frames` to iteration."""
    #     return self._exposure

    #     if isinstance(self._capacity, int):
    #         return self._capacity
    #     if isinstance(self._capacity, Sequence):
    #         return sum(self._capacity)

    #     raise TypeError(f'Capacity: {type(self._capacity)} is not supported yet!')

    # --------        handlers        --------
    def put(self, frame: Array[int]) -> None:
        """Добавить новый кадр `frame` в буфер."""

        # time
        time_at = time.perf_counter()

        if self._started_at is None:
            self._started_at = time_at

        self._finished_at = time_at

        # buffer
        self.buffer.append(frame)

        # data
        if len(self.buffer) == self.capacity:  # если буфер заполнен, то ранные обрабатываются `handler`, передаются в `data` и буфер очищается

            #
            intensity = np.array(self.buffer)
            clipped = intensity == (2**ADC_RESOLUTION - 1)

            datum = Datum(
                intensity=intensity,
                units=Units.digit,
                clipped=clipped,
                meta=Meta(
                    capacity=self._capacity,
                    exposure=self._exposure,
                    started_at=None,
                    finished_at=time_at,
                ),
            )
            datum = self.handler(datum)

            self.data.append(datum)

            #
            self.buffer.clear()

    def clear(self) -> None:
        """Clear buffer and data."""
        self.buffer.clear()
        self.data.clear()

    # --------        private        --------
    def __len__(self) -> int:
        return len(self._data)
