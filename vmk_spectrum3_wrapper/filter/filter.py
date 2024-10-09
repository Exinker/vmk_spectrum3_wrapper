from abc import ABC, abstractmethod

from vmk_spectrum3_wrapper.types import Array, U


class AbstractFilter(ABC):
    """Абстрактный базовый класс фильтров обработки данных."""

    # --------        private        --------
    def __bool__(self) -> bool:
        return True

    @abstractmethod
    def __call__(self, data: Array[U], *args, **kwargs) -> Array[U]:
        raise NotImplementedError
