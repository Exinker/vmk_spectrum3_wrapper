import matplotlib.pyplot as plt

from vmk_spectrum3_wrapper.device import Device, DeviceConfigAuto
from vmk_spectrum3_wrapper.storage import BufferDeviceStorage
from vmk_spectrum3_wrapper.units import get_label


if __name__ == '__main__':
    device = Device(
        storage=BufferDeviceStorage(),
    )
    device = device.create(
        config=DeviceConfigAuto(),
    )
    device = device.connect()
    device = device.set_exposure(4)

    data = device.read(1)

    #
    plt.plot(
        data.flatten(),
    )

    plt.xlabel('number')
    plt.ylabel('I, {units}'.format(
        units=get_label(device.storage.units),
    ))

    plt.show()
