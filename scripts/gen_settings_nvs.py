#!/usr/bin/env python3

import argparse
from binascii import hexlify, unhexlify
from pathlib import Path

import intelhex


class SettingsNVSStorage:
    """Settings NVS storage class for Zephyr settings subsystem with NVS backend."""

    SECTOR_SIZE = 4096  # Default sector size for most flash devices
    ERASED_BYTE = b"\xff"
    NVS_NAMECNT = 0x8000

    def __init__(self, sector_count: int = 8, offset: int = 0):
        self.sector_count = sector_count
        self.offset = offset

        # Initialize with erased flash (0xff)
        # It looks like the flash partition can be smaller than the configured sector_count of NVS
        # in this case settings_nvs initializes MIN(flash_partition_size, sector_count
        self.data = bytearray(self.ERASED_BYTE * self.SECTOR_SIZE * self.sector_count)

    def generate(self, entries):
        offset = 0
        trail_offset = self.SECTOR_SIZE

        # Add sector close ate
        trail_offset -= 16
        self._insert_by_offset(trail_offset, self._sector_close_ate())

        # Add largest name entry id
        trail_offset -= 8
        self._insert_by_offset(trail_offset, unhexlify("008000000200ff8d"))
        self._insert_by_offset(offset, unhexlify("0180"))
        offset += 2

        # Add settings data entry
        name, entry = entries[0]
        entry = unhexlify(entry)
        trail_offset -= 8
        ate = (
            (self.NVS_NAMECNT + 1 + 0x4000).to_bytes(2, byteorder="little")
            + offset.to_bytes(2, byteorder="little")
            + len(entry).to_bytes(2, byteorder="little")
            + b"\xff"
        )
        ate += self.crc8_ccitt(ate, init=0xFF).to_bytes(1, "little")
        self._insert_by_offset(trail_offset, ate)
        self._insert_by_offset(offset, entry)
        offset += len(entry)

        name = name.encode()
        trail_offset -= 8
        ate = (
            (self.NVS_NAMECNT + 1).to_bytes(2, byteorder="little")
            + offset.to_bytes(2, byteorder="little")
            + len(name).to_bytes(2, byteorder="little")
            + b"\xff"
        )
        ate += self.crc8_ccitt(ate, init=0xFF).to_bytes(1, "little")
        self._insert_by_offset(trail_offset, ate)
        self._insert_by_offset(offset, name)
        offset += len(name)

    def _insert_by_offset(self, offset: int, data: bytes):
        self.data[offset : offset + len(data)] = data

    def _sector_close_ate(self):
        """Close the current sector and prepare for writing a new ATE."""
        data = unhexlify("ffff00000000ff")
        data += self.crc8_ccitt(data).to_bytes(1, "little")
        data += b"\xff" * 8
        return data

    @staticmethod
    def crc8_ccitt(data: bytes, poly=0x07, init=0xFF):
        """Calculate CRC-8-CCITT checksum."""
        crc = init
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 0x80:
                    crc = ((crc << 1) ^ poly) & 0xFF
                else:
                    crc = (crc << 1) & 0xFF
        return crc

    def write_intel_hex(self, filename: Path):
        ih = intelhex.IntelHex()
        ih.frombytes(self.data, offset=self.offset)
        ih.write_hex_file(filename)

    def write_data(self, filename: Path):
        with open(filename, "wb") as f:
            f.write(self.data)


if __name__ == "__main__":
    data = "ffff00000000ff"  # 0x5c
    data = "01801e000400ff"  # 0x4f
    d = unhexlify(data)
    print(d)
    crc = SettingsNVSStorage.crc8_ccitt(d, init=0xFF)
    print(hex(crc))

    parser = argparse.ArgumentParser(
        description="Generate NVS settings for Zephyr with NVS backend."
    )
    parser.add_argument(
        "--sector-count",
        type=lambda x: int(x, 0),
        default=8,
        help="NVS sector_count (default: 8)",
    )
    parser.add_argument(
        "--offset",
        type=lambda x: int(x, 0),
        default=0xF8000,
        help="Base address/offset for Intel HEX (default: 0xf8000)",
    )
    parser.add_argument("--entry", action="append", default=[], help="NVS hex entry")
    args = parser.parse_args()

    entries = [tuple(e.split("=", 1)) for e in args.entry]
    print("sector_count: ", args.sector_count)
    print("offset: ", hex(args.offset))

    settings = SettingsNVSStorage(sector_count=args.sector_count, offset=args.offset)  # 0xf8000 for nrf52840dk
    settings.generate(entries)
    settings.write_intel_hex(Path("nvs_generated.hex"))
    # settings.write_data(Path("nvs_generated.bin"))
