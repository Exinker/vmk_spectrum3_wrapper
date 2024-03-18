"""
Analog-to-digital converter (ADC).

Author: Vaschenko Pavel
 Email: vaschenko@vmk.ru
  Date: 2024.03.18
"""
from dataclasses import dataclass
from enum import Enum

from vmk_spectrum3_wrapper.typing import Digit


@dataclass(frozen=True)
class ADCConfig:
    """ADC's config."""
    resolution: int
    log: bool

    # --------        private        --------
    def __str__(self) -> str:
        cls = self.__class__
        resolution = self.resolution

        return f'{cls.__name__}: {resolution}'


class ADC(Enum):
    """Enums with detectors."""

    _16bit = ADCConfig(
        resolution=16,
        log=False,
    )
    _18bit = ADCConfig(
        resolution=18,
        log=False,
    )

    @property
    def config(self) -> ADCConfig:
        """Config of the ADC."""
        return self.value

    @property
    def value_max(self) -> Digit:
        return 2**self.config.resolution - 1
