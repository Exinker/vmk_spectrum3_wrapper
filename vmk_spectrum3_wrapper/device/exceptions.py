import sys
from typing import TextIO

from vmk_spectrum3_wrapper.typing import Path


# --------        device        --------
class DeviceError(Exception):
    pass


class CreateDeviceError(DeviceError):
    pass


class SetupDeviceError(DeviceError):
    pass


class StatusDeviceError(DeviceError):
    pass


class ReadDeviceError(Exception):
    pass


class ConnectionDeviceError(Exception):
    pass


# --------        status        --------
class StatusTypeError(Exception):
    pass


# --------        handlers        --------
def eprint(message: str, error: Exception, file: TextIO | Path = sys.stdout) -> None:
    print(f'{message} {error}', file=file, flush=True)
