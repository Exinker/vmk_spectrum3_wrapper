from collections.abc import Sequence
import logging
import time
from typing import Callable, Mapping, overload

import numpy as np
import pyspectrum3 as ps3

from vmk_spectrum3_wrapper.data import Data, Meta
from vmk_spectrum3_wrapper.device.device_config import DeviceConfig, DeviceConfigAuto, DeviceConfigManual
from vmk_spectrum3_wrapper.exception import WrapperConnectionError, WrapperError, WrapperSetupError, WrapperStatusError, eprint
from vmk_spectrum3_wrapper.measurement_manager import MeasurementManager
from vmk_spectrum3_wrapper.measurement_manager.filters import F
from vmk_spectrum3_wrapper.types import Array, Digit, IP, MilliSecond


LOGGER = logging.getLogger(__name__)


class DeviceManagerFactory:

    def __init__(
        self,
        on_context: Callable[[ps3.AssemblyContext], None] | None = None,
        on_status: Callable[[Mapping[IP, ps3.AssemblyStatus]], None] | None = None,
        on_error: Callable[[ps3.AsyncDriverException], None] | None = None,
    ) -> None:

        self.on_context = on_context
        self.on_status = on_status
        self.on_error = on_error

    def create(self, config: DeviceConfig) -> ps3.DeviceManager:
        """Create device by config and initialize it."""

        device_manager = self._create(config=config)

        if self.on_context:
            device_manager.set_context_callback(self.on_context)
        if self.on_status:
            device_manager.set_status_callback(self.on_status)
        if self.on_error:
            device_manager.set_error_callback(self.on_error)

        return device_manager

    def _create(self, config: DeviceConfig) -> ps3.DeviceManager:  # pragma: no cover

        device_manager = ps3.DeviceManager()

        if isinstance(config, DeviceConfigAuto):
            device_manager.initialize(
                ps3.AutoConfig().config(),
            )
            return device_manager

        if isinstance(config, DeviceConfigManual):
            device_manager.initialize(
                ps3.DeviceConfigFile([ps3.AssemblyConfigFile(ip) for ip in config.ip]),
            )
            return device_manager

        raise ValueError(f'Device {type(config).__name__} is not supported yet!')


class Device:

    def __init__(
        self,
        config: DeviceConfig | None = None,
        verbose: bool = False,
    ) -> None:

        self._config = config or DeviceConfigAuto()
        self._device_manager = DeviceManagerFactory(
            on_context=self._on_context,
            on_status=self._on_status,
            on_error=self._on_error,
        ).create(
            config=self.config,
        )
        self._measurement_manager = None
        self._status = None
        self._is_connected = False

        self.verbose = verbose

    @property
    def config(self) -> DeviceConfig:
        return self._config

    @property
    def device_manager(self) -> ps3.DeviceManager:
        return self._device_manager

    @property
    def status(self) -> Mapping[IP, ps3.AssemblyStatus] | None:
        return self._status

    def connect(self) -> 'Device':
        """Connect to device."""

        try:
            self._check_connection(state=False)
        except WrapperConnectionError as error:
            LOGGER.error(
                f'{error.__class__.__name__}: {error.__str__()}',
            )
            return self

        try:
            self.device_manager.connect()
        except ps3.DriverException as error:
            LOGGER.error(
                'Device is NOT connected!',
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

        LOGGER.error(
            'Method: `disconnect` is no longer supported!',
        )
        return self

        try:
            self._check_connection(state=True)
        except WrapperError as error:
            LOGGER.error(
                f'{error.__class__.__name__}: {error.__str__()}',
            )
            return self

        try:
            self.device_manager.disconnect()
        except ps3.DriverException as error:
            LOGGER.error(
                'Device is not disconnected!',
                exc_info=error,
            )
            return self
        else:
            LOGGER.info(
                'Device is disconnected.',
            )
            self._is_connected = False

        return self

    @overload
    def setup(
        self,
        n_times: int,  # количество повторений схемы измерения (schema)
        exposure: MilliSecond,  # базовое время экспозиции
        capacity: int = 1,  # количество накоплений
        filter: F | None = None,
    ) -> 'Device': ...
    @overload
    def setup(
        self,
        n_times: int,  # количество повторений схемы измерения (schema)
        exposure: tuple[MilliSecond, MilliSecond],  # базовое время экспозиции в расширенном режиме измерений
        capacity: tuple[int, int] = ...,  # количество накоплений в расширенном режиме измерений
        filter: F | None = None,
    ) -> 'Device': ...
    def setup(self, n_times, exposure, capacity=1, filter=None):
        """Setup device to read a measurement."""

        self._measurement_manager = MeasurementManager.create(
            n_times=n_times,
            exposure=exposure,
            capacity=capacity,
            filter=filter,
        )

        try:
            self._check_connection(state=True)
            # self._check_status(ps3.AssemblyStatus.ALIVE)
        except WrapperConnectionError as error:
            LOGGER.error(
                f'{error.__class__.__name__}: {error.__str__()}',
            )
            return self

        try:
            self.device_manager.set_pipe_filter(ps3.DefaultCopyPipeFilter.instance())
            self.device_manager.set_measurement(ps3.Measurement(*self._measurement_manager))
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
                self._measurement_manager,
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
        except WrapperError as error:
            LOGGER.error(
                'Device is not ready!',
                exc_info=error,
            )
            return None

        self.device_manager.read()
        self._wait(timeout)

        if blocking:
            while self._measurement_manager.progress < 1:
                self._wait(timeout)
                LOGGER.debug(
                    'Reading data: %d%s',
                    self._measurement_manager.progress*100,
                    '%',
                )

            data, started_at, finished_at = self._measurement_manager.storage.pull()
            if LOGGER.isEnabledFor(logging.INFO):
                n_data = len(data)
                seconds = finished_at - started_at
                LOGGER.info(
                    'Reading is completed! Total: %d data in %.3fs (approx).',
                    n_data,
                    seconds,
                )

            return Data.squeeze(
                data,
                Meta(
                    exposure=self._measurement_manager.storage.exposure,
                    capacity=self._measurement_manager.storage.capacity,
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

        raise WrapperStatusError(f'Status type {type(__status)} is not supported yet!')

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
        self._measurement_manager.put(frame)

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
            if state is False:
                raise WrapperConnectionError('Device is connected before!')
            if state is True:
                raise WrapperConnectionError('Device have to be connected before!')

    def _check_status(self, __status: ps3.AssemblyStatus | Sequence[ps3.AssemblyStatus]) -> None:

        if self.status is None:
            raise WrapperConnectionError('Device is not found! Check the connection!')

        if not self.is_status(__status):
            message = 'Fix assembly before: {ip}!'.format(
                ip=', '.join([
                    ip
                    for ip, status in self.status.items()
                    if status != __status
                ]),
            )
            raise WrapperStatusError(message)

    def _check_measurement(self) -> None:
        if self._measurement_manager is None:
            raise WrapperSetupError('Setup a device before!')

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
                    measurement=self._measurement_manager,
                ),
            ]),
        )
