from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import TypeAlias

from vmk_spectrum3_wrapper.config import CHANGE_EXPOSURE_TIMEOUT
from vmk_spectrum3_wrapper.types import IP, MilliSecond


@dataclass
class DeviceConfigAuto:
    change_exposure_timeout: MilliSecond = field(default=CHANGE_EXPOSURE_TIMEOUT)


@dataclass
class DeviceConfigManual:
    ip: Sequence[IP]
    change_exposure_timeout: MilliSecond = field(default=CHANGE_EXPOSURE_TIMEOUT)


DeviceConfig: TypeAlias = DeviceConfigAuto | DeviceConfigManual
