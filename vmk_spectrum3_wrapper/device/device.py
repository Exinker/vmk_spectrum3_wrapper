import time
from collections.abc import Sequence
from typing import Callable, Mapping

import numpy as np
import pyspectrum3 as ps3

from vmk_spectrum3_wrapper.data import Data, DataMeta
from vmk_spectrum3_wrapper.device.config import DeviceConfig, DeviceConfigAuto, DeviceConfigManual
from vmk_spectrum3_wrapper.exception import ConnectionDeviceError, DeviceError, SetupDeviceError, StatusDeviceError, eprint
from vmk_spectrum3_wrapper.filter import F
from vmk_spectrum3_wrapper.measurement import Measurement
from vmk_spectrum3_wrapper.types import Array, Digit, IP, MilliSecond


class DeviceFactory:

    def __init__(
        self,
        on_context: Callable[[ps3.AssemblyContext], None] | None = None,
        on_status: Callable[[Mapping[IP, ps3.AssemblyStatus]], None] | None = None,
        on_error: Callable[[ps3.AsyncDriverException], None] | None = None,
    ) -> None:

        self.on_context = on_context
        self.on_status = on_status
        self.on_error = on_error

    def create(self, config: DeviceConfig) -> 'Device':
        """Create device by config and initialize it."""

        device = self._create(config=config)

        if self.on_context:
            device.set_context_callback(self.on_context)
        if self.on_status:
            device.set_status_callback(self.on_status)
        if self.on_error:
            device.set_error_callback(self.on_error)

        return device

    def _create(self, config: DeviceConfig) -> 'Device':

        device = ps3.DeviceManager()

        if isinstance(config, DeviceConfigAuto):
            device.initialize(
                ps3.AutoConfig().config(),
            )
            return device

        if isinstance(config, DeviceConfigManual):
            device.initialize(
                ps3.DeviceConfigFile([ps3.AssemblyConfigFile(ip) for ip in config.ip]),
            )
            return device

        raise ValueError(f'Device {type(config).__name__} is not supported yet!')


class Device:

    def __init__(
        self,
        config: DeviceConfig | None = None,
        verbose: bool = False,
    ) -> None:

        self._config = config or DeviceConfigAuto()
        self._device = DeviceFactory(
            on_context=self._on_context,
            on_status=self._on_status,
            on_error=self._on_error,
        ).create(
            config=self.config,
        )
        self._status = None
        self._is_connected = False

        self.verbose = verbose

    @property
    def config(self) -> DeviceConfig:
        return self._config

    @property
    def device(self) -> 'Device':
        return self._device

    @property
    def status(self) -> Mapping[IP, ps3.AssemblyStatus] | None:
        return self._status

    def connect(self) -> 'Device':
        """Connect to device."""
        emessage = 'Device is not ready to connect!'

        try:
            self._check_connection(state=False)
        except DeviceError as error:
            eprint(message=emessage, error=error)

            return self

        try:
            self.device.connect()
        except ps3.DriverException as error:
            eprint(message=emessage, error=error)
        else:
            self._is_connected = True

        return self

    def disconnect(self) -> 'Device':
        """Disconnect from device."""
        emessage = 'Device is not ready to disconnect!'

        try:
            self._check_connection(state=True)
        except DeviceError as error:
            eprint(message=emessage, error=error)

            return self

        try:
            self.device.disconnect()
        except ps3.DriverException as error:
            eprint(message=emessage, error=error)
        else:
            self._is_connected = False

        return self

    def setup(
        self,
        n_times: int,
        exposure: MilliSecond | tuple[MilliSecond, MilliSecond],
        capacity: int | tuple[int, int] = 1,
        handler: F | None = None,
    ) -> 'Device':
        """Setup device to read."""
        emessage = 'Device is not ready to setup!'

        self._measurement = Measurement.create(
            n_times=n_times,
            exposure=exposure,
            capacity=capacity,
            handler=handler,
        )

        try:
            self._check_connection()
            self._check_status(ps3.AssemblyStatus.ALIVE)
        except DeviceError as error:
            eprint(message=emessage, error=error)

            return self

        try:
            self.device.set_pipe_filter(ps3.DefaultCopyPipeFilter.instance())
            self.device.set_measurement(ps3.Measurement(*self._measurement))
        except ps3.DriverException as error:
            eprint(message=emessage, error=error)

            return self
        else:
            self._wait(
                duration=self.config.change_exposure_delay,  # TODO: ждем пока Сергей реализует get_current_mode и get_current_exposure для двойного времени экспозиции
            )
            if self.verbose:
                emessage = f'Setup: {self._measurement}'
                print(emessage)

        return self

    def read(
        self,
        blocking: bool = True,
        timeout: MilliSecond = 100,
    ) -> Data | None:
        """Прочитать и вернуть данные (blocking), или прочитать в `storage` (non blocking)."""

        # pass checks
        try:
            self._check_connection()
            # self._check_status(ps3.AssemblyStatus.ALIVE)  # TODO: по какой-то причине должго не приходит статус ps3.AssemblyStatus.ALIVE
            self._check_measurement()

        except DeviceError as error:
            eprint(
                message='Device is not ready to read!',
                error=error,
            )
            return None

        # read data
        self.device.read()
        self._wait(timeout)

        # block
        if blocking:
            while self._measurement.progress < 1:
                self._wait(timeout)

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
    def _on_context(self, context: ps3.AssemblyContext) -> None:
        self._on_frame(
            frame=np.array(context.result),
        )

    def _on_frame(self, frame: Array[Digit]) -> None:
        self._measurement.put(frame)

        if self.verbose:
            print('on_frame:', len(frame), frame, flush=True)

    def _on_status(self, status: Mapping[IP, ps3.AssemblyStatus]) -> None:
        self._status = status

        if self.verbose:
            print('on_status:', status, flush=True)

    def _on_error(self, error: ps3.AsyncDriverException) -> None:

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
    @staticmethod
    def _wait(duration: MilliSecond) -> None:
        time.sleep(1e-3*duration)

    def __repr__(self) -> str:
        cls = self.__class__

        return '{name}(\n{content}\n)'.format(
            name=cls.__name__,
            content='\n'.join([
                '\tstatus: {status},'.format(
                    status=str(self.status),
                ),
                '\tsetup: [{measurement}],'.format(
                    measurement=self._measurement,
                ),
            ]),
        )
