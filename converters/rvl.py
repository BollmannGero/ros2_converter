import struct


def parse_rvl_file(data: bytes) -> tuple[int, int, bytes]:
    """Validate the RVL1 container and return width, height, and compressed payload."""
    # Little-endian layout: magic (4 bytes), width, height, payload length (uint32).
    header_size = struct.calcsize("<4sIII")
    if len(data) < header_size:
        raise ValueError("RVL file is shorter than its header")

    magic, width, height, payload_size = struct.unpack_from("<4sIII", data)
    if magic != b"RVL1":
        raise ValueError("RVL file does not have the RVL1 signature")
    if width == 0 or height == 0:
        raise ValueError("RVL image width and height must be greater than zero")
    if payload_size != len(data) - header_size:
        raise ValueError("RVL payload length does not match the file size")
    if payload_size == 0 or payload_size % 4 != 0:
        raise ValueError("RVL payload must contain one or more complete 32-bit words")

    return width, height, data[header_size:]
