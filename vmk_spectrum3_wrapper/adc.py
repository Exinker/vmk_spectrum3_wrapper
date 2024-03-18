"""
Analog-to-digital converter (ADC).

Author: Vaschenko Pavel
 Email: vaschenko@vmk.ru
  Date: 2024.03.18
"""
from dataclasses import dataclass
from enum import Enum


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

    _16BIT = ADCConfig(
        resolution=16,
        log=False,
    )
    _18BIT = ADCConfig(
        resolution=18,
        log=False,
    )
