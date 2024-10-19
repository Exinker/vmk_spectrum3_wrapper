import numpy as np

from vmk_spectrum3_wrapper.types import MicroSecond, MilliSecond


def to_microsecond(__exposure: MilliSecond) -> MicroSecond:
    return int(np.round(1000 * __exposure).astype(int))
