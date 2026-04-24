import machine

import McuBoot
import FlashBoot

SPI0_MISO = 0
SPI0_CS = 1
SPI0_SCLK = 2
SPI0_MOSI = 3

LED_PIN = 4

SPI1_MISO = 8
SPI1_CS = 9
SPI1_SCLK = 10
SPI1_MOSI = 11

PWR_PIN = 12
EN_PIN = 13

# Settings
MISO0 = machine.Pin(SPI0_MISO, machine.Pin.IN, pull=machine.Pin.PULL_UP, value=1)
CS0 = machine.Pin(SPI0_CS, machine.Pin.OPEN_DRAIN, pull=machine.Pin.PULL_UP, value=1)
SCLK0 = machine.Pin(SPI0_SCLK, machine.Pin.OPEN_DRAIN, pull=machine.Pin.PULL_UP, value=1)
MOSI0 = machine.Pin(SPI0_MOSI, machine.Pin.OPEN_DRAIN, pull=machine.Pin.PULL_UP, value=1)

LED = machine.Pin(LED_PIN, machine.Pin.OUT)

MISO1 = machine.Pin(SPI1_MISO, machine.Pin.IN, pull=machine.Pin.PULL_UP, value=1)
CS1 = machine.Pin(SPI1_CS, machine.Pin.OPEN_DRAIN, pull=machine.Pin.PULL_UP, value=1)
SCLK1 = machine.Pin(SPI1_SCLK, machine.Pin.OPEN_DRAIN, pull=machine.Pin.PULL_UP, value=1)
MOSI1 = machine.Pin(SPI1_MOSI, machine.Pin.OPEN_DRAIN, pull=machine.Pin.PULL_UP, value=1)

PWR = machine.Pin(PWR_PIN, machine.Pin.OUT, value=0)
EN = machine.Pin(EN_PIN, machine.Pin.OUT, value=0)

# Initialize SPI


mcuboot = McuBoot.McuBoot((SCLK0, MOSI0, MISO0), CS0, EN, PWR, LED)
flashboot = FlashBoot.FlashBoot((SCLK1, MOSI1, MISO1), CS1, EN, PWR)
mcuboot.disable_bus()
flashboot.disable_bus()
