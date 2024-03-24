from collections.abc import Sequence
from typing import NewType

from vmk_spectrum3_wrapper.data import Datum
from vmk_spectrum3_wrapper.filter.base_filter import BaseFilter
from vmk_spectrum3_wrapper.units import Units


F = NewType('F', BaseFilter)


class PipeFilter(BaseFilter):
    """Конвейер фильтров."""

    def __init__(self, filters: Sequence[F]):
        self._filters = [item for item in filters if item is not None]

    @property
    def filters(self) -> Sequence[F]:
        return self._filters

    # --------        private        --------
    def __call__(self, datum: Datum, *args, **kwargs) -> Datum:

        for handler in self.filters:
            # print(type(handler), handler)
            try:
                datum = handler(datum, *args, **kwargs)
            except Exception as error:
                print(error)

        return datum

    def __getitem__(self, index: int) -> F:
        return self.filters[index]
