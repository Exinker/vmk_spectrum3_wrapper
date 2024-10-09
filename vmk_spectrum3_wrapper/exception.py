import sys
from typing import TextIO

from vmk_spectrum3_wrapper.types import Path


# --------        device        --------
class DeviceError(Exception):
    pass


class ConnectionDeviceError(Exception):
    pass


class ReadDeviceError(Exception):
    pass


class SetupDeviceError(DeviceError):
    pass


class StatusDeviceError(DeviceError):
    pass


# --------        storage        --------
class StorageError(Exception):
    pass


class SetupStorageError(StorageError):
    pass


# --------        handler        --------
def eprint(message: str, error: Exception, file: TextIO | Path = sys.stdout) -> None:
    print(f'{message} {error}', file=file, flush=True)
