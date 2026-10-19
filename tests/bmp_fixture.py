"""Small standard V4 fixtures; no game resources or production conversion."""
import struct


def bmp_v4(alphas=(0, 128, 255)):
    pixels = b"".join(bytes((30, 20, 10, alpha)) for alpha in alphas)
    dib = struct.pack("<IiiHHIIiiII", 108, len(alphas), 1, 1, 32, 3,
                      len(pixels), 0, 0, 0, 0)
    dib += struct.pack("<IIIII", 0x00ff0000, 0x0000ff00, 0x000000ff,
                       0xff000000, 0x73524742) + bytes(48)
    return b"BM" + struct.pack("<IHHI", 122 + len(pixels), 0, 0, 122) + dib + pixels
