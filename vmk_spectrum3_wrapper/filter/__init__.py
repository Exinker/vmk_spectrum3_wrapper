from typing import TypeAlias

from .flow_filter import ClipFilter, DeviationFilter, OffsetFilter, ScaleFilter, ShuffleFilter
from .buffer_filter import BufferFilter, IntegrationFilter, HighDynamicRangeIntegrationFilter
from .pipe_filter import CoreFilterPreset, IntegrationFilterPreset, PipeFilter


Filter: TypeAlias = CoreFilterPreset | IntegrationFilterPreset | PipeFilter
