from abc import ABC

from typing import TypeAlias

from vmk_spectrum3_wrapper.typing import T
from vmk_spectrum3_wrapper.units import Units


class BaseData(ABC):
    
    def __init__(self, __data: Array[T], units: Units):
        self._data = __data
        self._units = units

    @property
    def data(self) -> Attay[T]:
        return self._data

    @property
    def units(self) -> Units:
        return self._units

    # --------        private        --------
    def __mul__(self, other: float):
        cls = self.__class__

        if isinstance(other, float):
            return cls(self.data * other, units=self.units)

        raise TypeError(f'Type {type(other)} is not supported yet!')

    def __imul__(self, other: float):
        return self * other

    def __rmul__(self, other: float):
        return self * other


class EmissionData(BaseData):
    
    def __init__(self, __data: Array[T], units: Units):
        super().__init__(__data, units=units)


Data: TypeAlias = EmissionData
