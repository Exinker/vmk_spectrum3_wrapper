from typing import NewType, TypeAlias, TypeVar

from numpy.typing import NDArray


# --------        structures        --------
Array: TypeAlias = NDArray


# --------        temperature units        --------
Kelvin = NewType('Kelvin', float)
Celsius = NewType('Celsius', float)


# --------        time units        --------
Second = NewType('Second', float)
MilliSecond = NewType('MilliSecond', float)
MicroSecond = NewType('MicroSecond', int)

Hz = NewType('Hz', float)

# --------        spacial units        --------
Inch = NewType('Inch', float)

Meter = NewType('Meter', float)
CentiMeter = NewType('CentiMeter', float)
MilliMeter = NewType('MilliMeter', float)
MicroMeter = NewType('MicroMeter', float)
NanoMeter = NewType('NanoMeter', float)
PicoMeter = NewType('Pico', float)

Number = NewType('Number', float)


# --------        value units        --------
Absorbance = NewType('Absorbance', float)
A: TypeAlias = Absorbance

Digit = NewType('Digit', float)
Electron = NewType('Electron', float)
Percent = NewType('Percent', float)
U = TypeVar('U', Digit, Electron, Percent)


# --------        other units        --------
IP = NewType('IP', str)
Path = NewType('IP', str)
