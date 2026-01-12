#! /bin/bash

UDEVINFO="udevadm info --attribute-walk"

DEVICES="/dev/sda1 /dev/ttyACM0"

echo $DEVICES
echo ""

for i in $DEVICES
do
	CMD="$UDEVINFO $i"
	echo "==========================="
	echo "CMD = $CMD"
	echo "==========================="
	$CMD | cat
	echo ""
done


