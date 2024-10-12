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
from vmk_spectrum3_wrapper.filter import F
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


def isclose(a: Array | None, b: Array | None) -> bool:

    if isinstance(a, None) and isinstance(b, None):
        return True
    if isinstance(a, np.ndarray) and isinstance(b, np.ndarray):
        return np.isclose(a, b)

    return False


@pytest.fixture
def fake_device_factory() -> Callable[..., FakeDevice]:

    def inner(*args, **kwargs) -> FakeDevice:
        device = FakeDevice()
        device = device.setup(*args, **kwargs)
        return device

    return inner
