import matplotlib.pyplot as plt

from vmk_spectrum3_wrapper.device import Device


if __name__ == '__main__':
    device = Device()
    device = device.connect()
    device = device.setup(exposure=4)

    n_frames = 2
    data = device.read(n_frames)

    #
    for t in range(n_frames):
        plt.plot(
            data.intensity[t, :],
            linewidth=1,
            label=f'frame: {t+1}',
        )
    plt.xlabel(r'number')
    plt.ylabel(r'$I$ [{units}]'.format(
        units=data.units.label,
    ))
    plt.legend(loc='upper right')

    plt.show()
