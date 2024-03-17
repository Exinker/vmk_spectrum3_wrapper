from vmk_spectrum3_wrapper.data import Data, Datum, Meta
from vmk_spectrum3_wrapper.handler.base_handler import BaseHandler
from vmk_spectrum3_wrapper.units import Units, get_scale


class Handler(BaseHandler):
    """Not reduce dimension handlers."""


class SwapHandler(Handler):
    """Handler to swap a datum if needed."""

    def __init__(self, flag: bool = False):
        self._flag = flag

    @property
    def flag(self) -> bool:
        return self._flag

    # --------        private        --------
    def __call__(self, datum: Datum, *args, **kwargs) -> Datum:

        if not self.flag:
            return datum

        return Datum(
            intensity=datum.intensity.flip(),
            units=datum.units,
            clipped=datum.clipped.flip(),
            meta=Meta(
                capacity=datum.meta.capacity,
                exposure=datum.meta.exposure,
                started_at=datum.meta.started_at,
                finished_at=datum.meta.finished_at,
            ),
        )


class ScaleHandler(Handler):
    """Handler to scale a datum from `Units.digit` to `units`"""

    def __init__(self, units: Units | None = None):
        self._units = units or Units.percent
        self._scale = get_scale(self.units)

    @property
    def units(self) -> Units:
        return self._units

    @property
    def scale(self) -> float:
        return self._scale

    # --------        private        --------
    def __call__(self, datum: Datum, *args, **kwargs) -> Datum:
        assert datum.units == Units.digit, 'ScaleHandler: {datum.units} is not valid! Only `digit` is supported!'

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


class OffsetHandler(BaseHandler):

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
