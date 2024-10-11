from vmk_spectrum3_wrapper.filter.core_filter import ShuffleFilter


def test_shuffle_filter_skip():
    filter = ShuffleFilter(
        shuffle=None,
    )

    assert filter is None
