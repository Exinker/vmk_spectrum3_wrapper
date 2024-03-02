from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import TypeAlias

from vmk_spectrum3_wrapper.typing import IP, MilliSecond


CHANGE_EXPOSURE_DELAY = 1000


@dataclass
class DeviceConfigAuto:
    change_exposure_delay: MilliSecond = field(default=CHANGE_EXPOSURE_DELAY)


@dataclass
class DeviceConfigEthernet:
    ip: IP | Sequence[IP]
    change_exposure_delay: MilliSecond = field(default=CHANGE_EXPOSURE_DELAY)


DeviceConfig: TypeAlias = DeviceConfigAuto | DeviceConfigEthernet
