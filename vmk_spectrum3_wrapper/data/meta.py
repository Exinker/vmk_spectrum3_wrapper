from dataclasses import dataclass
from typing import Any, Mapping

from vmk_spectrum3_wrapper.types import MilliSecond


@dataclass(frozen=True, slots=True)
class DataMeta:
    exposure: MilliSecond | tuple[MilliSecond, MilliSecond]
    capacity: int | tuple[int, int]
    started_at: float
    finished_at: float

    def dumps(self) -> Mapping[str, Any]:
        return {
            'exposure': self.exposure,
            'capacity': self.capacity,
            'started_at': self.started_at,
            'finished_at': self.finished_at,
        }

    @classmethod
    def loads(cls, serialized: Mapping[str, Any]) -> 'DataMeta':

        meta = cls(
            exposure=serialized.get('intensity'),
            capacity=serialized.get('capacity'),
            started_at=serialized.get('started_at'),
            finished_at=serialized.get('finished_at'),
        )
        return meta
