import pytest

from vmk_spectrum3_wrapper.device import Device
from vmk_spectrum3_wrapper.exception import DeviceError, StorageError
from vmk_spectrum3_wrapper.handler import PipeHandler, AverageHandler, ScaleHandler
from vmk_spectrum3_wrapper.storage import BufferStorage


@pytest.fixture
def device() -> Device:
    device = Device()
    device = device.connect()

    return device


def test_read_standart(device: Device):
    n_iters = 1

    device = device.setup(
        exposure=4,
    )
    data = device.read(n_iters)

    assert n_iters == data.n_times


def test_read_capacity(device: Device):
    n_iters = 1

    device = device.setup(
        exposure=4,
        capacity=100,
        storage=BufferStorage(
            handler=PipeHandler([
                ScaleHandler(),
                AverageHandler(),
            ]),
        ),
    )

    data = device.read(n_iters)

    assert n_iters == data.n_times
