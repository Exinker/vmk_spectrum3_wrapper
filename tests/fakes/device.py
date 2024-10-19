from dataclasses import dataclass, field
import logging

import numpy as np
import pyspectrum3 as ps3

from vmk_spectrum3_wrapper.device.device_config import DeviceConfig
from vmk_spectrum3_wrapper.types import Array, Digit


LOGGER = logging.getLogger(__name__)


class FakeAssemblyContext:

    class AssemblyParams:
        def __init__(self, id: str):
            self.id = id

    class FrameState:
        def __init__(self, frame_number: int):
            self.frame_number = frame_number

    def __init__(
        self,
        id: str,
        frame_number: int,
        result: Array[Digit],
    ):
        self.assembly_params = self.AssemblyParams(
            id=id,
        )
        self.frame_state = self.FrameState(
            frame_number=frame_number,
        )
        self.result = result


@dataclass
class FakeDeviceState:
    is_connected: bool = field(default=True)


class FakeDeviceManager:
    FAKE_IP = '0.0.0.2'

    def __init__(
        self,
        state: FakeDeviceState,
    ):
        self.state = state

        self.on_context = None
        self.on_status = None
        self.on_error = None
        self.measurement = None

    def set_context_callback(self, callback) -> None:
        self.on_context = callback

    def set_status_callback(self, callback) -> None:
        self.on_status = callback

    def set_error_callback(self, callback) -> None:
        self.on_error = callback

    def set_pipe_filter(self, *args, **kwargs) -> None:
        pass

    def set_measurement(self, measurement: ps3.Measurement) -> None:
        self.measurement = measurement

    def initialize(self, *args, **kwargs) -> None:
        pass

    def connect(self) -> None:
        if self.state.is_connected:
            self.on_status({
                self.FAKE_IP: ps3.AssemblyStatus.ALIVE,
            })
        else:
            raise ps3.DriverException(
                messages=['No connected assemblies'],
                ep=ps3.ExceptionProducer.DEVICE,
                et=ps3.ExceptionType.CONFIG_EXCEPTION,
            )

    def disconnect(self) -> None:
        if self.state.is_connected:
            self.on_status({
                self.FAKE_IP: ps3.AssemblyStatus.DISCONNECTED,
            })

    def read(self) -> None:
        n_frames = self.measurement.read_frames_num

        result = np.random.randint(0, 2**16-1, size=(n_frames, 2048))

        for n in range(n_frames):
            self.on_context(
                context=FakeAssemblyContext(
                    id=self.FAKE_IP,
                    frame_number=n + 1,
                    result=result[n, :],
                ),
            )


def device_manager_factory(
    config: DeviceConfig,
    state: bool | None = None,
) -> FakeDeviceManager:
    state = state or FakeDeviceState()

    return FakeDeviceManager(
        state=state,
    )
