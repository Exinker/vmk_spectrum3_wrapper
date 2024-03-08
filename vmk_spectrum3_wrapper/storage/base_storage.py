from abc import ABC, abstractmethod

from vmk_spectrum3_wrapper.data import Datum
from vmk_spectrum3_wrapper.exception import SetupStorageError
from vmk_spectrum3_wrapper.handler import PipeHandler
from vmk_spectrum3_wrapper.typing import MilliSecond, Second
from vmk_spectrum3_wrapper.units import Units


class BaseStorage(ABC):

    def __init__(self, handler: PipeHandler):
        self._handler = handler

        self._exposure = None
        self._capacity = None
        self._started_at = None  # время окончания измерения первого кадра
        self._finished_at = None  # время окончания измерения последнего кадра
        self._data = []

    @property
    def exposure(self) -> MilliSecond | tuple[MilliSecond, MilliSecond]:
        if self._exposure is None:
            raise SetupStorageError('Setup a storage before!')

        return self._exposure

    @property
    def capacity(self) -> int | tuple[int, int]:
        """"Required `n_frames` to iteration."""
        if self._capacity is None:
            raise SetupStorageError('Setup a storage before!')

        return self._capacity

    @property
    def handler(self) -> PipeHandler:
        return self._handler

    @property
    def data(self) -> list[Datum]:
        return self._data

    @property
    def units(self) -> Units:
        return self.handler.units

    @property
    def duration(self) -> Second:
        """Время измерения (от окончания измерения первого до окончания измерения последнего кадра!)."""
        if self._started_at is None:
            return 0

        return self._finished_at - self._started_at

    # --------        handlers        --------
    def setup(self, exposure: MilliSecond | tuple[MilliSecond, MilliSecond], capacity: int | tuple[int, int]) -> None:
        self._exposure = exposure
        self._capacity = capacity

    def pull(self, clear: bool = True) -> list[Datum]:
        """Pull data from storage."""

        try:
            return self.data.copy()

        finally:
            if clear:
                self.clear()

    @abstractmethod
    def put(self, frame: Datum) -> None:
        """Add the frame to storage."""
        raise NotImplementedError

    @abstractmethod
    def clear(self) -> None:
        """Clear storage."""
        raise NotImplementedError

    # --------        private        --------
    def __bool__(self) -> bool:
        return True

    def __len__(self) -> int:
        return len(self.data)

    def __repr__(self) -> str:
        cls = self.__class__

        return f'{cls.__name__}(units: {self.units.value})'
