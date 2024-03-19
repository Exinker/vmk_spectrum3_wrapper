import threading
import time
from collections.abc import Sequence
from typing import Mapping

import pyspectrum3 as ps3

from vmk_spectrum3_wrapper.data import Data
from vmk_spectrum3_wrapper.device.config import DeviceConfig, DeviceConfigAuto, ReadConfig, ReadMode
from vmk_spectrum3_wrapper.exception import ConnectionDeviceError, DeviceError, SetupDeviceError, StatusDeviceError, eprint
from vmk_spectrum3_wrapper.storage import FrameStorage
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

    @property
    def storage(self) -> FrameStorage | None:
        return self._storage

    # --------        handlers        --------
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

    def setup(self, exposure: MilliSecond | tuple[MilliSecond, MilliSecond], capacity: int | tuple[int, int] = 1, storage: FrameStorage | None = None) -> 'Device':
        """Setup device to read."""
        message = 'Device is not ready to setup!'
        config = ReadConfig(
            exposure=exposure,
            capacity=capacity,
        )

        # setup storage
        self._storage = storage or FrameStorage()
        self._storage.setup(
            exposure=exposure,
            capacity=capacity,
        )

        # pass checks
        try:
            self._check_connection()
            self._check_status(ps3.AssemblyStatus.ALIVE)

            if config == self._read_config:
                raise SetupDeviceError(f'The same read config: {self._read_config} ms!')

        except DeviceError as error:
            eprint(message=message, error=error)
            return self

        # setup device
        try:
            if config.mode == ReadMode.standart:
                self.device.set_exposure(*config)

            if config.mode == ReadMode.extended:
                self.device.set_double_exposure(*config)

        except ps3.DriverException as error:
            eprint(message=message, error=error)
            return self

        else:
            self._wait_set_exposure(config.duration)
            self._read_config = config

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
            self._check_read_config()

        except DeviceError as error:
            eprint(
                message='Device is not ready to read!',
                error=error,
            )
            return None

        # read data
        n_frames = n_iters * self._read_config.n_frames
        self.device.read(n_frames)
        self._wait_read()

        # block
        if blocking:
            while len(self.storage) < n_iters:
                time.sleep(1e-3*timeout)

            return Data.squeeze(self.storage.pull())

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
        self.storage.put(frame)

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

    def _check_read_config(self) -> None:

        if self._read_config is None:
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
