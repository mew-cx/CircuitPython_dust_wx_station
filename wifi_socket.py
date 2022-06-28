# SPDX-FileCopyrightText: 2022 Michael Weiblen http://mew.cx/
#
# SPDX-License-Identifier: MIT

# wifi_socket.py
'''
WIP!!!
This library is a wrapper to encapsulate the wifi and socketpool modules
for the dust weather station.
We only implement IPv4., and don't even attempt IPv6.

'''

import wifi
import socketpool
import ipaddress

__version__ = "0.0.0.0"
__repo__ = "https://github.com/mew-cx/dust_runtime.git"

#############################################################################

class WifiSocket:

    def __init__(self, host, port):
        self._host = host
        self._port = port
        self._socket = None

    def ConnectToAP(self, ssid, password):
        print("connecting to AP", ssid)
        wifi.radio.connect(ssid, password)
        print("wifi.radio.ipv4_address", wifi.radio.ipv4_address)

    def ConnectToSocket(self):
        pool = socketpool.SocketPool(wifi.radio)

        addr_info = pool.getaddrinfo(self._host, self._port)
        print("repr addr_info", repr(addr_info))
        server_ipv4 = ipaddress.ip_address(addr_info[0][4][0])
        print("server_ipv4", server_ipv4)
        print("ping time", wifi.radio.ping(server_ipv4), "ms")

        print("creating socket")
        self._socket = pool.socket(pool.AF_INET, pool.SOCK_STREAM)
        print("self._socket", self._socket)

        print("connecting to socket")
        TIMEOUT = 5
        self._socket.settimeout(TIMEOUT)
        self._socket.connect((self._host, self._port))

    def deinit(self):
        self._socket.close()
        self._socket = None
        # what else goes here? how to release pool and radio?

    @property
    def ipaddr(self):
        return wifi.radio.ipv4_address

    @property
    def socket(self):
        return self._socket

# vim: set sw=4 ts=8 et ic ai:
