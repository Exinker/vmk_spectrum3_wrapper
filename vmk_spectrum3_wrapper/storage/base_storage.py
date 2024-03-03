from abc import ABC, abstractmethod

from vmk_spectrum3_wrapper.handler import PipeHandler
from vmk_spectrum3_wrapper.typing import Array, T


class BaseStorage(ABC):

    def __init__(self, handler: PipeHandler | None = None):
        self._handler = handler or PipeHandler()

        self._started_at = None  # время начала измерения первого кадра
        self._finished_at = None  # время начала измерения последнего кадра
        self._data = []

    @property
    def duration(self) -> Second:
        """Время с начала измерения (от начала измерения первого до начала измерения последнего кадра!)."""
        if self._started_at is None:
            return 0

        return self._finished_at - self._started_at

    @property
    def handler(self) -> PipeHandler | None:
        return self._handler

    @property
    def data(self) -> list[Array[Digit]]:
        return self._data

    def pull(self, clear: bool = True) -> Array[Digit]:
        """Pull data from storage."""

        try:
            return np.array(self.data)

        finally:
            if clear:
                self.clear()

    @abstractmethod
    def put(self, frame: Array[Digit]) -> None:
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
