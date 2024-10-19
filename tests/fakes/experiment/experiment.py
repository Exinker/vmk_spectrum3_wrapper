import matplotlib.pyplot as plt
import numpy as np

from tests.fakes.experiment.config import ExperimentConfig, DEFAULT_EXPERIMENT_CONFIG
from tests.utils import calculate_deviation
from vmk_spectrum3_wrapper.config import DEFAULT_DETECTOR
from vmk_spectrum3_wrapper.types import Array, MilliSecond, U


def run_standart_experiment(
    exposure: MilliSecond,
    capacity: int,
    config: ExperimentConfig = DEFAULT_EXPERIMENT_CONFIG,
) -> Array[U]:

    value = np.zeros((capacity, config.detector.config.n_pixels))
    value += config.bias + (config.dark_current + config.light_current)*exposure
    value += np.random.randn(capacity, config.detector.config.n_pixels) * calculate_deviation(value, units=config.units)

    return value


def run_extended_experiment(
    exposure: tuple[MilliSecond, MilliSecond],
    capacity: tuple[int, int],
    config: ExperimentConfig = DEFAULT_EXPERIMENT_CONFIG,
) -> Array[U]:
    assert len(exposure) == len(capacity)

    values = []
    for tau, n in zip(exposure, capacity):
        value = run_standart_experiment(
            exposure=tau,
            capacity=n,
            config=config,
        )
        values.append(value)

    return np.concatenate(values)


if __name__ == '__main__':
    n_numbers = DEFAULT_DETECTOR.config.n_pixels
    exposure = (1, 10)
    capacity = (100, 10)

    number = np.arange(n_numbers)
    value = run_extended_experiment(
        exposure=exposure,
        capacity=capacity,
        config=ExperimentConfig(
            bias=5,
            dark_current=0.2,
            light_current=1 + np.sin(2*np.pi*number/n_numbers),
            detector=DEFAULT_DETECTOR,
        ),
    )
    assert value.shape == (sum(capacity), n_numbers)

    plt.plot(value.T)
    plt.show()
