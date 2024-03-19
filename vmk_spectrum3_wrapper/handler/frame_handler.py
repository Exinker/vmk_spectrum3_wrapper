from vmk_spectrum3_wrapper.adc import ADC
from vmk_spectrum3_wrapper.data import Data, Datum, Meta
from vmk_spectrum3_wrapper.detector import Detector
from vmk_spectrum3_wrapper.device.config import _ADC, _DETECTOR
from vmk_spectrum3_wrapper.handler.base_handler import BaseHandler
from vmk_spectrum3_wrapper.noise import Noise
from vmk_spectrum3_wrapper.typing import Array, Digit
from vmk_spectrum3_wrapper.units import Units


class FrameHandler(BaseHandler):
    """One frame or not reduce dimension handlers."""


# --------        raw signal handlers        --------
class SwapHandler(FrameHandler):
    """Handler to swap a datum if needed."""

    def __init__(self, flag: bool = False):
        self._flag = flag

        if self._flag:
            raise NotImplementedError

    @property
    def flag(self) -> bool:
        return self._flag

    # --------        private        --------
    def __call__(self, datum: Datum, *args, **kwargs) -> Datum:
        assert datum.units == Units.digit, f'{self.__class__.__name__}: {datum.units} is not valid! Only `digit` is supported!'

        if not self.flag:
            return datum

        return Datum(
            intensity=datum.intensity.flip(),
            units=datum.units,
            meta=Meta(
                capacity=datum.meta.capacity,
                exposure=datum.meta.exposure,
                started_at=datum.meta.started_at,
                finished_at=datum.meta.finished_at,
            ),
        )


class ClipHandler(FrameHandler):
    """Handler to clip a datum."""

    def __init__(self, adc: ADC | None = None):
        self.adc = adc or _ADC  # TODO:
        self.value_max = self.adc.value_max

    def handle(self, value: Array[Digit]) -> Array[bool]:
        return value >= self.value_max

    # --------        private        --------
    def __call__(self, datum: Datum, *args, **kwargs) -> Datum:
        assert datum.units == Units.digit, f'{self.__class__.__name__}: {datum.units} is not valid! Only `digit` is supported!'

        return Datum(
            intensity=datum.intensity,
            units=datum.units,
            clipped=self.handle(datum.intensity),
            meta=Meta(
                capacity=datum.meta.capacity,
                exposure=datum.meta.exposure,
                started_at=datum.meta.started_at,
                finished_at=datum.meta.finished_at,
            ),
        )


class ScaleHandler(FrameHandler):
    """Handler to scale a datum from `Units.digit` to `units`."""

    def __init__(self, units: Units | None = None):
        self._units = units or Units.percent
        self._scale = self.units.scale

    @property
    def units(self) -> Units:
        return self._units

    @property
    def scale(self) -> float:
        return self._scale

    # --------        private        --------
    def __call__(self, datum: Datum, *args, **kwargs) -> Datum:
        assert datum.units == Units.digit, f'{self.__class__.__name__}: {datum.units} is not valid! Only `digit` is supported!'

        return Datum(
            intensity=self.scale*datum.intensity,
            units=self.units,
            clipped=datum.clipped,
            meta=Meta(
                capacity=datum.meta.capacity,
                exposure=datum.meta.exposure,
                started_at=datum.meta.started_at,
                finished_at=datum.meta.finished_at,
            ),
        )


# --------        calibrations        --------
class OffsetHandler(FrameHandler):
    """Calibrate `data` by offset intensity."""

    def __init__(self, offset: Data):
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

        return Datum(
            intensity=datum.intensity - self.offset.intensity,
            units=datum.units,
            clipped=datum.clipped | self.offset.clipped,
            meta=Meta(
                capacity=datum.meta.capacity,
                exposure=datum.meta.exposure,
                started_at=datum.meta.started_at,
                finished_at=datum.meta.finished_at,
            ),
        )


# --------        others        --------
class DeviationHandler(FrameHandler):
    """Calculate a deviation of the `data`."""

    def __init__(self, units: Units, adc: ADC | None = None, detector: Detector | None = None):
        self.units = units
        self.adc = adc or _ADC  # FIXME: remove it!
        self.detector = detector or _DETECTOR  # FIXME: remove it!

        self.noise = Noise(
            adc=self.adc,
            detector=self.detector,
            units=self.units,
            n_frames=1,
        )

    def handle(self, value: Array[Digit]) -> Array[Digit]:
        return self.noise(value)

    # --------        private        --------
    def __call__(self, datum: Datum, *args, **kwargs) -> Datum:
        assert datum.units == self.units

        return Datum(
            intensity=datum.intensity,
            units=datum.units,
            clipped=datum.clipped,
            deviation=self.handle(datum.intensity),
            meta=Meta(
                capacity=datum.meta.capacity,
                exposure=datum.meta.exposure,
                started_at=datum.meta.started_at,
                finished_at=datum.meta.finished_at,
            ),
        )
