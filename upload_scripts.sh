#!/bin/bash

set -e

#echo "❌  Deleting old files..."
#ampy -p /dev/ttyUSB0 rm boot.py
#ampy -p /dev/ttyUSB0 rmdir src

#ampy -p /dev/ttyUSB0 reset

echo "⌛  Uploading scripts (this operation may take some time)..."
ampy -p /dev/ttyUSB0 put boot.py boot.py
ampy -p /dev/ttyUSB0 put src src
echo "✅  Scripts uploaded!"
echo "⭕  Please reboot the device manually..."