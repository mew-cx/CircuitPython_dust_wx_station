#! /bin/bash

DEVICES="/dev/sda1 /dev/ttyACM0"

echo $DEVICES
echo ""

for i in $DEVICES
do
	CMD="udevadm info --attribute-walk $i"
	echo "==========================="
	echo "CMD = $CMD"
	echo "==========================="
	$CMD | cat
	echo ""

	CMD="udevadm info --query=all $i"
	echo "==========================="
	echo "CMD = $CMD"
	echo "==========================="
	$CMD | cat
	echo ""
done
