import random
import time

import pytest

from vmk_spectrum3_wrapper.data import Meta
from vmk_spectrum3_wrapper.types import MilliSecond


@pytest.mark.parametrize(
    ['exposure', 'capacity'],
    [
        (1, 10),
        ((1, 100), (100, 1)),
    ],
)
def test_meta_consistency(
    exposure: MilliSecond | tuple[MilliSecond, MilliSecond],
    capacity: int | tuple[int, int],
):
    started_at = time.time()
    meta = Meta(
        exposure=exposure,
        capacity=capacity,
        started_at=started_at,
        finished_at=started_at + random.randint(0, 100),
    )

    dump = meta.dumps()

    assert Meta.loads(dump) == meta
