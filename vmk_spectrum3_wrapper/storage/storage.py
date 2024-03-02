import time

import numpy as np

from vmk_spectrum3_wrapper.typing import Array, Digit, Second
from vmk_spectrum3_wrapper.units import Units, get_scale
from vmk_spectrum3_wrapper.handler import Handler, PipeHandler, ScaleHandler


class Storage:

    def __init__(self, handler: Handler | None = None) -> None:

        self._started_at = None  # время начала измерения первого кадра
        self._finished_at = None  # время начала измерения последнего кадра
        self._data = []

        self._handler = handler or ScaleHandler(units=Units.percent)

    @property
    def duration(self) -> Second:
        """Время с начала измерения (от начала измерения первого до начала измерения последнего кадра!)."""
        if self._started_at is None:
            return 0

        return self._finished_at - self._started_at

    @property
    def handler(self) -> Handler | None:
        return self._handler

    @property
    def units(self) -> Units:

        if isinstance(self.handler, ScaleHandler):
            return self.handler.units

        if isinstance(self.handler, PipeHandler):
            for h in self.handler:
                if isinstance(h, ScaleHandler):
                    return h.units

        return Units.digit

    # --------        data        --------
    @property
    def data(self) -> list[Array[Digit]]:
        return self._data

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

    def pull(self, clear: bool = True) -> Array[Digit]:
        """Pull data from storage."""

        try:
            return np.array(self.data)

        finally:
            if clear:
                self.clear()

    def clear(self) -> None:
        """Clear storage."""
        self._data.clear()

    # --------        private        --------
    def __len__(self) -> int:
        return len(self._data)

    def __repr__(self) -> str:
        cls = self.__class__

        return f'{cls.__name__}(units: {self.units.value})'
