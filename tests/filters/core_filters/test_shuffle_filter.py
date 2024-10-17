from vmk_spectrum3_wrapper.measurement_manager.filters.core_filters import ShuffleFilter


def test_shuffle_filter_skip():
    filter = ShuffleFilter(
        shuffle=None,
    )

    assert filter is None
