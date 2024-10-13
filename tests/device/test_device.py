import pytest

from typing import Callable

import time
from collections.abc import Sequence
from typing import Callable, Mapping

import numpy as np
import pyspectrum3 as ps3

from vmk_spectrum3_wrapper.data import Data, Meta, Datum
from vmk_spectrum3_wrapper.device.device import Device, DeviceManagerFactory
from vmk_spectrum3_wrapper.device.device_config import DeviceConfig
from vmk_spectrum3_wrapper.types import Array, Digit, IP, MilliSecond


class FakeDeviceManager:

    def __init__(self):
        self.on_context = None
        self.on_status = None
        self.on_error = None
        self._is_connected = False
        self._filter = None
        self._measurement = None

    def set_context_callback(self, __on_context: Callable[[ps3.AssemblyContext], None]):
        self.on_context = __on_context

    def set_status_callback(self, __on_status: Callable[[Mapping[IP, ps3.AssemblyStatus]], None]):
        self.on_context = __on_status

    def set_error_callback(self, __on_error: Callable[[ps3.AsyncDriverException], None]):
        self.on_context = __on_error

    def connect(self) -> None:
        self._is_connected = True

    def disconnect(self) -> None:
        self._is_connected = False

    def set_pipe_filter(self, __filter: ps3.DefaultCopyPipeFilter) -> None:
        self._filter = __filter

    def set_measurement(self, __measurement: ps3.Measurement) -> None:
        self._measurement = __measurement

    def read(self) -> None:
        print()


def _create(self, config: DeviceConfig) -> FakeDeviceManager:
    return FakeDeviceManager()


def test_device_read(
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr(DeviceManagerFactory, '_create', _create)

    device = Device()

    assert True
