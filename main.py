#!/usr/bin/env python3
"""PURE HONEY - entrypoint (copy-only, stdlib).

Verifies the committed entry.png (PNG magic, 1024x1024 IHDR, at most
1,048,576 bytes) and copies it to $MAKEFUN_OUTPUT_DIR/entry.png
(default /output). Writes nothing into this repository, and reads
nothing outside it except the output directory from the environment.
"""
import os
import shutil
import struct
import sys

MAX_BYTES = 1048576
EXPECTED_SIZE = (1024, 1024)


def fail(message):
    print(f"main.py: {message}", file=sys.stderr)
    return 1


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    dst = os.path.join(out_dir, "entry.png")
    if not os.path.isfile(src):
        return fail("entry.png not found next to main.py")
    size = os.path.getsize(src)
    if size > MAX_BYTES:
        return fail(f"entry.png is {size} bytes, over the {MAX_BYTES} limit")
    with open(src, "rb") as fh:
        head = fh.read(33)
    if head[:8] != b"\x89PNG\r\n\x1a\n":
        return fail("entry.png is not a PNG file")
    if head[12:16] != b"IHDR":
        return fail("entry.png has no IHDR chunk")
    width, height = struct.unpack(">II", head[16:24])
    if (width, height) != EXPECTED_SIZE:
        return fail(f"entry.png is {width}x{height}, expected 1024x1024")
    os.makedirs(out_dir, exist_ok=True)
    shutil.copyfile(src, dst)
    print(f"main.py: copied entry.png ({size} bytes, 1024x1024) to {dst}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
