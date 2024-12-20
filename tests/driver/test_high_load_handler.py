import time

import pyspectrum3 as ps3
import pytest

from vmk_spectrum3_wrapper.measurement_manager import to_microsecond
from vmk_spectrum3_wrapper.types import Array, MilliSecond


DATA = []
HIGH_LOAD_TIMEOUT: MilliSecond = 50


def sleep(timeout: MilliSecond) -> None:
    if timeout < 10:  # the smallest time interval limitation
        timeout = 10

    time.sleep(1e-3*timeout)


def on_context(context: ps3.AssemblyContext):
    DATA.append(context.raw_frame)

    time.sleep(1e-3*HIGH_LOAD_TIMEOUT)


@pytest.fixture
def dev():
    dev = ps3.DeviceManager()
    dev.initialize(
        ps3.AutoConfig().config(),
    )
    dev.set_context_callback(on_context)

    dev.connect()

    return dev


@pytest.mark.skip()
@pytest.mark.parametrize('tau', [2, 1, 0.4])
def test_high_load_filter(tau: MilliSecond, dev, n: int = 100) -> None:
    DATA.clear()

    # setup device
    dev.set_exposure(to_microsecond(tau))
    sleep(timeout=2*tau)  # нужно брать старый таймер!

    # read
    dev.read(n)
    sleep(2*(tau + HIGH_LOAD_TIMEOUT)*n)

    #
    assert len(DATA) == n, f'{len(DATA)} frames are recorded instead {n}!'
