import numpy as np

from vmk_spectrum3_wrapper.exception import SetupDeviceError
from vmk_spectrum3_wrapper.typing import MilliSecond

from .utils import to_microsecond


def validate_exposure(exposure: MilliSecond) -> None:

    if not isinstance(exposure, (int, float)):
        raise SetupDeviceError('Время экспозиции должно быть числом!')
    if not exposure > 0:
        raise SetupDeviceError('Время экспозиции должно быть положительным числом!')
    if not to_microsecond(exposure) % 100 == 0:
        raise SetupDeviceError('Время экспозиции должно быть кратным 100 мкс!')


def validate_capacity(capacity: int) -> None:

    if not isinstance(capacity, int):
        raise SetupDeviceError('Количество накоплений должно быть целым числом!')
    if not (capacity > 0 and capacity < 2**24):
        raise SetupDeviceError('Количество накоплений должно быть числом с диапазоне [1; 2**24 - 1]!')
