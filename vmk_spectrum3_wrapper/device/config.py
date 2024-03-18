import itertools
from collections.abc import Sequence
from dataclasses import dataclass, field
from enum import Enum
from typing import Iterator, TypeAlias

import numpy as np

from vmk_spectrum3_wrapper.adc import ADC
from vmk_spectrum3_wrapper.typing import IP, MicroSecond, MilliSecond


CHANGE_EXPOSURE_DELAY = 1000
ADC_RESOLUTION = ADC._16BIT.config.resolution


# --------        device config        --------
@dataclass
class DeviceConfigAuto:
    change_exposure_delay: MilliSecond = field(default=CHANGE_EXPOSURE_DELAY)


@dataclass
class DeviceConfigEthernet:
    ip: IP | Sequence[IP]
    change_exposure_delay: MilliSecond = field(default=CHANGE_EXPOSURE_DELAY)


DeviceConfig: TypeAlias = DeviceConfigAuto | DeviceConfigEthernet


# --------        read config        --------
def to_microsecond(__exposure: MilliSecond) -> MicroSecond:
    value = int(np.round(1000 * __exposure).astype(int))

    assert value % 100 == 0, 'Invalid exposure: {value} mks!'.format(
        value=value,
    )

    return value


class ReadMode(Enum):
    standart = 'standart'
    extended = 'extended'


class ReadConfig:

    def __init__(self, exposure: MilliSecond | tuple[MilliSecond, MilliSecond], capacity: int | tuple[int, int]):
        self._exposure = exposure
        self._capacity = capacity

        self._mode = {
            int: ReadMode.standart,
            float: ReadMode.standart,
            tuple:  ReadMode.extended,
        }[type(exposure)]

        #
        if self.mode == ReadMode.extended:
            assert len(self.exposure) == len(self.capacity)

    @property
    def exposure(self) -> MilliSecond | tuple[MilliSecond, MilliSecond]:
        return self._exposure

    @property
    def capacity(self) -> int | tuple[int, int]:
        return self._capacity

    @property
    def mode(self) -> ReadMode:
        return self._mode

    @property
    def duration(self) -> MilliSecond:

        if self.mode == ReadMode.standart:
            return self.exposure * self.capacity
        if self.mode == ReadMode.extended:
            return sum(
                exposure*capacity
                for exposure, capacity in zip(self.exposure, self.capacity)
            )

        raise ValueError(f'Mode {self.mode} is not supported yet!')

    @property
    def n_frames(self) -> int:

        if self.mode == ReadMode.standart:
            return self.capacity
        if self.mode == ReadMode.extended:
            return sum(self.capacity)

        raise ValueError(f'Mode {self.mode} is not supported yet!')

    # --------        private        --------
    def __iter__(self) -> Iterator:

        if self.mode == ReadMode.standart:
            return iter([
                to_microsecond(self.exposure),
            ])

        if self.mode == ReadMode.extended:
            return itertools.chain(*[
                (to_microsecond(exposure), capacity)
                for exposure, capacity in zip(reversed(self.exposure), reversed(self.capacity))  # TODO: reverse items for compatibility with Atom
            ])

        raise TypeError()

    def __repr__(self) -> str:
        cls = self.__class__

        return f'{cls.__name__}({self})'

    def __str__(self) -> str:

        if self.mode == ReadMode.standart:
            return f'{self.exposure}'

        if self.mode == ReadMode.extended:
            return '; '.join([
                f'({exposure}, {capacity})'
                for exposure, capacity in zip(self.exposure, self.capacity)
            ])

        raise TypeError()
