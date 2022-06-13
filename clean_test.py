# SPDX-FileCopyrightText: 2021 Kevin J. Walters
# SPDX-License-Identifier: MIT

import time
import board
import busio
from adafruit_sps30.i2c import SPS30_I2C

DELAYS = (1.0, 0.0, 1.0, 0.1)
DEF_READS = len(DELAYS)
PM_PREFIXES = ("pm10", "pm25", "pm40", "pm100")


def some_reads(sps, num=DEF_READS):
    """Read and print out some values from the sensor which could be
    integers or floating-point values."""

    output_header = True
    last_idx = min(len(DELAYS), num) - 1
    for idx in range(last_idx + 1):
        data = sps.read()
        if output_header:
            print("PM1\tPM2.5\tPM4\tPM10")
            output_header = False
        # print(data)
        print("{}\t{}\t{}\t{}".format(*[data[pm + " standard"] for pm in PM_PREFIXES]))
        if idx != last_idx:
            time.sleep(DELAYS[idx])

    # Just for last value
    print("ALL for last read")
    for field in sps.FIELD_NAMES:
        print("{:s}: {}".format(field, data[field]))


i2c = busio.I2C(board.SCL, board.SDA, frequency=100_000)

print("Creating SPS30_I2C defaults")
sps30_int = SPS30_I2C(i2c, fp_mode=False)
fw_ver = sps30_int.firmware_version
print("Firmware int version: {:d}.{:d}".format(fw_ver[0], fw_ver[1]))
del sps30_int

print("Creating SPS30_I2C fp_mode=True")
sps30_fp = SPS30_I2C(i2c, fp_mode=True)
fw_ver = sps30_fp.firmware_version
print("Firmware float version: {:d}.{:d}".format(fw_ver[0], fw_ver[1]))

sps30_fp.start()  # needed to return to "Measurement" mode
print("reads after wakeup and start")
some_reads(sps30_fp)

# data sheet implies this takes 10 seconds but more like 14
print("Fan clean (the speed up is audible)")
sps30_fp.clean(wait=4)
for _ in range(2 * (10 - 4 + 15)):
    cleaning = bool(sps30_fp.read_status_register() & sps30_fp.STATUS_FAN_CLEANING)
    print("c" if cleaning else ".", end="")
    if not cleaning:
        break
    time.sleep(0.5)
print()
print("reads after clean")
some_reads(sps30_fp)

print("END TEST")
