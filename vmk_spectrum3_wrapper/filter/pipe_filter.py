from collections.abc import Sequence

from vmk_spectrum3_wrapper.data import Datum
from vmk_spectrum3_wrapper.filter.base_filter import BaseFilter
from vmk_spectrum3_wrapper.filter.buffer_filter import BufferFilter, IntegrationFilter
from vmk_spectrum3_wrapper.filter.flow_filter import ClipFilter, FlowFilter, ScaleFilter, SwapFilter
from vmk_spectrum3_wrapper.units import Units


class PipeFilter(BaseFilter):

    def __init__(self, filters: Sequence[FlowFilter | BufferFilter]):
        self._filters = filters

    @property
    def filters(self) -> Sequence[FlowFilter]:
        return self._filters

    @property
    def units(self) -> Units:
        return self.filters[0].units

    # --------        private        --------
    def __call__(self, datum: Datum, *args, **kwargs) -> Datum:

        for filter in self.filters:
            datum = filter(datum, *args, **kwargs)

        return datum

    def __getitem__(self, index: int) -> FlowFilter:
        return self.filters[index]


# --------        presets        --------
class CoreFilterPreset(PipeFilter):

    def __init__(self, units: Units = Units.percent):
        super().__init__(filters=[
            SwapFilter(),
            ClipFilter(),
            ScaleFilter(units=units),
        ])


class IntegrationFilterPreset(PipeFilter):

    def __init__(self, units: Units = Units.percent, is_averaging: bool = True):
        super().__init__(filters=[
            CoreFilterPreset(units=units),
            IntegrationFilter(is_averaging=is_averaging),
        ])
