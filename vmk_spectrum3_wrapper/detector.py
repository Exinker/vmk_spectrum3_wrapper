from dataclasses import dataclass, field
from enum import Enum

from vmk_spectrum3_wrapper.typing import Electron, MicroMeter


@dataclass(frozen=True)
class DetectorConfig:
    """Detector's confg."""
    name: str
    capacity: Electron
    read_noise: Electron
    n_pixels: int
    width: MicroMeter
    height: MicroMeter
    description: str = field(default='')

    # --------        private        --------
    def __str__(self) -> str:
        cls = self.__class__
        name = self.name

        return f'{cls.__name__}: {name}'


class Detector(Enum):
    """Enums with detectors."""

    BLPP2000 = DetectorConfig(
        name='БЛПП-2000',
        capacity=200_000,
        read_noise=25,
        n_pixels=2048,
        width=14,
        height=1000,
    )
    BLPP4000 = DetectorConfig(
        name='БЛПП-4000',
        capacity=80_000,
        read_noise=16,
        n_pixels=4096,
        width=7,
        height=200,
    )
    BLPP4100 = DetectorConfig(
        name='БЛПП-4100',
        capacity=100_000,
        read_noise=20,
        n_pixels=4096,
        width=7,
        height=1000,
    )

    @property
    def config(self) -> DetectorConfig:
        """Config of the detector."""
        return self.value

    @property
    def pitch(self) -> MicroMeter:
        """Pitch structure of the detector."""
        return self.config.width

    # --------        private        --------
    def __str__(self) -> str:
        cls = self.__class__
        name = self.config.name

        return f'{cls.__name__}: {name}'
