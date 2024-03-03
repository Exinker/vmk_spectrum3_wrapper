from abc import ABC, abstractmethod

from vmk_spectrum3_wrapper.typing import Array, T


class BaseHandler(ABC):

    # --------        private        --------
    def __bool__(self) -> bool:
        return True

    @abstractmethod
    def __call__(self, data: Array[T], *args, **kwargs) -> Array[T]:
        raise NotImplementedError
