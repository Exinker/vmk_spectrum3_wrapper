from vmk_spectrum3_wrapper.data.data import Datum
from vmk_spectrum3_wrapper.data.meta import Meta
from vmk_spectrum3_wrapper.typing import Array, T
from vmk_spectrum3_wrapper.units import Units


class Dark(Datum):

    def __init__(self, intensity: Array[T], units: Units, clipped: Array[bool] | None = None, meta: Meta | None = None):
        super().__init__(intensity=intensity, units=units, clipped=clipped, meta=meta)
