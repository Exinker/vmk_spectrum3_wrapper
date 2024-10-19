import time

import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm

from vmk_spectrum3_wrapper.types import MilliSecond


if __name__ == '__main__':
    interval: tuple[MilliSecond, MilliSecond] = (0, 100)
    n_times = 4*(interval[1] - interval[0]) + 1

    requested = np.linspace(*interval, n_times)
    actual = np.zeros(n_times)

    # measure actual timeouts
    for i, timeout in tqdm(enumerate(requested), total=n_times):
        started_at = time.perf_counter()
        time.sleep(1e-3*timeout)

        actual[i] = 1e+3*(time.perf_counter() - started_at)

    # show
    fig, ax = plt.subplots(figsize=(6, 4), tight_layout=True)

    plt.plot(
        [*interval],
        [*interval],
        color='grey', linestyle=':', linewidth=1,
    )
    plt.scatter(
        requested, actual,
        color='red', marker='+',
    )

    plt.xlim([*interval])
    plt.ylim([*interval])

    plt.xlabel('$t_r$ $[ms]$')
    plt.ylabel('$t_a$ $[ms]$')
    plt.show()
