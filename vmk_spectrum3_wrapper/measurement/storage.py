import time
from collections.abc import Sequence

import numpy as np

from vmk_spectrum3_wrapper.data import Datum
from vmk_spectrum3_wrapper.exception import SetupStorageError
from vmk_spectrum3_wrapper.filter import IntegrationFilterPreset, PipeFilter
from vmk_spectrum3_wrapper.typing import Array, MilliSecond, Second
from vmk_spectrum3_wrapper.units import Units


class Storage:

    def __init__(self, capacity: int | tuple[int, int], handler: PipeFilter | None = None):
        self._capacity = capacity
        self._handler = handler or IntegrationFilterPreset()

        self._started_at = None  # время окончания измерения первого кадра
        self._finished_at = None  # время окончания измерения последнего кадра

        self._data = []
        self._buffer = []

    @property
    def capacity(self) -> int | tuple[int, int]:
        """"Количество кадров для проведения измерения."""
        return self._capacity

    @property
    def handler(self) -> PipeFilter:
        return self._handler

    @property
    def buffer(self) -> list[Array[int]]:
        return self._buffer

    @property
    def buffer_size(self) -> int:
        if isinstance(self.capacity, int):
            return self.capacity
        if isinstance(self.capacity, Sequence):
            return sum(self.capacity)

    @property
    def data(self) -> list[Datum]:
        return self._data

    @property
    def duration(self) -> Second:
        """Время измерения (от окончания измерения первого до окончания измерения последнего кадра!)."""
        if self._started_at is None:
            return 0

        return self._finished_at - self._started_at

    # --------        handler        --------
    def pull(self, clear: bool = True) -> list[Datum]:
        """Pull data from storage."""

        try:
            return self.data.copy()

        finally:
            self.buffer.clear()
            self.data.clear()

    def put(self, frame: Array[int]) -> None:
        """Добавить новый кадр `frame` в буфер."""

        # time
        time_at = time.perf_counter()

        if self._started_at is None:
            self._started_at = time_at

        self._finished_at = time_at

        # buffer
        print('+2')
        self.buffer.append(frame)

        # data
        if len(self.buffer) == self.buffer_size:  # если буфер заполнен, то ранные обрабатываются `handler`, передаются в `data` и буфер очищается
            buffer = np.array(self.buffer)

            datum = Datum(
                intensity=buffer,
                units=Units.digit,
            )
            datum = self.handler(datum)

            self.data.append(datum)

            #
            self.buffer.clear()

    # --------        private        --------
    def __bool__(self) -> bool:
        return True

    def __len__(self) -> int:
        return len(self.data)

    def __repr__(self) -> str:
        cls = self.__class__

        return f'{cls.__name__}(handler: {self.handler})'
