from enum import Enum

from vmk_spectrum3_wrapper.device.config import _ADC
from vmk_spectrum3_wrapper.typing import Electron, U


class Units(Enum):
    """Device's output signal units."""
    digit = 'digit'
    percent = 'percent'
    electron = 'electron'

    @property
    def value_max(self) -> U:
        """Get unit's max value (clipped value)."""

        match self:
            case Units.digit:
                return _ADC.value_max
            case Units.percent:
                return 100
            case Units.electron:
                raise TypeError(f'Units {self} is not supported yet!')
            case _:
                raise TypeError(f'Units {self} is not supported yet!')

    @property
    def scale(self) -> float:
        """Unit's scale to coefficient."""

        return self.value_max / Units.digit.value_max

    @property
    def label(self, is_enclosed: bool = True) -> str:
        """Units's label."""

        match self:
            case Units.digit:
                return r''
            case Units.percent:
                return r'%'
            case Units.electron:
                return r'$e^{-}$'
            case _:
                raise TypeError(f'Units {self} is not supported yet!')


# --------        handlers        --------
def to_electron(value: U, units: Units, capacity: Electron) -> Electron:
    """Convert value to electron units."""

    match units:
        case Units.digit:
            return capacity * (value/units.value_max)
        case Units.percent:
            return capacity * (value/units.value_max)
        case Units.electron:
            return value

    raise TypeError(f'Units {units} is not supported yet!')
