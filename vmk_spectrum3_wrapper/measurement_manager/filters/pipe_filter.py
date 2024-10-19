from collections.abc import Sequence
import logging

from vmk_spectrum3_wrapper.data import Datum
from vmk_spectrum3_wrapper.measurement_manager.filters.base_filter import FilterABC
from vmk_spectrum3_wrapper.measurement_manager.filters.typing import F


LOGGER = logging.getLogger(__name__)


class PipeFilter(FilterABC):
    """Конвейер фильтров."""

    def __init__(self, filters: Sequence[F]):
        self._filters = filters

    @property
    def filters(self) -> Sequence[F]:
        return self._filters

    def __call__(self, datum: Datum, *args, **kwargs) -> Datum:

        for handler in self.filters:
            # LOGGER.debug(
            #     '%s is processing...',
            #     handler.__class__.__name__,
            # )

            try:
                datum = handler(datum, *args, **kwargs)

            except Exception as error:
                LOGGER.error(
                    'An error was happend while processing datum by filter %s',
                    handler,
                    exc_info=error,
                )
                print(error)

        return datum

    def __eq__(self, other: 'PipeFilter') -> bool:
        if not isinstance(other, self.__class__):
            return False

        return self.filters == other.filters

    def __getitem__(self, index: int) -> F:
        return self.filters[index]
