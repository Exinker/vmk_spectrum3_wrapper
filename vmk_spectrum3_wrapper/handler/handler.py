from typing import Callable

import numpy as np

from vmk_spectrum3_wrapper.handler.base_handler import BaseHandler
from vmk_spectrum3_wrapper.typing import Array, Digit, T
from vmk_spectrum3_wrapper.units import Units, get_scale


class Handler(BaseHandler):
    """Not reduce dimension handlers."""


class ScaleHandler(Handler):
    """Handler to scale a data from `Units.digit` to `units`"""

    def __init__(self, units: Units | None = None):
        self._units = units or Units.percent
        self._scale = get_scale(units)

    @property
    def units(self) -> Units:
        return self._units

    @property
    def scale(self) -> float:
        return self._scale

    # --------        private        --------
    def __call__(self, data: Array[Digit], *args, **kwargs) -> Array[T]:
        return self.scale*data
