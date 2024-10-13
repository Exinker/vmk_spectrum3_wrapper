
from vmk_spectrum3_wrapper.data import Data, Meta, Datum
from vmk_spectrum3_wrapper.device.device_config import DeviceConfig, DeviceConfigAuto, DeviceConfigManual
from vmk_spectrum3_wrapper.exception import ConnectionDeviceError, DeviceError, SetupDeviceError, StatusDeviceError, eprint
from vmk_spectrum3_wrapper.filters import F
from vmk_spectrum3_wrapper.measurement import Measurement, StandardSchema
from vmk_spectrum3_wrapper.types import Array, Digit, IP, MilliSecond
from vmk_spectrum3_wrapper.units import Units


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

        return self

    def read(self) -> Data:
        assert isinstance(self._measurement.schema, StandardSchema)

        schema = self._measurement.schema
        tau = schema.exposure
        capacity = schema.capacity

        n_numbers = 4096
        units = Units.percent
        intensity = np.random.randn(capacity, n_numbers)

        datum = Datum(
            units=units,
            intensity=intensity,
            clipped=intensity >= units.value_max,
            deviation=None,
        )







