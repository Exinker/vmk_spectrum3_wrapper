import threading
import time
from collections.abc import Sequence
from typing import Mapping

import numpy as np

import pyspectrum3 as ps3

from vmk_spectrum3_wrapper.device.config import DeviceConfig, DeviceConfigAuto
from vmk_spectrum3_wrapper.device.exceptions import CreateDeviceError, DeviceError, SetupDeviceError, StatusDeviceError, StatusTypeError, eprint
from vmk_spectrum3_wrapper.storage import Storage
from vmk_spectrum3_wrapper.typing import Array, IP, MicroSecond, MilliSecond, Second


class Device:

    def __init__(self, storage: Storage | None = None, verbose: bool = False) -> None:

        self.condition = threading.Condition(lock=None)
        self.verbose = verbose

        # device
        self._device = None
        self._storage = storage or Storage()
        self._status = None
        self._exposure = None
        self._change_exposure_delay = None

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
        config = config or DeviceConfigAuto()

        # device
        device = _create_device(config)

        device.set_frame_callback(self._on_frame)
        device.set_status_callback(self._on_status)
        device.set_error_callback(self._on_error)

        self._device = device

        #
        self._status = None
        self._is_connected = False
        self._exposure = None
        self._change_exposure_delay = config.change_exposure_delay

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

    # --------        exposure        --------
    @property
    def exposure(self) -> MilliSecond | None:
        return self._exposure

    def set_exposure(self, exposure: MilliSecond) -> 'Device':
        """Set exposure."""
        message = 'Device is not ready to set exposure!'

        # pass checks
        try:
            self._check_creation()
            self._check_connection()
            self._check_status(ps3.AssemblyStatus.ALIVE)

            if exposure == self.exposure:
                raise SetupDeviceError(f'The same exposure: {self.exposure} ms!')

        except DeviceError as error:
            eprint(message=message, error=error)
            return self

        # set exposure
        try:
            self._device.set_exposure(self._to_microsecond(exposure))

        except ps3.DriverException as error:
            eprint(message=message, error=error)
            return self

        else:
            self._exposure = exposure
            time.sleep(self._to_second(self._change_exposure_delay))  # delay after exposure update

            if self.verbose:
                message = f'Setup exposure: {self.exposure} ms!'
                print(message)

        return self

    @staticmethod
    def _to_microsecond(__exposure: MilliSecond) -> MicroSecond:
        value = int(np.round(1000 * __exposure).astype(int))

        assert value % 100 == 0, 'Invalid exposure: {value} mks!'.format(
            value=value,
        )

        return value

    @staticmethod
    def _to_second(__exposure: MilliSecond) -> Second:
        return __exposure / 1000

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
    def read(self, n_frames: int | None = None, blocking: bool = True, timeout: Second = 1e-2) -> Array[int]:
        """Прочитать `n_frames` кадров и вернуть их (blocking).""" """Прочитать `n_frames` кадров в `storage` (non blocking)."""

        # pass checks
        try:
            self._check_creation()
            self._check_connection()
            self._check_status(ps3.AssemblyStatus.ALIVE)
            self._check_exposure()

        except DeviceError as error:
            eprint(
                message='Device is not ready to read!',
                error=error,
            )
            return self

        # clear storage
        self.storage.clear()

        # read data
        self._device.read(n_frames or self.storage.buffer_size)

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

    def _check_exposure(self) -> None:

        if self.exposure is None:
            raise SetupDeviceError('Setup a exposure before!')

    # --------        private        --------
    def __repr__(self) -> str:
        cls = self.__class__

        return '{name}({content})'.format(
            name=cls.__name__,
            content=', '.join([
                '`{assembly}`'.format(
                    assembly=str(self.status),
                ),
                'exposure: {exposure}{units}'.format(
                    exposure='None' if self.exposure is None else f'{self.exposure}',
                    units='' if self.exposure is None else 'ms',
                ),
            ]),
        )
