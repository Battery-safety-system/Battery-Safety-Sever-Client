#!/bin/sh
# This is a comment!
echo Start the Program	# This is a comment, too!
sudo modprobe pcan
sudo ip link set can0 up type can bitrate 500000
python3 client-version5.py