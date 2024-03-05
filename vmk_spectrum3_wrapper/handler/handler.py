from vmk_spectrum3_wrapper.data import Datum, Meta
from vmk_spectrum3_wrapper.handler.base_handler import BaseHandler
from vmk_spectrum3_wrapper.units import Units, get_scale


class Handler(BaseHandler):
    """Not reduce dimension handlers."""


class ScaleHandler(Handler):
    """Handler to scale a data from `Units.digit` to `units`"""

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
    def __call__(self, data: Datum, *args, **kwargs) -> Datum:
        assert data.units == Units.digit, 'ScaleHandler: {data.units} is not valid! Only `digit` is supported!'

        return Datum(
            intensity=self.scale*data.intensity,
            units=self.units,
            clipped=data.clipped,
            meta=Meta(
                capacity=data.meta.capacity,
                exposure=data.meta.exposure,
                started_at=data.meta.started_at,
                finished_at=data.meta.finished_at,
            ),
        )
