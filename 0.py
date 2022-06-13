import time
import board
import atexit
import digitalio
import adafruit_ds1307


import adafruit_dotstar as dotstar

from adafruit_htu21d import HTU21D



import neopixel

import adafruit_mpl3115a2


import wifi
import socketpool
import ipaddress
from secrets import secrets


import busio
from adafruit_sps30.i2c import SPS30_I2C

import busio
from adafruit_sps30.i2c import SPS30_I2C







import microcontroller
import busio
from adafruit_ds1307 import DS1307
from adafruit_mpl3115a2 import MPL3115A2
from adafruit_htu21d import HTU21D
from adafruit_sps30.i2c import SPS30_I2C


# SPS30 limits I2C rate to 100kHz
i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)

# Create the I2C devices
ds1307 = adafruit_ds1307.DS1307(i2c)
htu21d = HTU21D(i2c)
mpl3115 = MPL3115A2(i2c)
sps30 = SPS30_I2C(i2c, fp_mode=True)




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
# TODO board.NEOPIXEL_POWER




::::::::::::::
blink.py
::::::::::::::
# SPDX-FileCopyrightText: 2021 Kattni Rembor for Adafruit Industries
# SPDX-License-Identifier: MIT
"""CircuitPython Blink Example - the CircuitPython 'Hello, World!'"""

::::::::::::::
ds1307_simpletest.py
::::::::::::::

::::::::::::::
dust_dotstar.py
::::::::::::::
# dust_dotstar.py -- http://mew.cx/ 2022-06-04
# SPDX-FileCopyrightText: 2022 Mike Weiblen

# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

# dotstar strip on hardware SPI
dots = dotstar.DotStar(board.SCK, board.MOSI, 4, brightness=0.1)
n_dots = len(dots)

@atexit.register
def clear():
    for dot in range(n_dots):
        dots[dot] = (0,0,0)

while True:
    for dot in range(n_dots):
        dots[dot] = (r, g, b)

    time.sleep(0.25)
::::::::::::::
htu21d_simpletest.py
::::::::::::::
# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT


# Create sensor object, communicating over the board's default I2C bus
i2c = board.I2C()  # uses board.SCL and board.SDA
sensor = HTU21D(i2c)


while True:
    print("\nTemperature: %0.1f C" % sensor.temperature)
    print("Humidity: %0.1f %%" % sensor.relative_humidity)
    time.sleep(2)

::::::::::::::
mpl3115a2_simpletest.py
::::::::::::::
# Initialize the MPL3115A2.
sensor = adafruit_mpl3115a2.MPL3115A2(i2c)
# Alternatively you can specify a different I2C address for the device:
# sensor = adafruit_mpl3115a2.MPL3115A2(i2c, address=0x10)

# You can configure the pressure at sealevel to get better altitude estimates.
# This value has to be looked up from your local weather forecast or meteorological
# reports.  It will change day by day and even hour by hour with weather
# changes.  Remember altitude estimation from barometric pressure is not exact!
# Set this to a value in pascals:
sensor.sealevel_pressure = 102250

# Main loop to read the sensor values and print them every second.
while True:
    pressure = sensor.pressure
    print("Pressure: {0:0.3f} pascals".format(pressure))
    altitude = sensor.altitude
    print("Altitude: {0:0.3f} meters".format(altitude))
    temperature = sensor.temperature
    print("Temperature: {0:0.3f} degrees Celsius".format(temperature))
    time.sleep(1.0)
::::::::::::::
rfc5424_formatter.py
::::::::::::::
# rfc5424_formatter.py
# https://www.rfc-editor.org/rfc/rfc5424.html


__version__ = "0.0.0"
__repo__ = "https://github.com/mew-cx/CircuitPython_logger_rfc5424"

class Facility:
    "Syslog facilities, RFC5424 section 6.2.1"
    KERN, USER, MAIL, DAEMON, AUTH, SYSLOG, LPR, NEWS, UUCP, CRON, \
        AUTHPRIV, FTP = range(0,12)
    LOCAL0, LOCAL1, LOCAL2, LOCAL3, LOCAL4, LOCAL5, LOCAL6, \
        LOCAL7 = range(16, 24)

class Severity:
    "Syslog severities, RFC5424 section 6.2.1"
    EMERG, ALERT, CRIT, ERR, WARNING, NOTICE, INFO, DEBUG = range(0,8)

def FormatTimestamp(t):
    "RFC5424 section 6.2.3"
    result = "{:04}-{:02}-{:02}T{:02}:{:02}:{:02}Z".format(
        t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec)
    return result

def FormatRFC5424(facility = Facility.USER,
                  severity = Severity.NOTICE,
                  timestamp = None,
                  hostname = None,
                  app_name = None,
                  procid = None,
                  msgid = None,
                  structured_data = None,
                  msg = None) :
    "RFC5424 section 6"

    # Sect 9.1: RFC5424's VERSION is "1"
    # Sect 6.2: HEADER MUST be ASCII
    header = "<{}>1 {} {} {} {} {} ".format(
        (facility << 3) + severity,
        timestamp or "-",
        hostname or "-",
        app_name or "-",
        procid or "-",
        msgid or "-")
    result = header.encode("ascii")

    # Sect 6.3: STRUCTURED-DATA has complicated encoding requirements,
    # so we require it to already be properly encoded.
    if not structured_data:
        structured_data = b"-"
    result += structured_data

    # Sect 6.4: # MSG SHOULD be UTF-8, but MAY be other encoding.
    # If using UTF-8, MSG MUST start with Unicode BOM.
    # Sect 6 ABNF: MSG is optional.
    #enc = "utf-8-sig"
    enc = "ascii"       # we're using ASCII
    if msg:
        result += b" " + msg.encode(enc)

    #print(repr(result))
    return result

#############################################################################

HOST = "pink"
PORT = 514
TIMEOUT = 5  #None

print("connecting to AP", secrets["ssid"])
wifi.radio.connect(secrets["ssid"], secrets["password"])
print("my ipaddr", wifi.radio.ipv4_address)

pool = socketpool.SocketPool(wifi.radio)
server_ipv4 = ipaddress.ip_address(pool.getaddrinfo(HOST, PORT)[0][4][0])
print("server ipaddr", server_ipv4)
print("ping time", wifi.radio.ping(server_ipv4), "ms")

with pool.socket(pool.AF_INET, pool.SOCK_STREAM) as s:
    print("creating socket")
    s = pool.socket(pool.AF_INET, pool.SOCK_STREAM)
    s.settimeout(TIMEOUT)
    print("connecting to socket")
    s.connect((HOST, PORT))

    sent = s.send(FormatRFC5424(
        facility = Facility.LOCAL3,
        severity = Severity.INFO,
        timestamp = FormatTimestamp(time.localtime()),
        hostname = wifi.radio.ipv4_address,
        app_name = "dust",
        procid = "procID",
        msgid = "msgID",
        msg = "rtc "+ FormatTimestamp(time.localtime())
        ))
    print("sent length : %d" % sent)
::::::::::::::
secrets.py
::::::::::::::
::::::::::::::
sps30_simpletest.py
::::::::::::::
# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-FileCopyrightText: 2021 Kevin J. Walters
# SPDX-License-Identifier: MIT

"""
Example program for Sensirion SPS30 using i2c.

Reminder: SPS30 interface select pin needs to be connected to ground for i2c mode.
"""

# SPS30 works up to 100kHz
i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)
sps30 = SPS30_I2C(i2c, fp_mode=False)

print("Found SPS30 sensor, reading data...")

while True:
    time.sleep(1)

    try:
        aqdata = sps30.read()
        # print(aqdata)
    except RuntimeError as ex:
        print("Unable to read from sensor, retrying..." + str(ex))
        continue

    print()
    print("Concentration Units (standard)")
    print("---------------------------------------")
    print(
        "PM 1.0: {}\tPM2.5: {}\tPM10: {}".format(
            aqdata["pm10 standard"], aqdata["pm25 standard"], aqdata["pm100 standard"]
        )
    )
    print("Concentration Units (number count)")
    print("---------------------------------------")
    print("Particles 0.3-0.5um  / cm3:", aqdata["particles 05um"])
    print("Particles 0.3-1.0um  / cm3:", aqdata["particles 10um"])
    print("Particles 0.3-2.5um  / cm3:", aqdata["particles 25um"])
    print("Particles 0.3-4.0um  / cm3:", aqdata["particles 40um"])
    print("Particles 0.3-10.0um / cm3:", aqdata["particles 100um"])
    print("---------------------------------------")
::::::::::::::
sps30_test.py
::::::::::::::
# SPDX-FileCopyrightText: 2021 Kevin J. Walters
# SPDX-License-Identifier: MIT

"""
Test program for Sensirion SPS30 device putting it through its paces using i2c.

SPS30 running 2.2 firmware appears to take around one second to change into the
requested mode for data type. Any read in that time will be in the previous format
causing bad data or CRC errors!

Reminder: SPS30 interface select pin needs to be connected to ground for i2c mode.
"""

DELAYS = (5.0, 2.0, 1.0, 0.1, 0.0, 0.0)
DEF_READS = len(DELAYS)
PM_PREFIXES = ("pm10", "pm25", "pm40", "pm100")
TEST_VERSION = "1.2"


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


print()
print("Reminder: tps units are different between integer and floating-point modes")
# Bogus data / bogus CRC errors for around one second after mode change are
# inhibited by default mode_change_delay=1.5 in SPS30_I2C constructor
# measured at 0.98 seconds, 1.5 is more conservative value
print()

# To allow a human to grab the serial console
# after a power up to capture the data
print("Sleeping for 20 seconds")
time.sleep(20)

# SPS30 works up to 100kHz
print("BEGIN TEST sps30_test version", TEST_VERSION)
i2c = busio.I2C(board.SCL, board.SDA, frequency=100_000)
print("Creating SPS30_I2C defaults")
sps30_int = SPS30_I2C(i2c, fp_mode=False)
fw_ver = sps30_int.firmware_version
print("Firmware version: {:d}.{:d}".format(fw_ver[0], fw_ver[1]))
print("Six reads in integer mode")
some_reads(sps30_int)
del sps30_int


print("Creating SPS30_I2C fp_mode=True")
sps30_fp = SPS30_I2C(i2c, fp_mode=True)
print("Six reads in default floating-point mode")

start_t = time.monotonic()
readstart_t = start_t
fails = 0
exception = None
for attempts in range(30):
    try:
        readstart_t = time.monotonic()
        some_reads(sps30_fp)
        break
    except RuntimeError as ex:
        exception = ex
        fails += 1
    time.sleep(0.050)
if fails:
    print("Number of exceptions:", fails)
    print("Last exception:", repr(exception))
    print("Time to good read:", readstart_t - start_t)

print("Stop and wait 10 seconds")
sps30_fp.stop()
print("Start and wait for data to become available")
sps30_fp.start()
start_t = time.monotonic()
while True:
    now_t = time.monotonic()
    got_data = sps30_fp.data_available
    if got_data or now_t - start_t > 30.0:
        break
print("Time since start: ", now_t - start_t)
print("Data available:", got_data)
print("Six more reads")
some_reads(sps30_fp)

print("Reset (goes to idle mode)")
sps30_fp.reset()
print("Start")
sps30_fp.start()
print("Six reads after reset+start")
some_reads(sps30_fp)

print("Stop / Sleep / 10 second pause / Wake-up / Start")
sps30_fp.stop()
sps30_fp.sleep()
time.sleep(5)
got_data = False
try:
    got_data = sps30_fp.data_available
    if got_data:
        print("Data available during sleep mode: BAD BAD BAD!")
except OSError:
    # this seems to happen in sleep mode
    # OSError: [Errno 19] Unsupported operation
    pass
time.sleep(5)
sps30_fp.wakeup()  # transitions back to "Idle" mode
sps30_fp.start()  # needed to return to "Measurement" mode
print("Six reads after wakeup and start")
some_reads(sps30_fp)
print("Six more reads after wakeup and start")
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
print("Six reads after clean")
some_reads(sps30_fp)

print("END TEST")
time.sleep(6)
::::::::::::::
wx.py
::::::::::::::
# mew 2022-02-27

# Derived from:
# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-FileCopyrightText: 2021 Kevin J. Walters
# SPDX-License-Identifier: MIT

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

