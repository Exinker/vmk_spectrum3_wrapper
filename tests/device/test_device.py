import pytest

from typing import Callable

import time
from collections.abc import Sequence
from typing import Callable, Mapping

import numpy as np
import pyspectrum3 as ps3

from vmk_spectrum3_wrapper.data import Data, Meta, Datum
from vmk_spectrum3_wrapper.device.device_config import DeviceConfig, DeviceConfigAuto, DeviceConfigManual
from vmk_spectrum3_wrapper.exception import ConnectionDeviceError, DeviceError, SetupDeviceError, StatusDeviceError, eprint
from vmk_spectrum3_wrapper.filters import F
from vmk_spectrum3_wrapper.measurement import Measurement, StandardSchema
from vmk_spectrum3_wrapper.types import Array, Digit, IP, MilliSecond
from vmk_spectrum3_wrapper.units import Units


class FakeDevice:

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


@pytest.fixture
def fake_device_factory() -> Callable[..., FakeDevice]:

    def inner(*args, **kwargs) -> FakeDevice:
        device = FakeDevice()
        device = device.setup(*args, **kwargs)
        return device

    return inner


import pytest


from vmk_spectrum3_wrapper.device.device import Device, DeviceManagerFactory


FAKE_IP = '0.0.0.2'


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


class FakeDeviceManager:

    def __init__(self):
        self.on_context = None
        self.on_status = None
        self.on_error = None

    def set_context_callback(self, callback) -> None:
        self.on_context = callback

    def set_status_callback(self, callback) -> None:
        self.on_status = callback

    def set_error_callback(self, callback) -> None:
        self.on_error = callback

    def set_pipe_filter(self, *args, **kwargs) -> None:
        pass

    def set_measurement(self, *args, **kwargs) -> None:
        pass

    def initialize(self, *args, **kwargs) -> None:
        pass

    def connect(self) -> None:
        message = {
            FAKE_IP: ps3.AssemblyStatus.ALIVE,
        }
        self.on_status(message)

    def read(self) -> None:
        n_frames = 1  # TODO: get n_frames from measurement

        for n in range(n_frames):
            self.on_context(
                context=FakeAssemblyContext(
                    id=FAKE_IP,
                    frame_number=n,
                    result=np.random.randint(0, 2**16-1, size=2048),
                ),
            )


def create_device_manager(self, config: DeviceConfig) -> FakeDeviceManager:
    return FakeDeviceManager()


def test_device_connect(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(DeviceManagerFactory, '_create', create_device_manager)

    device = Device()
    device.connect()

    assert device.is_status(ps3.AssemblyStatus.ALIVE)


@pytest.mark.parametrize(
    'n_times',
    [1, 10, 100],
)
def test_device_setup(
    n_times: int,
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr(DeviceManagerFactory, '_create', create_device_manager)

    device = Device()
    device.connect()
    device.setup(
        n_times=n_times,
        exposure=1,
    )

    data = device.read()

    assert data.n_times == n_times
