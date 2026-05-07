import sys

from machine import Pin, SoftSPI

from BusPins import BusPins
import McuBoot
from spiflash import SPIFlash

import time

FLASH_IMAGE_SIZE = 45096
file_name = "FPGA_bitstream_FLASH_MEM.bin"


class FlashBoot:
    bus: SoftSPI
    cs: Pin
    en: Pin
    pwr: Pin
    flash: SPIFlash
    pins: BusPins

    def __init__(self, pins: tuple, cs: Pin, en: Pin, pwr: Pin):
        self.pins = BusPins(*pins)

        # Initialize SPI
        self.bus = SoftSPI(sck=self.pins.sclk,
                           mosi=self.pins.mosi,
                           miso=self.pins.miso)

        self.pwr = pwr
        self.en = en
        self.cs = cs

        self.flash = SPIFlash(self.bus, cs=self.cs)

    def getid(self):
        self.enable_bus()
        time.sleep_ms(1)

        ret = self.flash.getid()
        print([hex(b) for b in ret], file=sys.stderr)

        self.disable_bus()

    def store(self):
        self.wake_flash()
        self.enable_bus()
        self.pwr.low()
        time.sleep_ms(1)

        self.flash.erase(0, "64k")

        try:
            with open(file_name, "rb") as f:
                self.flash.write_block(0, f.read(FLASH_IMAGE_SIZE))


        except OSError as e:
            print(f"Can't open the file: {e}")
        except Exception as e:
            print(f"Error: {e}")

        self.disable_bus()
        self.pwr.high()

    def verify(self):
        self.wake_flash()
        self.enable_bus()
        self.pwr.low()
        time.sleep_ms(1)

        flash_head = bytearray(2560)
        with open(file_name, "rb") as f:
            file_head = f.read(2560)
        self.flash.read_block(0, flash_head)
        print(f"{[(i, p) for i, p in enumerate(zip(file_head, flash_head)) if p[0] != p[1]]}")

        print(f"verify: {all([(bin == fls) for bin, fls in zip(file_head, flash_head)])}")

        self.disable_bus()
        self.pwr.high()

    def load(self, mcuboot: McuBoot.MCUBoot):
        mcuboot.disable_bus()
        self.wake_flash()

        self.disable_bus()
        self.cs.init(Pin.IN, pull=Pin.PULL_UP, value=1)
        time.sleep_ms(10)

        self.en.high()
        self.pwr.low()
        time.sleep_us(1100)
        self.pwr.high()
        time.sleep_us(3)
        self.cs.high()
        time.sleep_us(1100)
        for _ in range(FLASH_IMAGE_SIZE // 100):
            print(".", end="")
            time.sleep_ms(1)
        print(".")

        self.cs.high()
        self.disable_bus()

    def disable_bus(self):
        for pin in self.pins:
            pin.init(Pin.IN, pull=Pin.PULL_UP, value=1)
        self.cs.init(Pin.IN, pull=Pin.PULL_UP, value=1)
        time.sleep_ms(1)

    def enable_bus(self):
        self.enable_cs()
        self.pins.mosi.init(Pin.OPEN_DRAIN, pull=Pin.PULL_UP, value=1)
        self.pins.sclk.init(Pin.OPEN_DRAIN, pull=Pin.PULL_UP, value=1)
        self.bus = SoftSPI(sck=self.pins.sclk,
                           mosi=self.pins.mosi,
                           miso=self.pins.miso)

    def enable_cs(self):
        self.cs.init(Pin.OUT, value=1)
        time.sleep_ms(1)

    def wake_flash(self):
        self.enable_bus()
        self.cs.low()
        self.bus.write(bytearray([0xAB]))
        self.cs.high()
        self.disable_bus()
        time.sleep_ms(1)
