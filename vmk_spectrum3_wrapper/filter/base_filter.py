from abc import ABC, abstractmethod

from vmk_spectrum3_wrapper.typing import Array, U


class BaseFilter(ABC):

    # --------        private        --------
    def __bool__(self) -> bool:
        return True

    @abstractmethod
    def __call__(self, data: Array[U], *args, **kwargs) -> Array[U]:
        raise NotImplementedError
