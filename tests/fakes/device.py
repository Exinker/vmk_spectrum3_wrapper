

from vmk_spectrum3_wrapper.data import Data, DataMeta
from vmk_spectrum3_wrapper.device.config import DeviceConfig, DeviceConfigAuto, DeviceConfigManual
from vmk_spectrum3_wrapper.exception import ConnectionDeviceError, DeviceError, SetupDeviceError, StatusDeviceError, eprint
from vmk_spectrum3_wrapper.filter import F
from vmk_spectrum3_wrapper.measurement import Measurement
from vmk_spectrum3_wrapper.types import Array, Digit, IP, MilliSecond


class FakeDeviceConfig:
    pass


class FakeDevice:

    def __init__(
        self,
        config: FakeDeviceConfig | None = None,
        verbose: bool = False,
    ) -> None:

        self._config = config or FakeDeviceConfig()
        self._status = None
        self._is_connected = False

        self.verbose = verbose

    def connect(self) -> 'FakeDevice':
        self._is_connected = True

    def disconnect(self) -> 'FakeDevice':
        self._is_connected = False

    def setup(
        self,
        n_times: int,
        exposure: MilliSecond | tuple[MilliSecond, MilliSecond],
        capacity: int | tuple[int, int] = 1,
        handler: F | None = None,
    ) -> 'FakeDevice':

        self._measurement = Measurement.create(
            n_times=n_times,
            exposure=exposure,
            capacity=capacity,
            handler=handler,
        )









