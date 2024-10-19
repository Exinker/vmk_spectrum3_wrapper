import sys
from typing import TextIO

from vmk_spectrum3_wrapper.types import Path


class WrapperError(Exception):
    pass


class WrapperConnectionError(WrapperError):
    pass


class WrapperReadError(WrapperError):
    pass


class WrapperSetupError(WrapperError):
    pass


class WrapperStatusError(WrapperError):
    pass


# --------        storage        --------
class StorageError(Exception):
    pass


class SetupStorageError(StorageError):
    pass


# --------        handler        --------
def eprint(message: str, error: Exception, file: TextIO | Path = sys.stdout) -> None:
    print(f'{message} {error}', file=file, flush=True)
