from enum import Enum

from vmk_spectrum3_wrapper.config import _ADC
from vmk_spectrum3_wrapper.types import Electron, U


class Units(Enum):
    """Device's output signal units."""
    digit = 'digit'
    percent = 'percent'
    electron = 'electron'

    @property
    def value_max(self) -> U:
        """Get unit's max value (clipped value)."""

        if self == Units.digit:
            return _ADC.value_max
        if self == Units.percent:
            return 100
        if self == Units.electron:
            raise TypeError(f'Units {self} is not supported yet!')

        raise TypeError(f'Units {self} is not supported yet!')

    @property
    def scale(self) -> float:
        """Unit's scale to coefficient."""

        return self.value_max / Units.digit.value_max

    @property
    def label(self) -> str:
        """Units's label."""

        return self.get_label(is_enclosed=True)

    def get_label(self, is_enclosed: bool = False) -> str:
        """Get units's label."""
        label = self._get_label()

        if is_enclosed:
            return r'${label}$'.format(
                label=label,
            )
        return label

    def _get_label(self) -> str:

        if self == Units.digit:
            return r''
        if self == Units.percent:
            return r'\%'
        if self == Units.electron:
            return r'e^{-}'

        raise TypeError(f'Units {self} is not supported yet!')


def to_electron(value: U, units: Units, capacity: Electron) -> Electron:
    """Convert value to electron units."""

    if units == Units.digit:
        return capacity * (value/units.value_max)
    if units == Units.percent:
        return capacity * (value/units.value_max)
    if units == Units.electron:
        return value

    raise TypeError(f'Units {units} is not supported yet!')
