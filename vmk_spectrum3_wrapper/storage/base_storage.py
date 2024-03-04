from abc import ABC, abstractmethod, abstractproperty

from vmk_spectrum3_wrapper.data import Data
from vmk_spectrum3_wrapper.handler import PipeHandler
from vmk_spectrum3_wrapper.typing import Second
from vmk_spectrum3_wrapper.units import Units


class BaseStorage(ABC):

    def __init__(self, handler: PipeHandler | None = None):
        self._handler = handler or PipeHandler()

        self._started_at = None  # время окончания измерения первого кадра
        self._finished_at = None  # время окончания измерения последнего кадра
        self._data = []

    @property
    def duration(self) -> Second:
        """Время измерения (от окончания измерения первого до окончания измерения последнего кадра!)."""
        if self._started_at is None:
            return 0

        return self._finished_at - self._started_at

    @property
    def handler(self) -> PipeHandler:
        return self._handler

    @property
    def data(self) -> list[Data]:
        return self._data

    @property
    def units(self) -> Units:
        return self.handler.units

    def pull(self, clear: bool = True) -> Data:
        """Pull data from storage."""

        try:
            return self.data.copy()

        finally:
            if clear:
                self.clear()

    @abstractproperty
    def capacity(self) -> int:
        """"Required `n_frames` to iteration."""
        raise NotImplementedError

    @abstractmethod
    def put(self, frame: Data) -> None:
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
        return len(self._data)

    def __repr__(self) -> str:
        cls = self.__class__

        return f'{cls.__name__}(units: {self.units.value})'
