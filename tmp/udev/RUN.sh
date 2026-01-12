#! /bin/bash -x

lsusb -v >lsusb-v.txt
COLUMNS=125 man udev |cat> man_udev.txt 
COLUMNS=125 man udevadm |cat> man_udevadm.txt 
COLUMNS=125 man udev.conf |cat> man_udev.conf.txt 

udevadm info -a -n /dev/sda1
