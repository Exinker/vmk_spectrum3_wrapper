import itertools
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Iterator, TypeAlias

import numpy as np

from vmk_spectrum3_wrapper.typing import IP, MicroSecond, MilliSecond


CHANGE_EXPOSURE_DELAY = 1000


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


class ReadConfig:

    def __init__(self, exposure: MilliSecond | tuple[MilliSecond, MilliSecond], capacity: int | tuple[int, int]):
        self._exposure = exposure
        self._capacity = capacity

    @property
    def exposure(self) -> MilliSecond | tuple[MilliSecond, MilliSecond]:
        return self._exposure

    @property
    def capacity(self) -> int | tuple[int, int]:
        return self._capacity

    # --------        private        --------
    def __iter__(self) -> Iterator:

        if isinstance(self.exposure, float):
            return iter([self.exposure])

        if isinstance(self.exposure, tuple):
            return itertools.chain(*[
                (to_microsecond(exposure), capacity)
                for exposure, capacity in zip(self.exposure, self.capacity)
            ])

        raise TypeError()

    def __str__(self) -> str:
        cls = self.__class__

        if isinstance(self.exposure, float):
            content = f'{self.exposure}'
            return f'{cls.__name__}({content})'

        if isinstance(self.exposure, tuple):
            content = '; '.join([
                f'({exposure}, {capacity})'
                for exposure, capacity in zip(self.exposure, self.capacity)
            ])
            return f'{cls.__name__}({content})'

        raise TypeError()
