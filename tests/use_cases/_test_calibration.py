import pytest

from vmk_spectrum3_wrapper.calibration import calibrate_dark
from vmk_spectrum3_wrapper.device import Device
from vmk_spectrum3_wrapper.handler import AverageHandler, OffsetHandler, PipeHandler, ScaleHandler
from vmk_spectrum3_wrapper.storage import BufferStorage
from vmk_spectrum3_wrapper.typing import MilliSecond


@pytest.fixture
def device() -> Device:
    device = Device()
    device = device.connect()
    yield device

    device.disconnect()


def test_calibrate_dark(device: Device, exposure: MilliSecond = 4):
    n_iters = 1

    dark = calibrate_dark(
        device,
        exposure=exposure,
        capacity=100,
    )

    device = device.setup(
        exposure=exposure,
        capacity=2,
        storage=BufferStorage(
            handler=PipeHandler([
                ScaleHandler(),
                AverageHandler(),
                OffsetHandler(
                    dark=dark,
                ),
            ]),
        ),
    )

    data = device.read(n_iters)

    assert n_iters == data.n_times
