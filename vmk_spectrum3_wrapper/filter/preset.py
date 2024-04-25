from vmk_spectrum3_wrapper.data import Data
from vmk_spectrum3_wrapper.shuffle import Shuffle
from vmk_spectrum3_wrapper.units import Units

from .core_filter import ClipFilter, DeviationFilter, OffsetFilter, ScaleFilter, ShuffleFilter
from .integration_filter import HighDynamicRangeIntegrationFilter, StandardIntegrationFilter
from .pipe_filter import PipeFilter
from .switch_filter import SwitchFilter


class CorePreset(PipeFilter):

    def __init__(
        self,
        shuffle: Shuffle | None = None,
        units: Units | None = None,
        bias: Data | None = None,
        dark: Data | None = None,
    ):
        units = units or Units.percent

        filters = [
            ShuffleFilter(shuffle),
            ClipFilter(),
            ScaleFilter(units=units),
            OffsetFilter(offset=bias),
            DeviationFilter(offset=bias, units=units),
            OffsetFilter(offset=dark),
        ]

        super().__init__(
            filters=[item for item in filters if item is not None],
        )


class StandardIntegrationPreset(PipeFilter):

    def __init__(
        self,
        shuffle: Shuffle | None = None,
        units: Units | None = None,
        bias: Data | None = None,
        dark: Data | None = None,
        is_averaging: bool = True,
    ):
        super().__init__(filters=[
            CorePreset(shuffle=shuffle, units=units, bias=bias, dark=dark),
            StandardIntegrationFilter(is_averaging=is_averaging),
        ])


class HighDynamicRangeIntegrationPreset(PipeFilter):

    def __init__(
        self,
        shuffle: Shuffle | None = None,
        units: Units | None = None,
        bias: Data | None = None,
        dark: Data | None = None,
    ):
        super().__init__(filters=[
            SwitchFilter([
                StandardIntegrationPreset(shuffle=shuffle, units=units, bias=bias, dark=dark[0, :]),
                StandardIntegrationPreset(shuffle=shuffle, units=units, bias=bias, dark=dark[1, :]),
            ]),
            HighDynamicRangeIntegrationFilter(),
        ])
