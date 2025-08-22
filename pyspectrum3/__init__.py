from collections.abc import Sequence

from vmk_spectrum3_wrapper.types import MicroSecond


class AssemblyContext:
    pass


from enum import auto, Enum, unique


@unique
class AssemblyStatus(Enum):
    ALIVE = auto()  # {'10.116.220.2': AssemblyStatus.ALIVE}
    DISCONNECTED = auto()
    BUSY = auto()


@unique
class ExceptionType(Enum):
    NETWORK_EXCEPTION = 0
    CONFIG_EXCEPTION = 1
    INVALID_ARGUMENT = 2
    UNKNOWN_EXCEPTION = 4
    CALLBACK_EXCEPTION = 5


@unique
class ExceptionProducer(Enum):
    ASSEMBLY = auto()
    DEVICE = auto()


class DriverException(Exception):
    
    def __init__(
        self,
        messages: Sequence[str],
        ep: ExceptionProducer,
        et: ExceptionType,
    ):
        super().__init__()

        self.messages = messages
        self.ep = ep
        self.et = et


class AsyncDriverException(DriverException):
    pass


class DeviceManager:

    def initialize(self, *args, **kwargs):
        pass

    def set_context_callback(self, *args, **kwargs):
        pass

    def set_status_callback(self, *args, **kwargs):
        pass

    def set_error_callback(self, *args, **kwargs):
        pass

    def connect(self) -> None:
        pass


class AutoConfig():

    def config(self) -> None:
        pass


class DoubleTimer:

    def __init__(self, tau2: MicroSecond, n2: int, tau1: MicroSecond, n1: int) -> None:
        self.exposure = (tau1, tau2)
        self.capacity = (n1, n2)


class Exposure:

    def __init__(self, value: MicroSecond | DoubleTimer) -> None:
        self._value = value

    @property
    def is_double(self) -> bool:
        return isinstance(self._value, DoubleTimer)

    @property
    def single(self) -> MicroSecond:
        return self._value

    @property
    def double(self) -> DoubleTimer:
        return self._value


class Measurement:

    def __init__(self, exposure: Exposure, read_frames_num: int, skip_frames_num: int) -> None:
        self.exposure = exposure
        self.read_frames_num = read_frames_num
        self.skip_frames_num = skip_frames_num


class DefaultCopyPipeFilter:

    @classmethod
    def instance(cls) -> 'DefaultCopyPipeFilter':
        return cls()


for status in AssemblyStatus:
    print(status)