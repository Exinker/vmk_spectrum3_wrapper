import pytest

from vmk_spectrum3_wrapper.calibration import calibrate_dark
from vmk_spectrum3_wrapper.device import Device
from vmk_spectrum3_wrapper.measurement_manager.filters import OffsetFilter, PipeFilter, ScaleFilter, StandardIntegrationFilter
from vmk_spectrum3_wrapper.measurement_manager.storage import BufferStorage
from vmk_spectrum3_wrapper.types import MilliSecond


@pytest.fixture
def device() -> Device:
    device = Device()
    device = device.connect()
    yield device

    device.disconnect()


@pytest.mark.skip()
def test_calibrate_dark(device: Device, exposure: MilliSecond = 4):
    n_times = 1

    dark = calibrate_dark(
        device,
        exposure=exposure,
        capacity=100,
    )

    device = device.setup(
        n_times=n_times,
        exposure=exposure,
        capacity=2,
        storage=BufferStorage(
            filter=PipeFilter([
                ScaleFilter(),
                StandardIntegrationFilter(),
                OffsetFilter(
                    dark=dark,
                ),
            ]),
        ),
    )

    data = device.read()

    assert data.n_times == n_times
