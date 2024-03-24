from dataclasses import dataclass

from vmk_spectrum3_wrapper.typing import MilliSecond


@dataclass(frozen=True, slots=True)
class DataMeta:
    exposure: MilliSecond | tuple[MilliSecond, MilliSecond]
    capacity: int | tuple[int, int]
    started_at: float
    finished_at: float
