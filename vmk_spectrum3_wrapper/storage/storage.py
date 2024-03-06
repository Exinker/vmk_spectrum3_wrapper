import time

import numpy as np

from vmk_spectrum3_wrapper.data import Datum, Meta
from vmk_spectrum3_wrapper.device import ADC_RESOLUTION
from vmk_spectrum3_wrapper.handler import PipeHandler
from vmk_spectrum3_wrapper.storage.base_storage import BaseStorage
from vmk_spectrum3_wrapper.typing import Array, Digit, MilliSecond
from vmk_spectrum3_wrapper.units import Units


class Storage(BaseStorage):

    def __init__(self, handler: PipeHandler) -> None:
        super().__init__(handler=handler)

    # --------        handlers        --------
    def put(self, frame: Array[Digit]) -> None:
        """Add the frame to storage."""

        # time
        time_at = time.perf_counter()

        if self._started_at is None:
            self._started_at = time_at

        self._finished_at = time_at

        # data
        intensity = np.array(frame)
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

        self._data.append(datum)

    def clear(self) -> None:
        """Clear storage."""
        self._data.clear()
