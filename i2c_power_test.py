# i2c_power_test.py - test fesp32 VSENSOR control
# https://learn.adafruit.com/adafruit-esp32-s2-feather/i2c-power-management

import time
import board
import digitalio
import neopixel

i2c_power = digitalio.DigitalInOut(board.I2C_POWER)

pixel = neopixel.NeoPixel(board.NEOPIXEL, 1)
pixel.brightness = 0.3
pixel.fill((255, 0, 0))

i2c_power.switch_to_input()
time.sleep(0.1)  # allow signal to settle
default_value = i2c_power.value
print("DISABLE value:", default_value)
time.sleep(1)

pixel.fill((0, 255, 0))

i2c_power.switch_to_output(value=(not default_value))
print("ENABLE value:", i2c_power.value)
time.sleep(1)

pixel.fill((0, 0, 0))
