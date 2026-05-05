import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import serial
import ld2413

PORT = '/dev/ttyUSB0'

ser = serial.Serial(PORT, ld2413.BAUD_RATE, timeout=2)
print(f'Opened {PORT} at {ld2413.BAUD_RATE} baud')

# Read firmware version
ser.flushInput()
if ld2413.enable_configuration(ser):
    version = ld2413.read_firmware_version(ser)
    print(f'Firmware: {version}')
    ld2413.end_configuration(ser)
else:
    print('(Could not read firmware version)')

print('Reading distance — Ctrl+C to stop\n')

try:
    while True:
        frame = ser.read_until(ld2413.REPORT_TAIL)
        distance_mm = ld2413.read_distance(frame)

        if distance_mm is None:
            if len(frame) > 0:
                print(f'[bad frame ({len(frame)} B): {frame.hex(" ")}]')
            continue

        if distance_mm == 0.0:
            print('[out of range or threshold not calibrated — run update_threshold]')
            continue

        print(f'Distance: {distance_mm:8.2f} mm  ({distance_mm / 10:6.2f} cm)')

except KeyboardInterrupt:
    ser.close()
    print('\nSerial port closed.')
