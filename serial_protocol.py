import serial
import struct

BAUD_RATE = 115200

REPORT_HEADER  = bytes([0xF4, 0xF3, 0xF2, 0xF1])
REPORT_TAIL    = bytes([0xF8, 0xF7, 0xF6, 0xF5])
COMMAND_HEADER = bytes([0xFD, 0xFC, 0xFB, 0xFA])
COMMAND_TAIL   = bytes([0x04, 0x03, 0x02, 0x01])

REPORT_FRAME_LENGTH = 14  # 4 header + 2 length field + 4 float + 4 tail


def read_distance(data: bytes) -> float | None:
    '''
    Parse a report frame and return the detection distance in mm.
    Locates the header within data to handle misaligned first reads.
    Returns None if the frame is invalid or no target detected.
    '''
    pos = data.find(REPORT_HEADER)
    if pos == -1:
        return None
    frame = data[pos:]
    if len(frame) < REPORT_FRAME_LENGTH:
        return None
    if frame[10:14] != REPORT_TAIL:
        return None
    return struct.unpack_from('<f', frame, 6)[0]


def _send_command(ser: serial.Serial, command_word: bytes, command_value: bytes = b'') -> bytes:
    data_length = (2 + len(command_value)).to_bytes(2, 'little')
    frame = COMMAND_HEADER + data_length + command_word + command_value + COMMAND_TAIL
    ser.write(frame)
    return ser.read_until(COMMAND_TAIL)


def _ack_success(response: bytes) -> bool:
    # ACK status sits at bytes 8:10 (header[4] + length[2] + cmd_echo[2])
    return len(response) >= 10 and int.from_bytes(response[8:10], 'little') == 0


def read_firmware_version(ser: serial.Serial) -> str | None:
    '''Read firmware version. Returns e.g. "V1.4.14" or None on failure.'''
    response = _send_command(ser, bytes([0x00, 0x00]))
    if len(response) < 14:
        return None
    major = int.from_bytes(response[8:10],  'little')
    minor = int.from_bytes(response[10:12], 'little')
    patch = int.from_bytes(response[12:14], 'little')
    return f'V{major}.{minor}.{patch}'


def enable_configuration(ser: serial.Serial) -> bool:
    '''Enter configuration mode. Must be called before any config command.'''
    response = _send_command(ser, bytes([0xFF, 0x00]), bytes([0x01, 0x00]))
    return _ack_success(response)


def end_configuration(ser: serial.Serial) -> bool:
    '''Exit configuration mode and resume reporting.'''
    response = _send_command(ser, bytes([0xFE, 0x00]))
    return _ack_success(response)


def set_min_distance(ser: serial.Serial, distance_mm: int) -> bool:
    '''Set minimum detection distance (150–10500 mm). Requires config mode.'''
    response = _send_command(ser, bytes([0x74, 0x00]), distance_mm.to_bytes(2, 'little'))
    return _ack_success(response)


def set_max_distance(ser: serial.Serial, distance_mm: int) -> bool:
    '''Set maximum detection distance (150–10500 mm). Requires config mode.'''
    response = _send_command(ser, bytes([0x75, 0x00]), distance_mm.to_bytes(2, 'little'))
    return _ack_success(response)


def set_reporting_cycle(ser: serial.Serial, period_ms: int) -> bool:
    '''Set reporting period in ms (50–1000). Requires config mode.'''
    response = _send_command(ser, bytes([0x71, 0x00]), period_ms.to_bytes(2, 'little'))
    return _ack_success(response)


def read_reporting_cycle(ser: serial.Serial) -> int | None:
    '''Read current reporting period in ms. Requires config mode.'''
    response = _send_command(ser, bytes([0x70, 0x00]))
    if len(response) < 12:
        return None
    return int.from_bytes(response[8:12], 'little')


def update_threshold(ser: serial.Serial) -> bool:
    '''Trigger background noise calibration. Requires config mode.'''
    response = _send_command(ser, bytes([0x72, 0x00]))
    return _ack_success(response)
