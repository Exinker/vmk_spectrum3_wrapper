from collections.abc import Sequence

import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm

from vmk_spectrum3_wrapper.data import Data
from vmk_spectrum3_wrapper.device import Device
from vmk_spectrum3_wrapper.measurement_manager.filters import StandardIntegrationPreset, SwitchFilter
from vmk_spectrum3_wrapper.types import MilliSecond
from vmk_spectrum3_wrapper.units import Units


def calibrate_dark(
    device: Device,
    exposure: MilliSecond | tuple[MilliSecond, MilliSecond],
    capacity: int | tuple[int, int],
    units: Units | None = None,
    bias: Data | None = None,
    show: bool = False,
    save: bool = False,
) -> Data:
    """Calibrate device by dark signal."""

    device = device.setup(
        n_times=1,
        exposure=exposure,
        capacity=capacity,
        filter={
            int: StandardIntegrationPreset(units=units, bias=bias),
            tuple: SwitchFilter([
                StandardIntegrationPreset(units=units, bias=bias),
                StandardIntegrationPreset(units=units, bias=bias),
            ]),
        }.get(type(capacity)),
    )
    dark = device.read()

    # show
    if show:
        dark.show()

    # save
    if save:
        dark.save('dark.pkl')

    #
    return dark


def calibrate_bias(
    device: Device,
    exposure: Sequence[MilliSecond],
    capacity: int,
    units: Units | None = None,
    show: bool = False,
    save: bool = False,
) -> Data:
    """Calibrate device by bias signal."""

    data = []
    for tau in tqdm(exposure):
        device = device.setup(
            n_times=1,
            exposure=tau.item(),
            capacity=capacity,
            filter=StandardIntegrationPreset(
                units=units,
            ),
        )
        datum = device.read()

        #
        data.append(datum)

    # bias
    intensity = np.array([datum.intensity.flatten() for datum in data])
    clipped = np.array([datum.clipped.flatten() for datum in data])

    n_numbers = intensity.shape[1]

    bias = np.zeros(n_numbers)
    for n in range(n_numbers):
        mask = ~clipped[:, n]

        bias[n] = np.polyfit(exposure[mask], intensity[mask, n], deg=1)[1]

    bias = Data(
        units=datum.units,
        intensity=bias.reshape(1, -1),
        clipped=np.full(n_numbers, False),  # FIXME:
        deviation=np.full(n_numbers, 0),  # FIXME: calculate from polyfit
        meta=None,  # FIXME:
    )

    # show
    if show:

        # show data
        plt.subplots(figsize=(6, 4), tight_layout=True)

        for datum in data:
            plt.step(
                datum.number, datum.intensity.flatten(),
                where='mid',
            )

        plt.step(
            bias.number, bias.intensity.flatten(),
            where='mid',
            color='black', linestyle='-', linewidth=1.5,
        )

        plt.show()

    # save
    if save:
        bias.save('bias.pkl')

    #
    return bias
