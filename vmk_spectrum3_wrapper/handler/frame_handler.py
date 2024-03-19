import numpy as np

from vmk_spectrum3_wrapper.adc import ADC
from vmk_spectrum3_wrapper.data import Data, Datum, Meta
from vmk_spectrum3_wrapper.detector import Detector
from vmk_spectrum3_wrapper.device.config import _ADC, _DETECTOR
from vmk_spectrum3_wrapper.handler.base_handler import BaseHandler
from vmk_spectrum3_wrapper.noise import Noise
from vmk_spectrum3_wrapper.typing import Array, Digit, U
from vmk_spectrum3_wrapper.units import Units


class FrameHandler(BaseHandler):
    """One frame or not reduce dimension handlers."""

    def __init__(self, skip: bool = False):
        self._skip = skip

    @property
    def skip(self) -> bool:
        return self._skip


# --------        raw signal handlers        --------
class SwapHandler(FrameHandler):
    """Handler to swap a frame if needed."""

    def __init__(self, skip: bool = False):
        super().__init__(skip=skip)

    def kernel(self, value: Array[Digit] | None) -> Array[Digit] | None:
        if value is None:
            return None

        return value[::-1]

    # --------        private        --------
    def __call__(self, datum: Datum, *args, **kwargs) -> Datum:
        assert datum.units == Units.digit, f'{self.__class__.__name__}: {datum.units} is not valid! Only `digit` is supported!'
        assert datum.n_times == 1, 'Only 1d `datum` are supported!'

        #
        if self.skip:
            return datum

        return Datum(
            intensity=self.kernel(datum.intensity),
            units=datum.units,
            clipped=self.kernel(datum.clipped),
            deviation=self.kernel(datum.deviation),
            meta=datum.meta,
        )


class ClipHandler(FrameHandler):
    """Handler to clip a datum."""

    def __init__(self, adc: ADC | None = None, skip: bool = False):
        super().__init__(skip=skip)

        self.adc = adc or _ADC  # TODO:
        self.value_max = self.adc.value_max

    def kernel(self, value: Array[Digit]) -> Array[bool]:
        return value == self.value_max

    # --------        private        --------
    def __call__(self, datum: Datum, *args, **kwargs) -> Datum:
        assert datum.units == Units.digit, f'{self.__class__.__name__}: {datum.units} is not valid! Only `digit` is supported!'
        assert datum.n_times == 1, 'Only 1d `datum` are supported!'

        #
        if self.skip:
            return datum

        return Datum(
            intensity=datum.intensity,
            units=datum.units,
            clipped=self.kernel(datum.intensity),
            deviation=datum.deviation,
            meta=datum.meta,
        )


class ScaleHandler(FrameHandler):
    """Handler to scale a datum from `Units.digit` to `units`."""

    def __init__(self, units: Units | None = None, skip: bool = False):
        super().__init__(skip=skip)

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
        assert datum.n_times == 1, 'Only 1d `datum` are supported!'

        #
        if self.skip:
            return datum

        return Datum(
            intensity=self.kernel(datum.intensity),
            units=self.units,
            clipped=datum.clipped,
            deviation=self.kernel(datum.deviation),
            meta=datum.meta,
        )


# --------        calibrations        --------
class OffsetHandler(FrameHandler):
    """Calibrate `data` by offset intensity."""

    def __init__(self, offset: Data, skip: bool = False):
        super().__init__(skip=skip)

        assert offset.n_times == 1, 'Only 1d `datum` are supported!'
        self._offset = offset

    @property
    def offset(self) -> Data:
        return self._offset

    @property
    def units(self) -> Units:
        return self.offset.units

    # --------        private        --------
    def __call__(self, datum: Datum, *args, **kwargs) -> Datum:
        assert datum.units == self.units
        assert datum.n_times == 1, 'Only 1d `datum` are supported!'
        assert datum.n_numbers == self.offset.n_numbers

        #
        if self.skip:
            return datum

        return Datum(
            intensity=datum.intensity - self.offset.intensity,
            units=datum.units,
            clipped=datum.clipped | self.offset.clipped,
            deviation=np.sqrt(datum.deviation**2 + self.offset.deviation**2),
            meta=datum.meta,
        )


# --------        others        --------
class DeviationHandler(FrameHandler):
    """Calculate a deviation of the `data`."""

    def __init__(self, units: Units, adc: ADC | None = None, detector: Detector | None = None, skip: bool = False):
        super().__init__(skip=skip)

        self.units = units
        self.adc = adc or _ADC  # FIXME: remove it!
        self.detector = detector or _DETECTOR  # FIXME: remove it!

        self.noise = Noise(
            adc=self.adc,
            detector=self.detector,
            units=self.units,
            n_frames=1,
        )

    def kernel(self, value: Array[Digit]) -> Array[Digit]:
        return self.noise(value)

    # --------        private        --------
    def __call__(self, datum: Datum, *args, **kwargs) -> Datum:
        assert datum.units == self.units
        assert datum.n_times == 1, 'Only 1d `datum` are supported!'

        #
        if self.skip:
            return datum

        return Datum(
            intensity=datum.intensity,
            units=datum.units,
            clipped=datum.clipped,
            deviation=self.kernel(datum.intensity),
            meta=datum.meta,
        )
