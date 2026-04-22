# Engineer - Deepak Sharda - dshardam007@gmail.com
import sys
from collections import namedtuple
from machine import Pin, SPI
import time
import binascii

import FlashBoot

file_name = 'FPGA_bitstream_MCU.bin'


class BusPins(namedtuple("BusPins", [
    "sclk",  # Pin
    "mosi",  # Pin
    "miso"  # Pin
])):
    """
    - sclk: `Pin`
    - mosi: `Pin`
    - miso: `Pin`
    """


class McuBoot:
    bus: SPI
    cs: Pin
    led: Pin
    en: Pin
    pwr: Pin
    pins: tuple

    def __init__(self, pins: tuple, cs: Pin, en: Pin, pwr: Pin, led: Pin):
        self.pins = BusPins(*pins)

        self.bus = SPI(0,
                       sck=self.pins.sclk,
                       mosi=self.pins.mosi,
                       miso=self.pins.miso)
        self.cs = cs
        self.led = led
        self.en = en
        self.pwr = pwr

        self.led.off()
        self.cs.on()

    def disable_bus(self):
        for pin in self.pins:
            pin.init(Pin.IN)
        self.cs.init(Pin.IN, pull=Pin.PULL_UP, value=1)

    def enable_bus(self):
        self.cs.init(Pin.OUT, value=1)
        self.bus = SPI(0,
                       sck=self.pins.sclk,
                       mosi=self.pins.mosi,
                       miso=self.pins.miso)

    def send_bitstream_file(self, word_size=4):
        try:
            with open(file_name, 'rb') as f:
                while True:
                    self.led.toggle()
                    # Read 4 bytes per line
                    word = f.read(word_size)
                    if not word:
                        break

                    hex_word = binascii.hexlify(word).decode('utf-8')
                    print(f"Send word: {hex_word}", file=sys.stderr)
                    self.bus.write(word)
                    time.sleep_us(1)


        except OSError as e:
            print(f"Can't open the file: {e}", file=sys.stderr)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)

    def load(self, flashboot: FlashBoot.FlashBoot):

        print("Starting uploading bitstream:", file=sys.stderr)
        flashboot.disable_bus()
        self.enable_bus()
        time.sleep_ms(1)

        self.led.off()
        time.sleep_ms(1)

        self.cs.low()
        self.en.low()
        self.pwr.low()
        time.sleep_ms(10)

        self.en.high()
        self.pwr.high()
        time.sleep_us(3200)

        self.cs.high()
        time.sleep_us(10)

        self.cs.low()
        while self.pins.miso.value() == 1:
            time.sleep_us(1)
        self.send_bitstream_file()

        time.sleep_us(100)

        self.cs.high()

        self.led.low()

        print("Finished uploading bitstream", file=sys.stderr)

        self.disable_bus()
