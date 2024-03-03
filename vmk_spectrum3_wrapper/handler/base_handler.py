from abc import ABC, abstractmethod

from vmk_spectrum3_wrapper.typing import Array, T


class BaseHandler(ABC):

    # --------        private        --------
    @abstractmethod
    def __call__(self, data: Array[T], *args, **kwargs) -> Array[T]:
        raise NotImplementedError