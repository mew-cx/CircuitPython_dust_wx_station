# rfc5424_formatter.py
# https://www.rfc-editor.org/rfc/rfc5424.html

import time
import rtc

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

import wifi
import socketpool
import ipaddress
from secrets import secrets

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
