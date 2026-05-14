import sys
import time

import machine

from BusPins import BusPins
import McuBoot
import FlashBoot

SPI0_MISO = 0
SPI0_CS = 1
SPI0_SCLK = 2
SPI0_MOSI = 3

LED_PIN = 4

# SPI1_MISO = 8  # V1.0-R0.4
# SPI1_CS = 9  # V1.0-R0.4
# SPI1_SCLK = 10  # V1.0-R0.4
# SPI1_MOSI = 11  # V1.0-R0.4

PWR_PIN = 12
EN_PIN = 13

BUTTON1_PIN = 29
BUTTON2_PIN = 28
BUTTON3_PIN = 27
BUTTON4_PIN = 26

# Settings
MISO0 = machine.Pin(SPI0_MISO, machine.Pin.IN, pull=machine.Pin.PULL_UP, value=1)
CS0 = machine.Pin(SPI0_CS, machine.Pin.OPEN_DRAIN, pull=machine.Pin.PULL_UP, value=1)
SCLK0 = machine.Pin(SPI0_SCLK, machine.Pin.OPEN_DRAIN, pull=machine.Pin.PULL_UP, value=1)
MOSI0 = machine.Pin(SPI0_MOSI, machine.Pin.OPEN_DRAIN, pull=machine.Pin.PULL_UP, value=1)

LED = machine.Pin(LED_PIN, machine.Pin.OUT)

# MISO1 = machine.Pin(SPI1_MISO, machine.Pin.IN, pull=machine.Pin.PULL_UP, value=1)  # V1.0-R0.4
# CS1 = machine.Pin(SPI1_CS, machine.Pin.OPEN_DRAIN, pull=machine.Pin.PULL_UP, value=1)  # V1.0-R0.4
# SCLK1 = machine.Pin(SPI1_SCLK, machine.Pin.OPEN_DRAIN, pull=machine.Pin.PULL_UP, value=1)  # V1.0-R0.4
# MOSI1 = machine.Pin(SPI1_MOSI, machine.Pin.OPEN_DRAIN, pull=machine.Pin.PULL_UP, value=1)  # V1.0-R0.4

PWR = machine.Pin(PWR_PIN, machine.Pin.OUT, value=0)
EN = machine.Pin(EN_PIN, machine.Pin.OUT, value=0)

BUTTON1 = machine.Pin(BUTTON1_PIN, machine.Pin.IN, pull=machine.Pin.PULL_UP, value=1)
BUTTON2 = machine.Pin(BUTTON2_PIN, machine.Pin.IN, pull=machine.Pin.PULL_UP, value=1)
BUTTON3 = machine.Pin(BUTTON3_PIN, machine.Pin.IN, pull=machine.Pin.PULL_UP, value=1)
BUTTON4 = machine.Pin(BUTTON4_PIN, machine.Pin.IN, pull=machine.Pin.PULL_UP, value=1)

mcuboot = McuBoot.McuBoot(BusPins(SCLK0, MOSI0, MISO0), CS0, EN, PWR, LED)
# flashboot = FlashBoot.FlashBoot(BusPins(SCLK1, MOSI1, MISO1), CS1, EN, PWR)  # V1.0-R0.4
flashboot = FlashBoot.FlashBoot(BusPins(SCLK0, MISO0, MOSI0), CS0, EN, PWR)  # V1.0-R0.5

while True:
    print(".", end="", file=sys.stderr)
    if BUTTON1.value() == 0:
        mcuboot.load(flashboot)
    elif BUTTON2.value() == 0:
        flashboot.load(mcuboot)
    elif BUTTON3.value() == 0:
        mcuboot.disable_bus()
        flashboot.store()
    elif BUTTON4.value() == 0:
        mcuboot.disable_bus()
        flashboot.verify()
    time.sleep_ms(100)
