from functools import partial
import logging

import pytest

from vmk_spectrum3_wrapper.device.device import Device, DeviceConfigAuto, DeviceManagerFactory
from vmk_spectrum3_wrapper.measurement_manager import MeasurementManager
from vmk_spectrum3_wrapper.measurement_manager.filters import EyeFilter, PipeFilter, StandardIntegrationPreset
from tests.fakes.device import device_manager_factory


LOGGER = logging.getLogger(__name__)


def test_device_setup_standard_schema_default(
    monkeypatch: pytest.MonkeyPatch,
    caplog,
):
    monkeypatch.setattr(Device, 'config', DeviceConfigAuto(change_exposure_delay=0))
    monkeypatch.setattr(DeviceManagerFactory, '_create', partial(device_manager_factory))
    caplog.set_level(logging.INFO)

    n_times = 1
    exposure = 1
    default_measurement = MeasurementManager.create(
        n_times=n_times,
        exposure=exposure,
        capacity=1,
        filter=StandardIntegrationPreset(),
    )

    device = Device()
    device = device.connect()
    device = device.setup(
        n_times=n_times,
        exposure=exposure,
    )

    assert isinstance(device, Device)
    assert device._measurement_manager == default_measurement
    assert f'Device is setup: {default_measurement}' in caplog.text


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
