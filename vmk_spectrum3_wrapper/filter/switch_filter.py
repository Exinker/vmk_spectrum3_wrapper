from collections.abc import Sequence

from vmk_spectrum3_wrapper.data import Datum
from vmk_spectrum3_wrapper.data.utils import crop, join

from .base_filter import BaseFilter
from .pipe_filter import PipeFilter


class SwitchFilter(BaseFilter):
    """ """

    def __init__(self, filters: Sequence[PipeFilter]):
        self._filters = filters

    @property
    def filters(self) -> Sequence[PipeFilter]:
        return self._filters

    # --------        private        --------
    def __call__(self, datum: Datum, *args, capacity: tuple[int, int], **kwargs) -> Datum:
        shots = split_shots(datum, capacity)

        for i, handler in enumerate(self.filters):
            # print(type(handler), handler)
            try:
                shots[i] = handler(shots[i])
            except Exception as error:
                print(error)

        spam = join_shots(shots)

        return spam

    def __getitem__(self, index: int) -> PipeFilter:
        return self.filters[index]


# --------        utils        --------
def split_shots(datum: Datum, capacity: tuple[int, int], n0: int = 0) -> list[Datum]:

    shots = []
    for dn in capacity:
        index = slice(n0, n0+dn)
        shots.append(
            Datum(
                intensity=crop(datum.intensity, index),
                units=datum.units,
                clipped=crop(datum.clipped, index),
                deviation=crop(datum.deviation, index),
            ),
        )

        n0 += dn

    #
    return shots


def join_shots(shots: Sequence[Datum]) -> Datum:
    return Datum(
        intensity=join([shot.intensity for shot in shots]),
        units=shots[0].units,
        clipped=join([shot.clipped for shot in shots]),
        deviation=join([shot.deviation for shot in shots]),
    )
