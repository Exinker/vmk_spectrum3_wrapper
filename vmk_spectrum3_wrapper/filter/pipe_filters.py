from collections.abc import Sequence

from vmk_spectrum3_wrapper.config import DEBUG
from vmk_spectrum3_wrapper.data import Datum
from vmk_spectrum3_wrapper.filter.base_filter import FilterABC
from vmk_spectrum3_wrapper.filter.typing import F


class PipeFilter(FilterABC):
    """Конвейер фильтров."""

    def __init__(self, filters: Sequence[F]):
        self._filters = filters

    @property
    def filters(self) -> Sequence[F]:
        return self._filters

    def __call__(self, datum: Datum, *args, **kwargs) -> Datum:

        for handler in self.filters:
            if DEBUG:
                print(type(handler), handler)

            try:
                datum = handler(datum, *args, **kwargs)

            except Exception as error:
                print(error)

        return datum

    def __getitem__(self, index: int) -> F:
        return self.filters[index]
