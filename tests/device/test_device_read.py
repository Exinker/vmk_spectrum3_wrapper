from functools import partial
import logging

import pytest

from vmk_spectrum3_wrapper.device.device import Device, DeviceConfigAuto, DeviceManagerFactory
from vmk_spectrum3_wrapper.measurement_manager.filters import EyeFilter, PipeFilter
from tests.fakes.device import device_manager_factory


LOGGER = logging.getLogger(__name__)


@pytest.mark.parametrize(
    'n_times',
    [1, 10, 100],
)
def test_device_read_standard_schema(
    n_times: int,
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr(Device, 'config', DeviceConfigAuto(change_exposure_delay=0))
    monkeypatch.setattr(DeviceManagerFactory, '_create', partial(device_manager_factory))
    exposure = 1

    device = Device()
    device.connect()
    device.setup(
        n_times=n_times,
        exposure=exposure,
    )

    data = device.read()

    assert data.n_times == n_times


@pytest.mark.parametrize(
    'n_times',
    [1, 10, 100],
)
def test_device_read_extended_schema(
    n_times: int,
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr(Device, 'config', DeviceConfigAuto(change_exposure_delay=0))
    monkeypatch.setattr(DeviceManagerFactory, '_create', partial(device_manager_factory))
    exposure = (1, 10)
    capacity = (10, 1)

    device = Device()
    device.connect()
    device.setup(
        n_times=n_times,
        exposure=exposure,
        capacity=capacity,
        filter=PipeFilter([
            EyeFilter(),
        ]),
    )

    data = device.read()

    assert data.n_times == n_times * sum(capacity)
