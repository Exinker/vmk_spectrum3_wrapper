from collections.abc import Sequence

import numpy as np

from vmk_spectrum3_wrapper.config import LOGGER_LEVEL
from vmk_spectrum3_wrapper.data import Datum
from vmk_spectrum3_wrapper.filters.base_filter import FilterABC
from vmk_spectrum3_wrapper.filters.pipe_filters import PipeFilter


class SwitchFilter(FilterABC):
    """Фильтр, разделяющий конвееры обработки данных на несколько (два)."""

    def __init__(self, filters: Sequence[PipeFilter]):
        self._filters = filters

    @property
    def filters(self) -> Sequence[PipeFilter]:
        return self._filters

    def __call__(
        self,
        datum: Datum,
        *args,
        capacity: tuple[int, int],
        **kwargs,
    ) -> Datum:
        shots = split_shots(datum, capacity)

        for i, handler in enumerate(self.filters):
            if LOGGER_LEVEL == 'DEBUG':
                print(type(handler), handler)

            try:
                shots[i] = handler(shots[i])

            except Exception as error:
                print(error)

        return merge_shots(shots)


def split_shots(
    datum: Datum,
    capacity: tuple[int, int],
) -> list[Datum]:
    """Разделить `datum` по `capacity` на несколько (два)."""

    def inner(capacity: tuple[int, int]) -> slice:
        t0 = 0

        for dt in capacity:
            yield slice(t0, t0+dt)

            t0 += dt

    return [
        datum[index, :]
        for index in inner(capacity)
    ]


def merge_shots(
    shots: Sequence[Datum],
) -> Datum:
    """Слить несколько `shots` в один `datum`."""

    def inner(values):
        try:
            return np.concatenate(values, axis=0)

        except Exception as error:
            print(error)

        return None

    if LOGGER_LEVEL == 'DEBUG':
        for i, shot in enumerate(shots):
            print(f'short({i}): {shot.n_times}x{shot.n_numbers}', shot.intensity, shot.clipped)

    return Datum(
        units=shots[0].units,
        intensity=inner([shot.intensity for shot in shots]),
        clipped=inner([shot.clipped for shot in shots]),
        deviation=inner([shot.deviation for shot in shots]),
    )
