import pickle

import numpy as np

from vmk_spectrum3_wrapper.data import Datum
from vmk_spectrum3_wrapper.measurement_manager.filters.base_filter import FilterABC
from vmk_spectrum3_wrapper.measurement_manager.filters.switch_filters import split_shots
from vmk_spectrum3_wrapper.types import MilliSecond


class IntegrationFilterABC(FilterABC):
    """Базоый класс для интегральных фильтров (снижающих размерность данных по времени)."""


class StandardIntegrationFilter(IntegrationFilterABC):
    """Интегральный фильтр."""

    def __init__(self, is_averaging: bool = True):
        self._is_averaging = is_averaging

    @property
    def is_averaging(self) -> bool:
        return self._is_averaging

    def __call__(self, datum: Datum, *args, **kwargs) -> Datum:
        factor = datum.n_times if self.is_averaging else 0

        intensity = np.sum(datum.intensity, axis=0)/factor
        clipped = np.max(datum.clipped, axis=0) if isinstance(datum.clipped, np.ndarray) else None
        deviation = np.sqrt(np.sum(datum.deviation**2, axis=0)/factor) if isinstance(datum.deviation, np.ndarray) else None

        return Datum(
            units=datum.units,
            intensity=intensity,
            clipped=clipped,
            deviation=deviation,
        )

    def __eq__(self, other: 'StandardIntegrationFilter') -> None:
        if not isinstance(other, self.__class__):
            return False

        return all([
            self.is_averaging == other.is_averaging,
        ])


class HighDynamicRangeIntegrationFilter(IntegrationFilterABC):
    """Интегральный в расширенном динамическом диапазоне фильтр."""

    def __call__(self, datum: Datum, *args, exposure: MilliSecond | tuple[MilliSecond, MilliSecond], capacity: int | tuple[int, int], save: bool = True, **kwargs) -> Datum:
        assert datum.n_times == 2

        if save:
            with open('spam.pkl', 'wb') as file:
                pickle.dump(datum, file)

        shots = split_shots(datum, capacity=(1, 1))

        intensity = np.zeros((datum.n_times, datum.n_numbers))
        deviation = np.zeros((datum.n_times, datum.n_numbers))
        weight = np.zeros((datum.n_times, datum.n_numbers))
        factor = np.zeros(datum.n_times)
        for i, shot in enumerate(shots):
            factor[i] = (max(exposure)/exposure[i])

            intensity[i] = shot.intensity * factor[i]
            deviation[i] = shot.deviation * factor[i]
            deviation[i, shot.clipped.flatten()] = np.infty
            weight[i] = (1 / deviation[i]) ** 2

        intensity = np.array([np.dot(intensity, w) for intensity, w in zip(intensity.T, weight.T)] / np.sum(weight, axis=0))
        deviation = np.sqrt(np.array([np.dot(deviation[deviation < np.infty]**2, w[deviation < np.infty]**2) for deviation, w in zip(deviation.T, weight.T)] / np.sum(weight, axis=0) ** 2))
        clipped = np.min([shot.clipped for shot in shots], axis=0).flatten()

        if any(clipped):
            intensity[clipped] = [shot.intensity * factor[i] for i, shot in shots][-1][clipped]
            deviation[clipped] = [shot.deviation * factor[i] for i, shot in shots][-1][clipped]

        return Datum(
            units=datum.units,
            intensity=intensity,
            clipped=clipped,
            deviation=deviation,
        )
