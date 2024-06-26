import threading
import time
from collections.abc import Sequence
from typing import Mapping

import pyspectrum3 as ps3

from vmk_spectrum3_wrapper.data import Data, DataMeta
from vmk_spectrum3_wrapper.device.config import DeviceConfig, DeviceConfigAuto
from vmk_spectrum3_wrapper.exception import ConnectionDeviceError, DeviceError, SetupDeviceError, StatusDeviceError, eprint
from vmk_spectrum3_wrapper.filter import F
from vmk_spectrum3_wrapper.measurement.measurement import fetch_measurement
from vmk_spectrum3_wrapper.measurement.schema import ExtendedSchema, StandardSchema
from vmk_spectrum3_wrapper.typing import Array, IP, MilliSecond


def _create_device(config: DeviceConfig) -> 'Device':
    """Create device by config and initialize."""
    device = ps3.DeviceManager()

    if isinstance(config, DeviceConfigAuto):
        device.initialize(
            ps3.AutoConfig().config(),
        )
        return device

    raise ValueError(f'Device {type(config).__name__} is not supported yet!')


class Device:

    def __init__(self, config: DeviceConfig | None = None, verbose: bool = False) -> None:

        # config
        self._device_config = config or DeviceConfigAuto()
        self._read_config = None

        # device
        device = _create_device(self._device_config)
        device.set_frame_callback(self._on_frame)
        device.set_status_callback(self._on_status)
        device.set_error_callback(self._on_error)

        self._device = device
        self._status = None
        self._is_connected = False

        # storage
        self._storage = None

        #
        self.condition = threading.Condition(lock=None)
        self.verbose = verbose

    @property
    def device(self) -> 'Device':
        return self._device

    @property
    def status(self) -> Mapping[IP, ps3.AssemblyStatus] | None:
        return self._status

    # --------        handler        --------
    def connect(self) -> 'Device':
        """Connect to device."""
        message = 'Device is not ready to connect!'

        # pass checks
        try:
            self._check_connection(state=False)

        except DeviceError as error:
            eprint(message=message, error=error)
            return self

        # connect
        try:
            self.device.connect()

        except ps3.DriverException as error:
            eprint(message=message, error=error)

        else:
            self._is_connected = True

        return self

    def disconnect(self) -> 'Device':
        """Disconnect from device."""
        message = 'Device is not ready to disconnect!'

        # pass checks
        try:
            self._check_connection(state=True)

        except DeviceError as error:
            eprint(message=message, error=error)
            return self

        # disconnect
        try:
            self.device.disconnect()

        except ps3.DriverException as error:
            eprint(message=message, error=error)

        else:
            self._is_connected = False

        return self

    def setup(self, exposure: MilliSecond | tuple[MilliSecond, MilliSecond], capacity: int | tuple[int, int] = 1, handler: F | None = None) -> 'Device':
        """Setup device to read."""
        message = 'Device is not ready to setup!'

        self._measurement = fetch_measurement(
            exposure=exposure,
            capacity=capacity,
            handler=handler,
        )

        # pass checks
        try:
            self._check_connection()
            self._check_status(ps3.AssemblyStatus.ALIVE)

        except DeviceError as error:
            eprint(message=message, error=error)
            return self

        # setup device
        schema = self._measurement.schema

        try:
            if isinstance(schema, StandardSchema):
                self.device.set_exposure(*schema)
            if isinstance(schema, ExtendedSchema):
                self.device.set_double_exposure(*schema)

        except ps3.DriverException as error:
            eprint(message=message, error=error)
            return self

        else:
            self._wait_set_exposure(schema.duration_total)

            if self.verbose:
                message = f'Setup config: {self._read_config}'
                print(message)

        return self

    def read(self, n_iters: int, blocking: bool = True, timeout: MilliSecond = 10) -> Data | None:
        """Прочитать `n_iters` раз и вернуть данные (blocking), или прочитать `n_iters` раз в `storage` (non blocking)."""

        # pass checks
        try:
            self._check_connection()
            self._check_status(ps3.AssemblyStatus.ALIVE)
            self._check_measurement()

        except DeviceError as error:
            eprint(
                message='Device is not ready to read!',
                error=error,
            )
            return None

        # setup measurement
        self._measurement.setup(n_iters)

        # read data
        n_frames = self._measurement.capacity_total

        self.device.read(n_frames)
        self._wait_read()

        # block
        if blocking:
            while self._measurement.progress < 1:
                time.sleep(1e-3*timeout)

            storage = self._measurement.storage

            return Data.squeeze(
                storage.pull(),
                DataMeta(
                    exposure=storage.exposure,
                    capacity=storage.capacity,
                    started_at=storage.started_at,
                    finished_at=storage.finished_at,
                ),
            )

    def is_status(self, __status: ps3.AssemblyStatus | Sequence[ps3.AssemblyStatus]) -> bool:

        if self.status is None:
            return False

        if isinstance(__status, ps3.AssemblyStatus):
            return all(
                status == __status
                for ip, status in self.status.items()
            )

        if isinstance(__status, Sequence):
            return all(
                status in __status
                for ip, status in self.status.items()
            )

        raise StatusDeviceError(f'Status type {type(__status)} is not supported yet!')

    # --------        callbacks        --------
    def _on_frame(self, frame: Array[int]) -> None:
        self._measurement.put(frame)

        # verbose
        if self.verbose:
            print('on_frame:', len(frame), flush=True)

    def _on_status(self, status: Mapping[IP, ps3.AssemblyStatus]) -> None:
        self._status = status

        # notify all
        with self.condition:
            self.condition.notify_all()

        # verbose
        if self.verbose:
            print('on_status:', status, flush=True)

    def _on_error(self, error: ps3.AsyncDriverException) -> None:

        # verbose
        if self.verbose:
            print('on_error:', type(error), error, flush=True)

    # --------        checks        --------
    def _check_connection(self, state: bool = True) -> None:
        if self._is_connected != state:
            raise ConnectionDeviceError({
                True: 'Device have to be connected before!',
                False: 'Device is connected before!',
            }.get(state))

    def _check_status(self, __status: ps3.AssemblyStatus | Sequence[ps3.AssemblyStatus]) -> None:

        if self.status is None:
            raise ConnectionDeviceError('Device is not found! Check the connection!')

        if not self.is_status(__status):
            message = 'Fix assembly before: {ip}!'.format(
                ip=', '.join([
                    ip
                    for ip, status in self.status.items()
                    if status != __status
                ]),
            )
            raise StatusDeviceError(message)

    def _check_measurement(self) -> None:

        if self._measurement is None:
            raise SetupDeviceError('Setup a device before!')

    # --------        private        --------
    def _wait_set_exposure(self, duration: MilliSecond) -> None:
        # FIXME: ждем пока Сергей реализует get_current_mode и get_current_exposure для двойного времени экспозиции
        duration = self._device_config.change_exposure_delay

        time.sleep(1e-3*duration)  # delay after exposure update

    def _wait_read(self, duration: MilliSecond = 1000) -> None:
        time.sleep(1e-3*duration)  # delay after read

    def __repr__(self) -> str:
        cls = self.__class__

        return '{name}(\n{content}\n)'.format(
            name=cls.__name__,
            content='\n'.join([
                '\tstatus: {status},'.format(
                    status=str(self.status),
                ),
                '\tsetup: [{config}],'.format(
                    config=self._read_config,
                ),
            ]),
        )
