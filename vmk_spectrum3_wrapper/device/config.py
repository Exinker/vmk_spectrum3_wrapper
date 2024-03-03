from abc import ABC, abstractmethod, abstractproperty
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
class BaseReadConfig(ABC):

    # @abstractproperty
    # def total_duration(self) -> MilliSecond:
    #     raise NotImplementedError

    @abstractproperty
    def total_counts(self) -> int:
        raise NotImplementedError

    @staticmethod
    def to_microsecond(__exposure: MilliSecond) -> MicroSecond:
        value = int(np.round(1000 * __exposure).astype(int))

        assert value % 100 == 0, 'Invalid exposure: {value} mks!'.format(
            value=value,
        )

        return value

    # --------        private        --------
    @abstractmethod
    def __iter__(self) -> Iterator:
        raise NotImplementedError

    @abstractmethod
    def __str__(self) -> str:
        raise NotImplementedError


class StandardReadConfig(BaseReadConfig):

    def __init__(self, exposure: MilliSecond):
        self.exposure = exposure

    @property
    def total_counts(self) -> int:
        return 1

    # --------        private        --------
    def __iter__(self) -> Iterator:
        return iter([
            self.to_microsecond(self.exposure),
        ])

    def __str__(self) -> str:
        cls = self.__class__

        content = f'{self.exposure}'
        return f'{cls.__name__}({content})'


class ExtendedReadConfig(BaseReadConfig):

    def __init__(self, exposure: tuple[MilliSecond, MilliSecond]):
        self.exposure = exposure

    @property
    def total_counts(self) -> int:
        return sum(self.n_frames)

    # --------        private        --------
    def __iter__(self) -> Iterator:
        return iter(list(map(self.to_microsecond, self.exposure)))

    def __str__(self) -> str:
        cls = self.__class__

        content = '; '.join([
            f'({exposure}, {n_frames})'
            for exposure, n_frames in zip(self.exposure, self.n_frames)
        ])
        return f'{cls.__name__}({content})'


ReadConfig: TypeAlias = StandardReadConfig | ExtendedReadConfig
