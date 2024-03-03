import threading
import time
from collections.abc import Sequence
from typing import Mapping

import pyspectrum3 as ps3

from vmk_spectrum3_wrapper.device.config import DeviceConfig, DeviceConfigAuto, ReadConfig, ReadMode
from vmk_spectrum3_wrapper.device.exceptions import CreateDeviceError, DeviceError, SetupDeviceError, StatusDeviceError, StatusTypeError, eprint
from vmk_spectrum3_wrapper.storage import Storage
from vmk_spectrum3_wrapper.typing import Array, IP, MilliSecond, Second


class Device:

    def __init__(self, storage: Storage | None = None, verbose: bool = False) -> None:

        self.condition = threading.Condition(lock=None)
        self.verbose = verbose

        # device
        self._device = None
        self._storage = storage or Storage()
        self._status = None

        self._device_config = None
        self._read_config = None

    def create(self, config: DeviceConfig | None = None) -> 'Device':
        """Create a device."""

        def _create_device(config: DeviceConfig) -> 'Device':
            """Create device by config and initialize."""
            device = ps3.DeviceManager()

            if isinstance(config, DeviceConfigAuto):
                device.initialize(
                    ps3.AutoConfig().config(),
                )
                return device

            raise ValueError(f'Device {type(config).__name__} is not supported yet!')

        # config
        self._device_config = config or DeviceConfigAuto()

        # device
        device = _create_device(self._device_config)

        device.set_frame_callback(self._on_frame)
        device.set_status_callback(self._on_status)
        device.set_error_callback(self._on_error)

        self._device = device

        #
        self._status = None
        self._is_connected = False
        self._read_config = None

        return self

    def connect(self) -> 'Device':
        """Connect to device."""
        message = 'Device is not ready to connect!'

        # pass checks
        try:
            self._check_creation()
            self._check_connection(state=False)

        except DeviceError as error:
            eprint(message=message, error=error)
            return self

        # connect
        try:
            self._device.connect()

        except ps3.DriverException as error:
            eprint(message=message, error=error)

        else:
            self._is_connected = True

        return self

    def disconnect(self, timeout: Second = 5) -> 'Device':
        """Disconnect from device."""
        message = 'Device is not ready to disconnect!'

        # pass checks
        try:
            self._check_creation()
            self._check_connection(state=True)

        except DeviceError as error:
            eprint(message=message, error=error)
            return self

        # disconnect
        try:
            self._device.disconnect()

        except ps3.DriverException as error:
            eprint(message=message, error=error)

        else:
            self._is_connected = False

        return self

    def setup(self, exposure: MilliSecond | tuple[MilliSecond, MilliSecond]) -> 'Device':
        """Setup device to read."""
        message = 'Device is not ready to setup!'

        config = ReadConfig(
            exposure=exposure,
            capacity=self.storage._capacity,
        )

        # pass checks
        try:
            self._check_creation()
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
                self._device.set_exposure(*config)

            if config.mode == ReadMode.extended:
                self._device.set_double_exposure(*config)

        except ps3.DriverException as error:
            eprint(message=message, error=error)
            return self

        else:
            self._read_config = config

            duration = self._device_config.change_exposure_delay / 1000
            time.sleep(duration)  # delay after exposure update

            if self.verbose:
                message = f'Setup exposure: {self.exposure} ms!'
                print(message)
    
        # setup storage
        self.storage.clear()

        if config.mode == ReadMode.extended:
            pass
            # self.storage.handler

        return self

    # --------        storage        --------
    @property
    def storage(self) -> Storage | None:
        return self._storage

    def set_storage(self, storage: Storage) -> 'Device':
        """"""
        assert isinstance(storage, Storage)

        self._storage = storage

        return self

    # --------        status        --------
    @property
    def status(self) -> Mapping[IP, ps3.AssemblyStatus] | None:
        return self._status

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

        raise StatusTypeError(f'Status type {type(__status)} is not supported yet!')

    # --------        read        --------
    def read(self, n_iters: int, blocking: bool = True, timeout: Second = 1e-2) -> Array[int] | None:
        """Прочитать `n_iters` раз и вернуть данные (blocking), или прочитать `n_iters` раз в `storage` (non blocking)."""

        # pass checks
        try:
            self._check_creation()
            self._check_connection()
            self._check_status(ps3.AssemblyStatus.ALIVE)
            self._check_read_config()

        except DeviceError as error:
            eprint(
                message='Device is not ready to read!',
                error=error,
            )
            return self

        # read data
        self._device.read(n_iters * self.storage.capacity)

        if blocking:
            time.sleep(timeout)  # FIXME: нужна задержка, так как статуc не всегда успевает измениться

            with self.condition:
                while not self.is_status(ps3.AssemblyStatus.ALIVE):
                    self.condition.wait(timeout)

            return self.storage.pull()

    # --------        callbacks        --------
    def _on_frame(self, frame: Array[int]) -> None:
        self.storage.put(frame)

        # # verbose
        # if self.verbose:
        #     print('on_frame:', len(frame), flush=True)

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
    def _check_creation(self) -> None:
        if self._device is None:
            raise CreateDeviceError('Create a device before!')

    def _check_connection(self, state: bool = True) -> None:
        if self._is_connected != state:
            raise CreateDeviceError({
                True: 'Device have to be connected before!',
                False: 'Device is connected before!',
            }.get(state))

    def _check_status(self, __status: ps3.AssemblyStatus | Sequence[ps3.AssemblyStatus]) -> None:

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
