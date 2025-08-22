import os

from dotenv import load_dotenv

from vmk_spectrum3_wrapper.adc import ADC
from vmk_spectrum3_wrapper.detector import Detector
from vmk_spectrum3_wrapper.types import MilliSecond


load_dotenv(os.path.join('.', '.env'), verbose=True)


def load_default_adc(default: ADC = ADC._16bit) -> ADC:

    name = os.getenv('DEFAULT_ADC')
    if name is None:
        return default

    valid_adc = {
        '16': ADC._16bit,
        '18': ADC._18bit,
    }
    try:
        adc = valid_adc[name]
    except KeyError:
        print('ADC: {name} is not supported yet! Use one of the following: {valid}'.format(
            name=repr(name),
            valid=', '.join(repr(key) for key in valid_adc),
        ))
        return default
    else:
        return adc


def load_default_detector(default: Detector = Detector.BLPP2000) -> Detector:

    name = os.getenv('DEFAULT_DETECTOR')
    if name is None:
        return default

    try:
        detector = Detector[name]
    except KeyError:
        print('Detector: {name} is not supported yet! Use one of the following: {valid}'.format(
            name=repr(name),
            valid=', '.join(repr(detector.name) for detector in Detector),
        ))
        return default
    else:
        return detector


def load_change_exposure_timeout(default: MilliSecond = 1000) -> MilliSecond:

    value = os.getenv('CHANGE_EXPOSURE_TIMEOUT')
    if value is None:
        return default

    try:
        timeout = int(value)
    except TypeError:
        print('CHANGE_EXPOSURE_TIMEOUT is integer time in ms.')
        return default
    else:
        return timeout


LOGGING_LEVEL = os.getenv('LOGGING_LEVEL') or 'INFO'

DEFAULT_ADC = load_default_adc()
DEFAULT_DETECTOR = load_default_detector()
CHANGE_EXPOSURE_TIMEOUT = load_change_exposure_timeout()
