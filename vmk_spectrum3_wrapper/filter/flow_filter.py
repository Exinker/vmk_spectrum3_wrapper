from abc import abstractmethod
from typing import Any, Literal

import numpy as np

from vmk_spectrum3_wrapper.adc import ADC
from vmk_spectrum3_wrapper.config import _ADC, _DETECTOR
from vmk_spectrum3_wrapper.data import Data, Datum
from vmk_spectrum3_wrapper.detector import Detector
from vmk_spectrum3_wrapper.noise import Noise
from vmk_spectrum3_wrapper.shuffle import Shuffle
from vmk_spectrum3_wrapper.typing import Array, Digit, U
from vmk_spectrum3_wrapper.units import Units

from .base_filter import BaseFilter


class FlowFilter(BaseFilter):
    """Не снижающий размерность фильтр."""

    @abstractmethod
    def kernel(self, value: Array[U] | None) -> Array[Any] | None:
        raise NotImplementedError


# --------        core filters        --------
class ShuffleFilter(FlowFilter):
    """Смещения и перестановок фильтр."""

    def __init__(self, shuffle: Shuffle):
        self.shuffle = shuffle

    def kernel(self, value: Array[Digit] | None) -> Array[Digit] | None:
        if value is None:
            return None

        match value.ndim:
            case 1:
                return value[::-1]
            case 2:
                return np.fliplr(value)
            case _:
                raise ValueError

    # --------        private        --------
    def __call__(self, datum: Datum, *args, **kwargs) -> Datum:
        assert datum.units == Units.digit, f'{self.__class__.__name__}: {datum.units} is not valid! Only `digit` is supported!'

        return Datum(
            intensity=self.kernel(datum.intensity),
            units=datum.units,
            clipped=self.kernel(datum.clipped),
            deviation=self.kernel(datum.deviation),
        )


class ClipFilter(FlowFilter):
    """Маскирование зашкаленных отсчетов фильтр."""

    def __init__(self, adc: ADC | None = None):
        self.adc = adc or _ADC  # TODO:
        self.value_max = self.adc.value_max

    def kernel(self, value: Array[Digit]) -> Array[bool]:
        return value == self.value_max

    # --------        private        --------
    def __call__(self, datum: Datum, *args, **kwargs) -> Datum:
        assert datum.units == Units.digit, f'{self.__class__.__name__}: {datum.units} is not valid! Only `digit` is supported!'

        return Datum(
            intensity=datum.intensity,
            units=datum.units,
            clipped=self.kernel(datum.intensity),
            deviation=datum.deviation,
        )


class ScaleFilter(FlowFilter):
    """Масштабирования фильтр. Перевод из `Units.digit` в `units`."""

    def __init__(self, units: Units | None = None):
        self._units = units or Units.percent
        self._scale = self.units.scale

    @property
    def units(self) -> Units:
        return self._units

    def kernel(self, value: Array[Digit] | None) -> Array[U] | None:
        if value is None:
            return None

        return self._scale*value

    # --------        private        --------
    def __call__(self, datum: Datum, *args, **kwargs) -> Datum:
        assert datum.units == Units.digit, f'{self.__class__.__name__}: {datum.units} is not valid! Only `digit` is supported!'

        return Datum(
            intensity=self.kernel(datum.intensity),
            units=self.units,
            clipped=datum.clipped,
            deviation=self.kernel(datum.deviation),
        )


# --------        calibrations        --------
class OffsetFilter(FlowFilter):
    """Смещение `intensity` на велиличину `offset` фильтр."""

    def __init__(self, offset: Data):
        self._offset = offset

    @property
    def offset(self) -> Data:
        return self._offset

    def kernel(self, value: Array | None, kind: Literal['intensity', 'clipped', 'deviation']) -> Array | None:
        if (value is None):
            return None

        match kind:
            case 'intensity':
                return value - self.offset.intensity.flatten()
            case 'clipped':
                return value | self.offset.clipped.flatten()
            case 'deviation':
                return np.sqrt(value**2 + self.offset.deviation.flatten()**2)

    # --------        private        --------
    def __call__(self, datum: Datum, *args, **kwargs) -> Datum:
        assert datum.units == self.offset.units
        assert datum.n_numbers == self.offset.n_numbers

        return Datum(
            intensity=self.kernel(datum.intensity, kind='intensity'),
            units=datum.units,
            clipped=self.kernel(datum.clipped, kind='clipped'),
            deviation=self.kernel(datum.deviation, kind='deviation'),
        )


# --------        others        --------
class DeviationFilter(FlowFilter):
    """Расчет стандартного отклонения фильтр."""

    def __init__(self, units: Units, adc: ADC | None = None, detector: Detector | None = None):
        self._units = units
        self._adc = adc or _ADC  # FIXME: remove it!
        self._detector = detector or _DETECTOR  # FIXME: remove it!

        self.noise = Noise(
            adc=self._adc,
            detector=self._detector,
            units=self.units,
            n_frames=1,
        )

    @property
    def units(self) -> Units:
        return self._units

    def kernel(self, value: Array[U]) -> Array[U]:
        return self.noise(value)

    # --------        private        --------
    def __call__(self, datum: Datum, *args, **kwargs) -> Datum:
        assert datum.units == self.units

        return Datum(
            intensity=datum.intensity,
            units=datum.units,
            clipped=datum.clipped,
            deviation=self.kernel(datum.intensity),
        )
