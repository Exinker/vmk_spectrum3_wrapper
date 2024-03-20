import time
from collections.abc import Sequence

import numpy as np

from vmk_spectrum3_wrapper.data import Datum, Meta
from vmk_spectrum3_wrapper.filter.buffer_filter import BufferFilter
from vmk_spectrum3_wrapper.filter.pipe_filter import IntegrationFilterPreset, PipeFilter
from vmk_spectrum3_wrapper.storage.base_storage import BaseStorage
from vmk_spectrum3_wrapper.typing import Array
from vmk_spectrum3_wrapper.units import Units


class BufferStorage(BaseStorage):

    def __init__(self, filter: PipeFilter | None = None) -> None:
        if isinstance(filter, PipeFilter):
            assert any(isinstance(h, BufferFilter) for h in filter), 'PipeFilter should contains one BufferFilter at least!'

        #
        super().__init__(filter=filter or IntegrationFilterPreset())

        self._buffer = []

    @property
    def buffer(self) -> list[Array[int]]:
        return self._buffer

    @property
    def buffer_size(self) -> int:
        if isinstance(self.capacity, int):
            return self.capacity
        if isinstance(self.capacity, Sequence):
            return sum(self.capacity)

    # --------        filters        --------
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
        if len(self.buffer) == self.buffer_size:  # если буфер заполнен, то ранные обрабатываются `filter`, передаются в `data` и буфер очищается
            buffer = np.array(self.buffer)

            datum = Datum(
                intensity=buffer,
                units=Units.digit,
                meta=Meta(
                    capacity=self._capacity,
                    exposure=self._exposure,
                    started_at=None,
                    finished_at=time_at,
                ),
            )
            datum = self.filter(datum)
            self.data.append(datum)

            #
            self.buffer.clear()

    def clear(self) -> None:
        """Clear buffer and data."""
        self.buffer.clear()
        self.data.clear()
