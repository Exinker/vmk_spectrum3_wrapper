import pytest

from vmk_spectrum3_wrapper.device import Device
from vmk_spectrum3_wrapper.filter import PipeFilter, ScaleFilter, StandardIntegrationFilter
from vmk_spectrum3_wrapper.storage import BufferStorage
from vmk_spectrum3_wrapper.typing import MilliSecond


@pytest.fixture
def device() -> Device:
    device = Device()
    device = device.connect()
    yield device

    device.disconnect()


def test_read_storage(device: Device, exposure: MilliSecond = 4):
    n_times = 1

    device = device.setup(
        n_times=n_times,
        exposure=exposure,
    )
    data = device.read()

    assert n_times == data.n_times


def test_read_buffer_storage(device: Device, exposure: MilliSecond = 4, capacity: int = 100):
    n_times = 1

    device = device.setup(
        n_times=n_times,
        exposure=exposure,
        capacity=capacity,
        storage=BufferStorage(
            filter=PipeFilter([
                ScaleFilter(),
                StandardIntegrationFilter(),
            ]),
        ),
    )

    data = device.read()

    assert n_times == data.n_times
