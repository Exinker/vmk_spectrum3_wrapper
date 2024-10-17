from abc import abstractmethod
from typing import Any, Literal, overload

import numpy as np

from vmk_spectrum3_wrapper.adc import ADC
from vmk_spectrum3_wrapper.config import DEFAULT_ADC, DEFAULT_DETECTOR
from vmk_spectrum3_wrapper.data import Data, Datum
from vmk_spectrum3_wrapper.measurement_manager.filters.base_filter import FilterABC
from vmk_spectrum3_wrapper.measurement_manager.filters.exceptions import DatumFilterError, FilterError
from vmk_spectrum3_wrapper.noise import Noise
from vmk_spectrum3_wrapper.shuffle import Shuffle
from vmk_spectrum3_wrapper.types import Array, Digit, U
from vmk_spectrum3_wrapper.units import Units


class CoreFilterABC(FilterABC):
    """Базовый класс для основных фильтров (не снижающих размерность данных!)."""

    @abstractmethod
    def kernel(self, value: Array[U] | None) -> Array[Any] | None:
        raise NotImplementedError


class EyeFilter(CoreFilterABC):
    """Единичный (без преобразований) фильтр."""

    def kernel(self, value: Array[U]) -> Array[U]:
        return value

    def __call__(self, datum: Datum, *args, **kwargs) -> Datum:
        return Datum(
            units=datum.units,
            intensity=datum.intensity,
            clipped=self.kernel(datum.intensity),
            deviation=datum.deviation,
        )


class ShuffleFilter(CoreFilterABC):
    """Смещения и перестановок фильтр."""

    def __new__(cls, shuffle: Shuffle | None):
        if shuffle is None:
            return None

        return super().__new__(cls)

    def __init__(self, shuffle: Shuffle):
        if not isinstance(shuffle, Shuffle):
            raise FilterError(f'{self.__class__.__name__} is not support shuffle: {type(shuffle)}!')

        self._shuffle = shuffle

    @property
    def shuffle(self) -> Shuffle:
        return self._shuffle

    @overload
    def kernel(self, value: Array[Digit]) -> Array[Digit]: ...
    @overload
    def kernel(self, value: Array[bool]) -> Array[bool]: ...
    @overload
    def kernel(self, value: None) -> None: ...
    def kernel(self, value):
        if value is None:
            return None

        return self.shuffle(value)

    def __call__(self, datum: Datum, *args, **kwargs) -> Datum:
        if not (datum.units == Units.digit):
            raise DatumFilterError(f'{datum.units} is not valid! Only `digit` is supported!')

        return Datum(
            units=datum.units,
            intensity=self.kernel(datum.intensity),
            clipped=self.kernel(datum.clipped),
            deviation=self.kernel(datum.deviation),
        )

    def __eq__(self, other: 'ShuffleFilter') -> None:
        if not isinstance(other, self.__class__):
            return False

        return all([
            self.shuffle == other.shuffle,
        ])


class ClipFilter(CoreFilterABC):
    """Маскирование зашкаленных отсчетов фильтр."""

    def __init__(self, adc: ADC = DEFAULT_ADC):
        if not (adc == DEFAULT_ADC):
            raise FilterError('Change `DEFAULT_ADC` in config file instead!')

        self._adc = adc

    @property
    def adc(self) -> ADC:
        return self._adc

    @property
    def value_max(self) -> int:
        return self.adc.value_max

    def kernel(self, value: Array[Digit]) -> Array[bool]:
        return value == self.value_max

    def __call__(self, datum: Datum, *args, **kwargs) -> Datum:
        if not (datum.units == Units.digit):
            raise DatumFilterError(f'{datum.units} is not valid! Only `digit` is supported!')

        return Datum(
            units=datum.units,
            intensity=datum.intensity,
            clipped=self.kernel(datum.intensity),
            deviation=datum.deviation,
        )

    def __eq__(self, other: 'ClipFilter') -> None:
        if not isinstance(other, self.__class__):
            return False

        return all([
            self.adc == other.adc,
        ])


class ScaleFilter(CoreFilterABC):
    """Масштабирования фильтр. Перевод из `Units.digit` в `units`."""

    def __init__(self, units: Units = Units.percent):
        self._units = units

    @property
    def units(self) -> Units:
        return self._units

    @property
    def scale(self) -> Units:
        return self.units.scale

    @overload
    def kernel(self, value: Array[Digit]) -> Array[U]: ...
    @overload
    def kernel(self, value: None) -> None: ...
    def kernel(self, value):
        if value is None:
            return None

        return self.scale*value

    def __call__(self, datum: Datum, *args, **kwargs) -> Datum:
        if not (datum.units == Units.digit):
            raise DatumFilterError(f'{datum.units} is not valid! Only `digit` is supported!')

        return Datum(
            units=self.units,
            intensity=self.kernel(datum.intensity),
            clipped=datum.clipped,
            deviation=self.kernel(datum.deviation),
        )

    def __eq__(self, other: 'ScaleFilter') -> None:
        if not isinstance(other, self.__class__):
            return False

        return all([
            self.units == other.units,
            self.scale == other.scale,
        ])


class OffsetFilter(CoreFilterABC):
    """Смещение `intensity` на велиличину `offset` фильтр."""

    def __new__(cls, offset: Data | None):
        if offset is None:
            return None

        return super().__new__(cls)

    def __init__(self, offset: Data):
        if not isinstance(offset, Data):
            raise FilterError(f'{self.__class__.__name__} is not support offset: {type(offset)}!')
        if not (offset.units == Units.percent):
            raise FilterError(f'{offset.units} is not valid! Only `persent` is supported!')

        self._offset = offset

    @property
    def offset(self) -> Data:
        return self._offset

    @overload
    def kernel(self, value: Array[U], kind: Literal['intensity', 'clipped', 'deviation']) -> Array[U]: ...
    @overload
    def kernel(self, value: Array[bool], kind: Literal['intensity', 'clipped', 'deviation']) -> Array[bool]: ...
    @overload
    def kernel(self, value: None, kind: Literal['intensity', 'clipped', 'deviation']) -> None: ...
    def kernel(self, value, kind):
        if value is None:
            return None

        if kind == 'intensity':
            return value - self.offset.intensity.flatten()
        if kind == 'clipped':
            return value | self.offset.clipped.flatten()
        if kind == 'deviation':
            return np.sqrt(value**2 + self.offset.deviation.flatten()**2)

    def __call__(self, datum: Datum, *args, **kwargs) -> Datum:
        if not (datum.units == self.offset.units):
            raise DatumFilterError(f'{datum.units} is not valid!')
        if not (datum.n_numbers == self.offset.n_numbers):
            raise DatumFilterError(f'{datum.units} is not valid!')

        return Datum(
            units=datum.units,
            intensity=self.kernel(datum.intensity, kind='intensity'),
            clipped=self.kernel(datum.clipped, kind='clipped'),
            deviation=self.kernel(datum.deviation, kind='deviation'),
        )

    def __eq__(self, other: 'OffsetFilter') -> None:
        if not isinstance(other, self.__class__):
            return False

        return all([
            self.offset == other.offset,
        ])


class DeviationFilter(CoreFilterABC):
    """Расчет стандартного отклонения фильтр."""

    def __new__(cls, offset: Data | None, *args, **kwargs):
        if offset is None:
            return None

        return super().__new__(cls)

    def __init__(
        self,
        offset: Data,  # `offset` is necessary to calculate a deviation correctly!
        units: Units,
    ):
        self._units = units
        self._noise = Noise(
            adc=DEFAULT_ADC,
            detector=DEFAULT_DETECTOR,
            units=self.units,
            n_frames=1,
        )

    @property
    def units(self) -> Units:
        return self._units

    @property
    def noise(self) -> Noise:
        return self._noise

    def kernel(self, value: Array[U]) -> Array[U]:
        return self.noise(value)

    def __call__(self, datum: Datum, *args, **kwargs) -> Datum:
        assert datum.units == self.units

        return Datum(
            intensity=datum.intensity,
            units=datum.units,
            clipped=datum.clipped,
            deviation=self.kernel(datum.intensity),
        )

    def __eq__(self, other: 'DeviationFilter') -> None:
        if not isinstance(other, self.__class__):
            return False

        return all([
            self.units == other.units,
            self.noise == other.noise,
        ])
