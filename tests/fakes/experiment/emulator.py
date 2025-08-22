import numpy as np

from vmk_spectrum3_wrapper.adc import ADC
from vmk_spectrum3_wrapper.config import DEFAULT_ADC, DEFAULT_DETECTOR
from vmk_spectrum3_wrapper.detector import Detector
from vmk_spectrum3_wrapper.noise import Noise
from vmk_spectrum3_wrapper.types import Array, Digit, MilliSecond, Percent
from vmk_spectrum3_wrapper.units import to_digit, Units
from tests.fakes.experiment.config import SpectrumKernelConfig


# class SpectrumKernelFactory:

#     def __init__(
#         self,
#         adc: ADC = DEFAULT_ADC,
#         detector: Detector = DEFAULT_DETECTOR,
#     ):
#         self.adc = adc
#         self.detector = detector

#     def create(
#         self,
#         bias: Percent,
#         dark_current: Percent,
#         light_current: Percent | Array[Percent],
#     ) -> 'SpectrumKernel':
#         bias = 5
#         dark_current = 10/100/100 * self.adc.value_max
#         light_current

# Units
#         return SpectrumKernel(
#             bias=bias/100 * self.adc.value_max,
#         )


class SpectrumKernel:

    # factory = SpectrumKernelFactory

    def __init__(
        self,
        bias: Digit,
        dark_current: Digit,
        light_current: Digit | Array[Digit],
        units: Units = Units.digit,
    ):
        self.bias = bias
        self.dark_current = dark_current
        self.light_current = light_current
        self.units = units

    def __call__(self, exposure: MilliSecond) -> Array[Digit]:
        return self.bias + exposure * (self.dark_current + self.light_current)


ZERO_SPECTRUM_KERNEL = SpectrumKernel(
    bias=to_digit(5, units=Units.percent),
    durk_current=to_digit(0.01/100, units=Units.percent),
    light_current=to_digit(
        np.zeros(DEFAULT_DETECTOR.config.n_pixels),
        units=Units.percent),
)
LINEAR_SPECTRUM_KERNEL = SpectrumKernel(
    bias=to_digit(5, units=Units.percent),
    durk_current=to_digit(0.01/100, units=Units.percent),
    light_current=to_digit(
        np.linspace(0, 100, DEFAULT_DETECTOR.config.n_pixels),
        units=Units.percent,
    ),
)


class SpectrumEmulator():

    def __init__(
        self,
        kernel: SpectrumKernel,
        detector: Detector = DEFAULT_DETECTOR,
        adc: ADC = DEFAULT_ADC,
    ) -> None:
        self.kernel = kernel
        self.detector = detector
        self.adc = adc

    @property
    def noise(self) -> Noise:
        return Noise(
            detector=self.detector,
            adc=self.adc,
            units=Units.digit,
        )

    def emulate(
        self,
        n_frames: int,
        exposure: MilliSecond,
    ) -> Array[Digit]:

        value = self.kernel(exposure=exposure)
        value += np.random.randn(n_frames, len(value)) * self.noise(value)

        return value
