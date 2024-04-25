from typing import NewType

from .filter import AbstractFilter


F = NewType('F', AbstractFilter)
