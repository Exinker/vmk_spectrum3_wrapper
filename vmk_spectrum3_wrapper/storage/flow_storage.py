import time

from vmk_spectrum3_wrapper.data import Datum, Meta
from vmk_spectrum3_wrapper.filter.pipe_filter import PipeFilter, CoreFilterPreset
from vmk_spectrum3_wrapper.storage.base_storage import BaseStorage
from vmk_spectrum3_wrapper.typing import Array, Digit
from vmk_spectrum3_wrapper.units import Units


class FlowStorage(BaseStorage):

    def __init__(self, filter: PipeFilter | None = None) -> None:
        super().__init__(filter=filter or CoreFilterPreset())

    # --------        filters        --------
    def put(self, frame: Array[Digit]) -> None:
        """Add the frame to storage."""

        # time
        time_at = time.perf_counter()

        if self._started_at is None:
            self._started_at = time_at

        self._finished_at = time_at

        # data
        datum = Datum(
            intensity=frame,
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

    def clear(self) -> None:
        """Clear storage."""
        self.data.clear()
