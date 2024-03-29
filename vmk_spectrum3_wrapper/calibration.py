from typing import TYPE_CHECKING

from vmk_spectrum3_wrapper.device import Device
from vmk_spectrum3_wrapper.handler import AverageHandler, PipeHandler, ScaleHandler
from vmk_spectrum3_wrapper.storage import BufferStorage
from vmk_spectrum3_wrapper.typing import MilliSecond

if TYPE_CHECKING:
    from vmk_spectrum3_wrapper.data import Data


def calibrate_dark(device: Device, exposure: MilliSecond, capacity: int = 100) -> 'Data':
    """Calibrate device by dark signal."""

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
    data = device.read(1)

    return data
