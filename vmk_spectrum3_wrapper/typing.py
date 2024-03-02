from typing import NewType, TypeAlias, TypeVar

from numpy.typing import NDArray


# --------        types        --------
Array: TypeAlias = NDArray

IP = NewType('IP', str)
Path = NewType('IP', str)


# --------        time units        --------
Second = NewType('Second', float)
MilliSecond = NewType('MilliSecond', float)
MicroSecond = NewType('MicroSecond', int)

Hz = NewType('Hz', float)


# --------        spacial units        --------
Meter = NewType('Meter', float)
NanoMeter = NewType('NanoMeter', float)

Number = NewType('Number', float)


# --------        value units        --------
Absorbance = NewType('Absorbance', float)
Digit = NewType('Digit', float)
Electron = NewType('Electron', float)
Percent = NewType('Percent', float)

T = TypeVar('T', Digit, Electron, Percent)
