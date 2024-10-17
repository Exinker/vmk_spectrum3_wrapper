import pytest

from vmk_spectrum3_wrapper.device import Device
from vmk_spectrum3_wrapper.measurement_manager.filters import PipeFilter, ScaleFilter, StandardIntegrationFilter
from vmk_spectrum3_wrapper.measurement_manager.storage import BufferStorage
from vmk_spectrum3_wrapper.types import MilliSecond


@pytest.fixture
def device() -> Device:
    device = Device()
    device = device.connect()
    yield device

    device.disconnect()


@pytest.mark.skip()
def test_read_storage(device: Device, exposure: MilliSecond = 4):
    n_times = 1

    device = device.setup(
        n_times=n_times,
        exposure=exposure,
    )
    data = device.read()

    assert data.n_times == n_times


@pytest.mark.skip()
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

    assert data.n_times == n_times
