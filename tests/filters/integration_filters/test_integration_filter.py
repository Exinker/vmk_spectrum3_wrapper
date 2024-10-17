import pytest

from vmk_spectrum3_wrapper.measurement_manager.filters.integration_filters import StandardIntegrationFilter


@pytest.mark.parametrize(
    'is_averaging', [True, False],
)
def test_standard_integration_filter(
    is_averaging: bool,
):
    filter = StandardIntegrationFilter(
        is_averaging=is_averaging,
    )
