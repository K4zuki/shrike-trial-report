from collections import namedtuple
from machine import Pin


class BusPins(namedtuple("BusPins", [
    "sclk",  # type: Pin
    "mosi",  # type: Pin
    "miso"  # type: Pin
])):
    """
    - sclk: `Pin`
    - mosi: `Pin`
    - miso: `Pin`
    """
