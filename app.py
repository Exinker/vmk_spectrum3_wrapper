import matplotlib.pyplot as plt

from vmk_spectrum3_wrapper.device import Device
from vmk_spectrum3_wrapper.units import get_label


if __name__ == '__main__':
    device = Device()
    device = device.create()
    device = device.connect()
    device = device.set_exposure(4)

    n_frames = 2
    data = device.read(n_frames)

    #
    for i in range(n_frames):
        plt.plot(
            data[i],
            linewidth=1,
            label=f'frame: {i+1}',
        )
    plt.xlabel('number')
    plt.ylabel('I, {units}'.format(
        units=get_label(device.storage.units),
    ))
    plt.legend(loc='upper right')

    plt.show()
