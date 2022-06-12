# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import time
import board
import adafruit_ds1307

i2c = board.I2C()
rtc = adafruit_ds1307.DS1307(i2c)

def DayOfWeek(wday):
    # https://docs.python.org/3/library/time.html#time.struct_time
    # describes tm_wday as "range [0, 6], Monday is 0"
    return ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")[wday]

if False:
    # you must set year, mon, date, hour, min, sec and weekday
    # yearday is not supported, isdst can be set but we don't do anything with it at this time
    #                     year, mon, date, hour, min, sec, wday, yday, isdst
    t = time.struct_time((2017, 10, 29, 15, 14, 15, 0, -1, -1))
    print("Setting time to:", t)
    rtc.datetime = t

while True:
    t = rtc.datetime
    print("{} {}-{:02}-{:02}T{:02}:{:02}:{:02}Z".format(
        DayOfWeek(t.tm_wday),
        t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec))
    time.sleep(1.5)
