# dust_main.py

import busio
import time
import board
import atexit
import digitalio
#import microcontroller
import wifi
import socketpool
import ipaddress

import neopixel
import adafruit_ds1307
import adafruit_dotstar
import adafruit_htu21d
import adafruit_mpl3115a2
#import adafruit_sps30.i2c
from adafruit_sps30.i2c import SPS30_I2C

from secrets import secrets

#############################################################################

# SPS30 limits I2C rate to 100kHz
i2c = busio.I2C(board.SCL, board.SDA, frequency=100_000)
# I2C addresses found: 0xb, 0x40, 0x60, 0x68, 0x69

# Create the I2C sensor instances
ds1307  = adafruit_ds1307.DS1307(i2c)
htu21d  = adafruit_htu21d.HTU21D(i2c)
mpl3115 = adafruit_mpl3115a2.MPL3115A2(i2c)
#sps30   = adafruit_sps30.i2c(i2c, fp_mode=True)
sps30 = SPS30_I2C(i2c, fp_mode=True)

# dotstar strip on hardware SPI
NUM_DOTS = 4
dots = adafruit_dotstar.DotStar(board.SCK, board.MOSI, NUM_DOTS, brightness=0.1)

#############################################################################
# "The Syslog Protocol" : https://datatracker.ietf.org/doc/html/rfc5424

class Facility:
    "Syslog facilities, Sect 6.2.1"
    KERN, USER, MAIL, DAEMON, AUTH, SYSLOG, LPR, NEWS, UUCP, CRON, \
        AUTHPRIV, FTP = range(0,12)
    LOCAL0, LOCAL1, LOCAL2, LOCAL3, LOCAL4, LOCAL5, LOCAL6, \
        LOCAL7 = range(16, 24)

class Severity:
    "Syslog severities, Sect 6.2.1"
    EMERG, ALERT, CRIT, ERR, WARNING, NOTICE, INFO, DEBUG = range(0,8)

def FormatTimestamp(t):
    "Sect 6.2.3"
    result = "{:04}-{:02}-{:02}T{:02}:{:02}:{:02}Z".format(
        t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec)
    return result

def FormatSyslog(facility = Facility.USER,
                 severity = Severity.NOTICE,
                 timestamp = None,
                 hostname = None,
                 app_name = None,
                 procid = None,
                 msgid = None,
                 structured_data = None,
                 msg = None) :
    "RFC5424 Sect 6.x.x"

    # Sect 6.2: HEADER MUST be ASCII
    # Sect 9.1: RFC5424's VERSION is "1"
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

    print(repr(result))
    return result + b"\n"

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

print("creating socket")
sock = pool.socket(pool.AF_INET, pool.SOCK_STREAM)
sock.settimeout(TIMEOUT)

print("connecting to socket")
sock.connect((HOST, PORT))

#############################################################################
# main

InitializeDevices()

sock.send(FormatSyslog(
    facility = Facility.LOCAL3,
    severity = Severity.INFO,
    timestamp = FormatTimestamp(ds1307.datetime),
    hostname = wifi.radio.ipv4_address,
    app_name = "dust",
    msg = '"timestamp","temp[C]","RH[%]","pres[pa]","tps[um]",' \
          '"1.0um mass[ug/m^3]","2.5um mass[ug/m^3]","4.0um mass[ug/m^3]","10um mass[ug/m^3]",' \
          '"0.5um count[#/cm^3]","1.0um count[#/cm^3]","2.5um count[#/cm^3]","4.0um count[#/cm^3]","10um count[#/cm^3]"'
    ))

while True:
    ts = FormatTimestamp(ds1307.datetime)

    h = "{:0.1f},{:0.1f},{:0.0f},".format(
        htu21d.temperature, htu21d.relative_humidity, mpl3115.pressure)

    try:
        x = sps30.read()
        #print(x)
    except RuntimeError as ex:
        print("Cant read SPS30, skipping: " + str(ex))
        continue

    p1 = "{:0.3f},".format(x["tps"])
    p2 = "{:0.1f},{:0.1f},{:0.1f},{:0.1f},".format(
        x["pm10 standard"], x["pm25 standard"], x["pm40 standard"], x["pm100 standard"])
    p3 = "{:0.0f},{:0.0f},{:0.0f},{:0.0f},{:0.0f}".format(
        x["particles 05um"], x["particles 10um"], x["particles 25um"],
        x["particles 40um"], x["particles 100um"])

    result = ts + "," + h + p1 + p2 + p3

    sent = sock.send(FormatSyslog(
        facility = Facility.LOCAL3,
        severity = Severity.INFO,
        timestamp = ts,
        hostname = wifi.radio.ipv4_address,
        app_name = "dust",
        msg = result
        ))

    time.sleep(60)
