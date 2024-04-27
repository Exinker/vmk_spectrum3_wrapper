import time
from typing import overload

from vmk_spectrum3_wrapper.data import Data
from vmk_spectrum3_wrapper.filter import F
from vmk_spectrum3_wrapper.typing import Array, MilliSecond

from .schema import Schema, fetch_schema
from .storage import Storage


class Measurement:

    def __init__(self, n_times: int, schema: Schema, storage: Storage):
        self._n_times = n_times
        self._schema = schema
        self._storage = storage

        self._started_at = None
        self._finished_at = None

    @property
    def n_times(self) -> int | None:
        return self._n_times

    @property
    def schema(self) -> Schema:
        return self._schema

    @property
    def storage(self) -> Storage:
        return self._storage

    @property
    def progress(self) -> float | None:
        if self.n_times is None:
            return None

        return len(self.storage) / self.n_times

    @property
    def capacity_total(self) -> int:
        """Полное количество кадров."""
        if self.n_times is None:
            return None

        return self.n_times * self.schema.capacity_total

    @property
    def duration_total(self) -> MilliSecond | None:
        """Полное время измерения."""
        if self.n_times is None:
            return None

        return self.n_times * self.schema.duration_total

    def put(self, frame: Array[int]) -> None:
        """Добавить новый `frame` в `storage`."""

        # time
        time_at = time.perf_counter()

        if self._started_at is None:
            self._started_at = time_at

        self._finished_at = time_at

        #
        self.storage.put(frame)

    def pull(self) -> Data:
        """Забрать все `data` из `storage`."""
        if self.progress < 1:
            raise ValueError  # TODO: add custom exception!

        #
        return Data.squeeze(self.storage.pull())


# --------        factory        --------
@overload
def fetch_measurement(n_times: int, exposure: MilliSecond, capacity: int, handler: F | None = None) -> Measurement: ...
@overload
def fetch_measurement(n_times: int, exposure: tuple[MilliSecond, MilliSecond], capacity: tuple[int, int], handler: F | None = None) -> Measurement: ...
def fetch_measurement(n_times, exposure, capacity, handler):
    return Measurement(
        n_times=n_times,
        schema=fetch_schema(exposure, capacity),
        storage=Storage(exposure, capacity, handler),
    )
