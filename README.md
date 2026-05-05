# hlk-ld2413-reader

Python driver for the **HLK-LD2413** — a 24 GHz FMCW millimeter-wave radar sensor for high-precision liquid and material level detection (range 0.15–10 m, accuracy ±3 mm).

## Files

| File | Description |
|------|-------------|
| `ld2413.py` | Protocol library — frame parsing and all serial commands |
| `print_distance.py` | Read and print live distance measurements |
| `calibrate.py` | One-time background noise calibration (run before first use) |

## Requirements

- Python 3.10+
- `pyserial`

```
pip install -r requirements.txt
```

## Wiring

Connect via USB-to-TTL adapter (3.3 V logic):

| Sensor pin | Adapter pin |
|------------|-------------|
| OT1 (TX)   | RXD         |
| RX         | TXD         |
| GND        | GND         |
| 3V3        | VCCIO       |

Default serial port: `/dev/ttyUSB0` — adjust `PORT` in the scripts if needed.

## Quick start

**First use — calibrate background noise:**
```
python3 calibrate.py
```
Point the sensor at open sky or an empty room corner (not into the tank).
The calibration removes near-field antenna noise and housing reflections.
The tank bottom remains a valid target and is not affected.

**Read live distance:**
```
python3 print_distance.py
```

## Protocol

- Baud rate: 115200, 8N1
- Report frame: `F4 F3 F2 F1 | 04 00 | <float32 LE, mm> | F8 F7 F6 F5` (14 bytes)
- Command frame: `FD FC FB FA | <len 2B> | <cmd 2B> | <value NB> | 04 03 02 01`

## Available library functions

```python
read_distance(frame)              # parse report frame → float mm or None
enable_configuration(ser)         # enter config mode (required before commands)
end_configuration(ser)            # exit config mode, resume reporting
read_firmware_version(ser)        # → "V1.4.14"
set_min_distance(ser, mm)         # 150–10500 mm
set_max_distance(ser, mm)         # 150–10500 mm
set_reporting_cycle(ser, ms)      # 50–1000 ms
read_reporting_cycle(ser)         # → int ms
update_threshold(ser)             # save background noise calibration
```

## Configuring the sensor

Configuration changes are written to the sensor's flash and survive power cycles — you only need to run this once.

```python
import serial, ld2413

ser = serial.Serial('/dev/ttyUSB0', ld2413.BAUD_RATE, timeout=2)
ser.flushInput()

ld2413.enable_configuration(ser)

ld2413.set_min_distance(ser, 150)    # minimum detection distance in mm (150–10500)
ld2413.set_max_distance(ser, 5000)   # maximum detection distance in mm (150–10500)
ld2413.set_reporting_cycle(ser, 160) # reporting interval in ms (50–1000)

ld2413.end_configuration(ser)
ser.close()
```

Always call `enable_configuration` first and `end_configuration` when done — otherwise the sensor stays in config mode and stops reporting.

## Notes

- If the sensor always reports 0: run `calibrate.py` first (threshold not set).
- Measuring through a plastic tank lid works for most non-metallic plastics.
- Minimum detection distance: 150 mm.
- The sensor retains calibration across power cycles.
- Manufacturer resources (datasheet, host tool, firmware): [Hi-Link Google Drive](https://drive.google.com/drive/folders/1gT_a3_ARDGK7ZcbRR1IHGniUm5Zb9XuW)
