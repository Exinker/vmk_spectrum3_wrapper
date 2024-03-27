from vmk_spectrum3_wrapper.data import Data
from vmk_spectrum3_wrapper.shuffle import Shuffle
from vmk_spectrum3_wrapper.units import Units

from .integration_filter import HighDynamicRangeIntegrationFilter, StandardIntegrationFilter
from .core_filter import ClipFilter, DeviationFilter, OffsetFilter, ScaleFilter, ShuffleFilter
from .pipe_filter import PipeFilter
from .switch_filter import SwitchFilter


class CoreFilterPreset(PipeFilter):

    def __init__(
        self,
        shuffle: Shuffle | None = None,
        units: Units | None = None,
        bias: Data | None = None,
        dark: Data | None = None,
    ):
        units = units or Units.percent

        super().__init__(filters=[
            ShuffleFilter(shuffle) if isinstance(shuffle, Shuffle) else None,
            ClipFilter(),
            ScaleFilter(units=units),
            OffsetFilter(bias) if isinstance(bias, Data) else None,
            DeviationFilter(units=units) if isinstance(bias, Data) else None,
            OffsetFilter(dark) if isinstance(dark, Data) else None,
        ])


class StandardIntegrationFilterPreset(PipeFilter):

    def __init__(
        self,
        shuffle: Shuffle | None = None,
        units: Units | None = None,
        bias: Data | None = None,
        dark: Data | None = None,
        is_averaging: bool = True,
    ):
        super().__init__(filters=[
            CoreFilterPreset(shuffle=shuffle, units=units, bias=bias, dark=dark),
            StandardIntegrationFilter(is_averaging=is_averaging),
        ])


class HighDynamicRangeIntegrationFilterPreset(PipeFilter):

    def __init__(
        self,
        shuffle: Shuffle | None = None,
        units: Units | None = None,
        bias: Data | None = None,
        dark: Data | None = None,
    ):
        super().__init__(filters=[
            SwitchFilter([
                StandardIntegrationFilterPreset(shuffle=shuffle, units=units, bias=bias, dark=dark[0, :]),
                StandardIntegrationFilterPreset(shuffle=shuffle, units=units, bias=bias, dark=dark[1, :]),
            ]),
            HighDynamicRangeIntegrationFilter(),
        ])
