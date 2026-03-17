#!/bin/bash
# entrypoint.sh

# Wait until the RTL-SDR device exists
echo "Waiting for RTL-SDR device..."
while [ ! -e /dev/bus/usb ]; do
    sleep 1
done

# Optional: wait a few more seconds for device to be fully initialized
sleep 3

echo "Starting dump1090..."
exec ./dump1090 --interactive --net --net-ro-port 30002

