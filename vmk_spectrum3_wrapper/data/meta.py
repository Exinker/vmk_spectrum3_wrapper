from dataclasses import dataclass

from vmk_spectrum3_wrapper.typing import MilliSecond


@dataclass(frozen=True, slots=True)
class Meta:
    capacity: int | tuple[int, int]
    exposure: MilliSecond | tuple[MilliSecond, MilliSecond]

    started_at: float
    finished_at: float | None
