from abc import ABC, abstractmethod

from vmk_spectrum3_wrapper.types import Array, U


class FilterABC(ABC):
    """Абстрактный базовый класс фильтров обработки данных."""

    def __bool__(self) -> bool:
        return True

    @abstractmethod
    def __call__(self, datum: Array[U], *args, **kwargs) -> Array[U]:
        raise NotImplementedError
