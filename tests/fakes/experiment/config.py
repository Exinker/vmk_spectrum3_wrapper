from dataclasses import dataclass

from vmk_spectrum3_wrapper.config import DEFAULT_DETECTOR
from vmk_spectrum3_wrapper.detector import Detector
from vmk_spectrum3_wrapper.types import Array
from vmk_spectrum3_wrapper.units import Units


@dataclass(frozen=True, slots=True)
class ExperimentConfig:
    bias: Units.percent
    dark_current: float
    light_current: float | Array[float]
    detector: Detector = DEFAULT_DETECTOR
    units: Units = Units.percent


DEFAULT_EXPERIMENT_CONFIG = ExperimentConfig(
    bias=5,
    dark_current=0.1,
    light_current=0.2,
)
