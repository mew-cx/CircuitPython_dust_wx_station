# SPDX-FileCopyrightText: 2022 Michael Weiblen http://mew.cx/
#
# SPDX-License-Identifier: MIT

# wifi_socket.py  (TODO: a better name?)
# TODO need exceptions
'''
WIP!!!  WIP!!!
This library is a wrapper to encapsulate the wifi and socketpool modules
for the dust weather station.
We only implement IPv4.

'''

import wifi
import socketpool
import ipaddress

__version__ = "0.0.0.0"
__repo__ = "https://github.com/mew-cx/dust_runtime.git"

#############################################################################

def ConnectToAP(self, ssid, password, timeout=5):
    print("connecting to AP", ssid)
    wifi.radio.connect(ssid, password)
    return wifi.radio.ipv4_address

def ConnectToSocket(self, host, port):
    pool = socketpool.SocketPool(wifi.radio)
    print("repr(pool)", pool)

    #addr_info = pool.getaddrinfo(host, port)
    #print("repr addr_info", repr(addr_info))
    #server_ipv4 = ipaddress.ip_address(addr_info[0][4][0])
    #print("server_ipv4", server_ipv4, "(server)")
    #print("ping server_ipv4:", wifi.radio.ping(server_ipv4), "ms")

    print("creating socket")
    sock = pool.socket(pool.AF_INET, pool.SOCK_STREAM)
    print("repr(sock)", sock)

    print("connecting to socket")
    sock.settimeout(timeout)
    sock.connect((host, port))
    return sock

# vim: set sw=4 ts=8 et ic ai:
