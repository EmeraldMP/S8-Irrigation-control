#!/bin/bash

while :
do
	if ! pgrep -x "par_sensor" > /dev/null
	then
		gnome-terminal -- python3 /home/pi/Data_collect/FB/Rpi_to_arduino.py
		sleep 10
	fi
	
done
