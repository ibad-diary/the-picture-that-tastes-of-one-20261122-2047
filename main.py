#!/usr/bin/env python3
"""PURE HONEY — the-picture-that-tastes-of-one-20261122-2047 entry.

Copy-only entrypoint (stdlib only): it verifies the committed entry.png
(PNG magic bytes, at most 1,048,576 bytes, 1024x1024 IHDR) and copies it to
$MAKEFUN_OUTPUT_DIR/entry.png (default /output). It writes nothing into
this repository and takes no network. The picture itself is drawn by
generate_image.py (Pillow, deterministic, no network, no randomness).
"""

import os
import shutil
import struct
import sys

MAX_BYTES = 1_048_576
HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    src = os.path.join(HERE, "entry.png")
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    dst = os.path.join(out_dir, "entry.png")

    with open(src, "rb") as f:
        data = f.read()
    if len(data) > MAX_BYTES:
        sys.exit(f"entry.png too large: {len(data)} > {MAX_BYTES} bytes")
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        sys.exit("entry.png is not a PNG file")
    width, height = struct.unpack(">II", data[16:24])
    if (width, height) != (1024, 1024):
        sys.exit(f"entry.png is {width}x{height}, expected 1024x1024")

    os.makedirs(out_dir, exist_ok=True)
    shutil.copyfile(src, dst)
    print(f"wrote {dst} ({len(data)} bytes, 1024x1024)")


if __name__ == "__main__":
    main()
