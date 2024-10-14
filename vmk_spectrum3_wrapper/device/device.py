from collections.abc import Sequence
import logging
import time
from typing import Callable, Mapping

import numpy as np
import pyspectrum3 as ps3

from vmk_spectrum3_wrapper.data import Data, Meta
from vmk_spectrum3_wrapper.device.device_config import DeviceConfig, DeviceConfigAuto, DeviceConfigManual
from vmk_spectrum3_wrapper.exception import ConnectionDeviceError, DeviceError, SetupDeviceError, StatusDeviceError, eprint
from vmk_spectrum3_wrapper.filter import F
from vmk_spectrum3_wrapper.measurement import Measurement
from vmk_spectrum3_wrapper.types import Array, Digit, IP, MilliSecond


LOGGER = logging.getLogger(__name__)


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

        try:
            self._check_connection(state=False)
        except DeviceError as error:
            LOGGER.error(
                'Device is not ready!',
                exc_info=error,
            )
            return self

        try:
            self.device.connect()
        except ps3.DriverException as error:
            LOGGER.info(
                'Device is not connected!',
                exc_info=error,
            )
            return self
        else:
            LOGGER.info(
                'Device is connected.',
            )
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
            LOGGER.error(
                'Device is not ready!',
                exc_info=error,
            )
            return self

        try:
            self.device.set_pipe_filter(ps3.DefaultCopyPipeFilter.instance())
            self.device.set_measurement(ps3.Measurement(*self._measurement))
        except ps3.DriverException as error:
            LOGGER.error(
                'Device is not setup!',
                exc_info=error,
            )
            return self
        else:
            self._wait(
                duration=self.config.change_exposure_delay,  # TODO: ждем пока Сергей реализует get_current_mode и get_current_exposure для двойного времени экспозиции
            )
            LOGGER.info(
                'Device is setup: %s',
                self._measurement,
            )

        return self

    def read(
        self,
        blocking: bool = True,
        timeout: MilliSecond = 100,
    ) -> Data | None:
        """Прочитать и вернуть данные (blocking), или прочитать в `storage` (non blocking)."""

        try:
            self._check_connection()
            # self._check_status(ps3.AssemblyStatus.ALIVE)  # TODO: по какой-то причине иногда не приходит статус ps3.AssemblyStatus.ALIVE
            self._check_measurement()
        except DeviceError as error:
            LOGGER.error(
                'Device is not ready!',
                exc_info=error,
            )
            return None

        self.device.read()
        self._wait(timeout)

        if blocking:
            while self._measurement.progress < 1:
                self._wait(timeout)
                LOGGER.debug(
                    'Reading data: %d%s',
                    self._measurement.progress*100,
                    '%',
                )

            frames, started_at, finished_at = self._measurement.storage.pull()
            if LOGGER.isEnabledFor(logging.INFO):
                n_frames = len(frames)
                seconds = (finished_at - started_at)*(n_frames)/(n_frames - 1) if n_frames > 1 else 0
                LOGGER.info(
                    'Reading is complete! Total: %d frames in %.3fs (approx).',
                    n_frames,
                    seconds,
                )

            return Data.squeeze(
                frames,
                Meta(
                    exposure=self._measurement.storage.exposure,
                    capacity=self._measurement.storage.capacity,
                    started_at=started_at,
                    finished_at=finished_at,
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

    def _on_context(self, context: ps3.AssemblyContext) -> None:
        LOGGER.debug(
            'Data is received: %s (%d)',
            context.assembly_params.id,
            context.frame_state.frame_number,
        )
        self._on_frame(
            frame=np.array(context.result),
        )

    def _on_frame(self, frame: Array[Digit]) -> None:
        self._measurement.put(frame)

    def _on_status(self, status: Mapping[IP, ps3.AssemblyStatus]) -> None:
        LOGGER.info(
            'Status is updated: %s.',
            status,
        )
        self._status = status

    def _on_error(self, error: ps3.AsyncDriverException) -> None:
        LOGGER.error(
            'Error is raised: %s',
            error,
            exc_info=error,
        )

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
