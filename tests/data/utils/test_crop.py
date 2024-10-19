from vmk_spectrum3_wrapper.data.utils import crop


def test_crop_none():
    value = None

    assert crop(value, index=tuple()) is None
