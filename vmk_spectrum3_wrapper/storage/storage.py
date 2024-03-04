import time

import numpy as np

from vmk_spectrum3_wrapper.data import Data, Meta
from vmk_spectrum3_wrapper.device import ADC_RESOLUTION
from vmk_spectrum3_wrapper.handler import PipeHandler
from vmk_spectrum3_wrapper.storage.base_storage import BaseStorage
from vmk_spectrum3_wrapper.typing import Array, Digit
from vmk_spectrum3_wrapper.units import Units


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
        intensity = np.array(frame)
        mask = intensity == (2**ADC_RESOLUTION - 1)

        datum = Data(
            intensity=intensity,
            mask=mask,
            units=Units.digit,
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
