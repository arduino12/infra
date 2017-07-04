#!/bin/bash

DEV_MAC="98:D3:31:90:30:3A"
inside=1

detected()
{
	# hcitool rssi $DEV_MAC &>/dev/null
	touch /dev/rfcomm0
	ret=$?

	if [ $ret -ne 0 ]; then
		sudo rfcomm connect 0 $DEV_MAC &
		sleep 10
		hcitool rssi $DEV_MAC &>/dev/null
		ret=$?
	fi;
	# if [ $ret -ne 0 ]; then
		# sudo rfcomm release 0
		# sleep 1
	# fi;
	if [ $ret -eq 0 ] && [ $inside -eq 1 ]; then
		inside=0
		echo "connected"
	elif [ $ret -eq 1 ] && [ $inside -eq 0 ]; then
		inside=1
		echo "not connected"
	fi;
}

while :; do
	detected
done
