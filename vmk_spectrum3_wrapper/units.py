from enum import Enum
from typing import TypeVar

from vmk_spectrum3_wrapper.typing import Electron, T




class Units(Enum):
    """Device's output signal units."""
    digit = 'digit'
    percent = 'percent'
    electron = 'electron'


def get_clipping(units: Units) -> T:
    """Get unit's clipping value (max value)."""

    match units:
        case Units.digit:
            adc = 16
            return 2**adc - 1
        case Units.percent:
            return 100
        case Units.electron:
            raise NotImplementedError

    raise TypeError(f'Units {units} is not supported yet!')


def get_scale(units: Units) -> float:
    """Get unit's scale coefficient."""

    return get_clipping(units) / get_clipping(Units.digit)


def get_label(units: Units, is_enclosed: bool = True) -> str:
    """Get units's label."""

    match units:
        case Units.digit:
            label = r''
        case Units.percent:
            label = r'%'
        case Units.electron:
            label = r'$e^{-}$'
        case _:
            raise TypeError(f'Units {units} is not supported yet!')

    #
    if is_enclosed:
        return f'[{label}]'

    return label


# --------        handlers        --------
def to_electron(value: T, units: Units, capacity: Electron) -> Electron:
    """Convert value to electron units."""

    match units:
        case Units.digit:
            adc = 16
            return capacity * (value/(2**adc - 1))
        case Units.percent:
            return capacity * (value/100)
        case Units.electron:
            return value

    raise TypeError(f'Units {units} is not supported yet!')
