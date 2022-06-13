# mew 2022-02-27

# Derived from:
# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-FileCopyrightText: 2021 Kevin J. Walters
# SPDX-License-Identifier: MIT

import time
import board
import microcontroller
import busio
from adafruit_ds1307 import DS1307
from adafruit_mpl3115a2 import MPL3115A2
from adafruit_htu21d import HTU21D
from adafruit_sps30.i2c import SPS30_I2C

# SPS30 works up to 100kHz
#i2c = board.I2C()
i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)
rtc = DS1307(i2c)
htu21d = HTU21D(i2c)
mpl3115 = MPL3115A2(i2c)
sps30 = SPS30_I2C(i2c, fp_mode=True)

daynames = ("Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat")

# You can configure the pressure at sealevel to get better altitude estimates.
# This value has to be looked up from your local weather forecast or meteorological
# reports.  It will change day by day and even hour by hour with weather
# changes.  Remember altitude estimation from barometric pressure is not exact!
# Set this to a value in pascals:
mpl3115.sealevel_pressure = 102250

while True:
    print("CPU: %0.3f C" % microcontroller.cpu.temperature)

    t = rtc.datetime
    # print(t)     # for debug
    wday = daynames[int(t.tm_wday)]
    print("DS1307: {} {}-{:02}-{:02} {:02}:{:02}:{:02}".format(
        wday, t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec)
    )

    print("HTU21D: %0.1f C, %0.1f %%RH" % (
        htu21d.temperature, htu21d.relative_humidity))

    print("MPL3115: %0.3f pas, %0.3f m, %0.3f C" % (
        mpl3115.pressure, mpl3115.altitude, mpl3115.temperature))

    try:
        aqdata = sps30.read()
        print(aqdata)
    except RuntimeError as ex:
        print("Cant read from sensor, retrying..." + str(ex))
        continue

    print("Concentration Units (standard):")
    print("\tPM 1.0: {}\tPM2.5: {}\tPM10: {}".format(
            aqdata["pm10 standard"], aqdata["pm25 standard"], aqdata["pm100 standard"]
        )
    )
    print("Concentration Units (number count):")
    print("\t0.3-0.5um  / cm3:", aqdata["particles 05um"])
    print("\t0.3-1.0um  / cm3:", aqdata["particles 10um"])
    print("\t0.3-2.5um  / cm3:", aqdata["particles 25um"])
    print("\t0.3-4.0um  / cm3:", aqdata["particles 40um"])
    print("\t0.3-10.0um / cm3:", aqdata["particles 100um"])
    print()

    time.sleep(300)

