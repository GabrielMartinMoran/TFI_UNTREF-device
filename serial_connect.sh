#!/bin/bash
echo "⌛  Connecting to device via serial..."

picocom /dev/ttyUSB0 -b115200