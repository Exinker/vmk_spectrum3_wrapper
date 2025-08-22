import logging
from functools import partial

import numpy as np
import pytest

from tests.fakes.device import device_manager_factory
from vmk_spectrum3_wrapper.calibrations import calibrate_bias
from vmk_spectrum3_wrapper.device.device import Device, DeviceConfigAuto, DeviceManagerFactory


# @pytest.mark.skip()
def test_calibrate_bias(
    monkeypatch: pytest.MonkeyPatch,
    caplog,
):
    monkeypatch.setattr(Device, 'config', DeviceConfigAuto(change_exposure_delay=0))
    monkeypatch.setattr(DeviceManagerFactory, '_create', partial(device_manager_factory))
    caplog.set_level(logging.INFO)

    device = Device()
    device = device.connect()

    bias = calibrate_bias(
        device=device,
        exposure=np.arange(1, 10),
        capacity=100,
    )

    assert bias.n_times == 1
