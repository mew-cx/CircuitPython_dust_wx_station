import busio
import time
import board
import atexit
import digitalio
import microcontroller
import wifi
import socketpool
import ipaddress

import neopixel
import adafruit_ds1307
import adafruit_dotstar
import adafruit_htu21d
import adafruit_mpl3115a2
import adafruit_sps30

from secrets import secrets

#############################################################################

# SPS30 limits I2C rate to 100kHz
i2c = busio.I2C(board.SCL, board.SDA, frequency=100_000)

# Create the I2C sensor instances
ds1307  = adafruit_ds1307.DS1307(i2c)
htu21d  = adafruit_htu21d.HTU21D(i2c)
mpl3115 = adafruit_mpl3115a2.MPL3115A2(i2c)
sps30   = adafruit_sps30.i2c(i2c, fp_mode=True)

# dotstar strip on hardware SPI
NUM_DOTS = 4
dots = dotstar.DotStar(board.SCK, board.MOSI, NUM_DOTS, brightness=0.1)

#############################################################################

def InitializeDevices():
    # Turn off I2C VSENSOR to save power
    i2c_power = digitalio.DigitalInOut(board.I2C_POWER)
    i2c_power.switch_to_input()

    # Turn off onboard D13 red LED to save power
    led = digitalio.DigitalInOut(board.LED)
    led.direction = digitalio.Direction.OUTPUT
    led.value = False

    # Turn off onboard NeoPixel to save power
    pixel = neopixel.NeoPixel(board.NEOPIXEL, 1)
    pixel.brightness = 0.0
    pixel.fill((0, 0, 0))
    # TODO disable board.NEOPIXEL_POWER

    # Don't care about altitude, so use Standard Atmosphere [pascals]
    mpl3115.sealevel_pressure = 101325


@atexit.register
def shutdown():
    for dot in range(NUM_DOTS):
        dots[dot] = (0,0,0)

#############################################################################

while True:

    print("htu21d : {:0.3f}C {:0.1f}%RH\nmpl3115 : {0:0.3f}pa {0:0.3f}m {0:0.3f}C".format(
        htu21d.temperature,
        htu21d.relative_humidity,
        mpl3115a2.pressure,
        mpl3115a2.altitude,
        mpl3115a2.temperature
        ))


#############################################################################

# rfc5424_formatter.py
# wx.py
# sps30_simpletest.py

