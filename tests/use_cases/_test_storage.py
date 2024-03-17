import pytest

from vmk_spectrum3_wrapper.device import Device
from vmk_spectrum3_wrapper.handler import AverageHandler, PipeHandler, ScaleHandler
from vmk_spectrum3_wrapper.storage import BufferStorage
from vmk_spectrum3_wrapper.typing import MilliSecond


@pytest.fixture
def device() -> Device:
    device = Device()
    device = device.connect()
    yield device

    device.disconnect()


def test_read_storage(device: Device, exposure: MilliSecond = 4):
    n_iters = 1

    device = device.setup(
        exposure=exposure,
    )
    data = device.read(n_iters)

    assert n_iters == data.n_times


def test_read_buffer_storage(device: Device, exposure: MilliSecond = 4, capacity: int = 100):
    n_iters = 1

    device = device.setup(
        exposure=exposure,
        capacity=capacity,
        storage=BufferStorage(
            handler=PipeHandler([
                ScaleHandler(),
                AverageHandler(),
            ]),
        ),
    )

    data = device.read(n_iters)

    assert n_iters == data.n_times
