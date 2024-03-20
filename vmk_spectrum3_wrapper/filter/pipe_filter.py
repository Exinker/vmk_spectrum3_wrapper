from collections.abc import Sequence

from vmk_spectrum3_wrapper.data import Data, Datum
from vmk_spectrum3_wrapper.filter.base_filter import BaseFilter
from vmk_spectrum3_wrapper.filter.buffer_filter import BufferFilter, IntegrationFilter
from vmk_spectrum3_wrapper.filter.flow_filter import ClipFilter, FlowFilter, OffsetFilter, ScaleFilter, SwapFilter
from vmk_spectrum3_wrapper.units import Units


class PipeFilter(BaseFilter):

    def __init__(self, filters: Sequence[FlowFilter | BufferFilter]):
        self._filters = [item for item in filters if item is not None]

    @property
    def filters(self) -> Sequence[FlowFilter]:
        return self._filters

    @property
    def units(self) -> Units:
        return self.filters[0].units

    # --------        private        --------
    def __call__(self, datum: Datum, *args, **kwargs) -> Datum:

        for item in self.filters:
            try:
                datum = item(datum, *args, **kwargs)
            except Exception as error:
                print(error)

        return datum

    def __getitem__(self, index: int) -> FlowFilter:
        return self.filters[index]


# --------        presets        --------
class CoreFilterPreset(PipeFilter):

    def __init__(self, dark: Data | None = None, units: Units = Units.percent):
        super().__init__(filters=[
            SwapFilter(),  # TODO: add `swap`
            ClipFilter(),
            ScaleFilter(units=units),
            OffsetFilter(offset=dark) if isinstance(dark, Data) else None,
        ])


class IntegrationFilterPreset(PipeFilter):

    def __init__(self, dark: Data | None = None, units: Units = Units.percent, is_averaging: bool = True):
        super().__init__(filters=[
            CoreFilterPreset(dark=dark, units=units),
            IntegrationFilter(is_averaging=is_averaging),
        ])
