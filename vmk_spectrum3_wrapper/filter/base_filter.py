from abc import ABC, abstractmethod
from typing import Any

from vmk_spectrum3_wrapper.typing import Array, U


class BaseFilter(ABC):

    # @abstractmethod
    # def kernel(self, value: Array[U] | None) -> Array[Any] | None:
    #     raise NotImplementedError

    # --------        private        --------
    def __bool__(self) -> bool:
        return True

    @abstractmethod
    def __call__(self, data: Array[U], *args, **kwargs) -> Array[U]:
        raise NotImplementedError
