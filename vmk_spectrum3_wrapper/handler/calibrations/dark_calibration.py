from vmk_spectrum3_wrapper.data import Datum, Meta
from vmk_spectrum3_wrapper.handler.base_handler import BaseHandler
from vmk_spectrum3_wrapper.units import Units, get_scale


class DarkCalibration(BaseHandler):

    def __init__(self, dark: Dark):
        self._dark = dark

    @property
    def dark(self) -> Dark:
        return self._dark

    # --------        private        --------
    def __call__(self, data: Datum, *args, **kwargs) -> Datum:
        return data - self.dark
