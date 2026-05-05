import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import time
import serial
import serial_protocol

PORT = '/dev/ttyUSB0'
WARMUP_SECONDS = 10

print('HLK-LD2413 Threshold Calibration')
print('=' * 40)
print('This calibrates the sensor\'s near-field noise (antenna + housing).')
print('Point the sensor at open sky or an empty corner of a room —')
print('do NOT point it into the tank (the tank bottom should remain a valid target).\n')
input('Position the sensor, then press Enter...')

ser = serial.Serial(PORT, serial_protocol.BAUD_RATE, timeout=2)
ser.flushInput()

print(f'\nMeasuring background noise for {WARMUP_SECONDS} seconds...')
deadline = time.time() + WARMUP_SECONDS
while time.time() < deadline:
    ser.read_until(serial_protocol.REPORT_TAIL)
    remaining = deadline - time.time()
    print(f'  {remaining:.0f}s remaining  ', end='\r')

print('\nSaving threshold...')
if not serial_protocol.enable_configuration(ser):
    print('Error: could not enter configuration mode.')
    ser.close()
    sys.exit(1)

if serial_protocol.update_threshold(ser):
    print('Threshold updated successfully.')
else:
    print('Error: update_threshold failed.')

serial_protocol.end_configuration(ser)
ser.close()
print('Done. You can now run print_distance.py.')
