from functools import partial
import logging

import pyspectrum3 as ps3
import pytest

from vmk_spectrum3_wrapper.device.device import Device, DeviceConfigAuto, DeviceManagerFactory
from tests.fakes.device import device_manager_factory, FakeDeviceState


LOGGER = logging.getLogger(__name__)


def test_device_connect(
    monkeypatch: pytest.MonkeyPatch,
    caplog,
):
    monkeypatch.setattr(Device, 'config', DeviceConfigAuto(change_exposure_delay=0))
    monkeypatch.setattr(DeviceManagerFactory, '_create', partial(device_manager_factory))
    caplog.set_level(logging.INFO)

    device = Device()
    device = device.connect()

    assert isinstance(device, Device)
    assert device.is_status(ps3.AssemblyStatus.ALIVE)
    assert 'Device is connected.' in caplog.text


def test_device_connect_not_connected_error(
    monkeypatch: pytest.MonkeyPatch,
    caplog,
):
    monkeypatch.setattr(DeviceManagerFactory, '_create', partial(device_manager_factory, state=FakeDeviceState(is_connected=False)))
    caplog.set_level(logging.ERROR)

    device = Device()
    device = device.connect()

    assert isinstance(device, Device)
    assert 'Device is NOT connected!' in caplog.text


def test_device_connect_is_connected_before_error(
    monkeypatch: pytest.MonkeyPatch,
    caplog,
):
    monkeypatch.setattr(Device, 'config', DeviceConfigAuto(change_exposure_delay=0))
    monkeypatch.setattr(DeviceManagerFactory, '_create', partial(device_manager_factory))
    caplog.set_level(logging.ERROR)

    device = Device()
    device = device.connect()
    device = device.connect()

    assert isinstance(device, Device)
    assert 'Device is connected before!' in caplog.text


@pytest.mark.skip('Method: `disconnect` is no longer supported!')
def test_device_disconnect(
    monkeypatch: pytest.MonkeyPatch,
    caplog,
):
    monkeypatch.setattr(Device, 'config', DeviceConfigAuto(change_exposure_delay=0))
    monkeypatch.setattr(DeviceManagerFactory, '_create', partial(device_manager_factory))
    caplog.set_level(logging.INFO)

    device = Device()
    device = device.connect()
    device = device.disconnect()

    assert isinstance(device, Device)
    assert device.is_status(ps3.AssemblyStatus.DISCONNECTED)
    assert 'Device is disconnected.' in caplog.text


@pytest.mark.skip('Method: `disconnect` is no longer supported!')
def test_device_disconnect_not_connected_error(
    monkeypatch: pytest.MonkeyPatch,
    caplog,
):
    monkeypatch.setattr(DeviceManagerFactory, '_create', partial(device_manager_factory, state=FakeDeviceState(is_connected=False)))
    caplog.set_level(logging.ERROR)

    device = Device()
    device = device.connect()
    device = device.disconnect()

    assert isinstance(device, Device)
    assert 'Device is NOT connected!' in caplog.text
