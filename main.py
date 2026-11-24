#!/usr/bin/env python3
"""Entry program for make.fun competition "news-image-20261123".

Sum up 23 November 2026's world news in one image.

The grader's sandbox has no network, so -- as the competition rules
explicitly allow ("a repository holding the image and a one-line program
that copies it there") -- this program copies the pre-rendered image
asset shipped in the repository (entry.png, drawn by build_image.py) to
the output directory. It uses only the Python standard library and is
fully deterministic: every run writes exactly the asset's bytes.

Output directory: $MAKEFUN_OUTPUT_DIR when set (the kit's local-run
convention), otherwise /output. The file written is entry.png.
"""

import os
from pathlib import Path

ASSET_NAME = "entry.png"
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def main() -> None:
    asset = Path(__file__).resolve().parent / ASSET_NAME
    data = asset.read_bytes()
    if not data.startswith(PNG_MAGIC):
        raise ValueError(f"{ASSET_NAME} is not a PNG image")
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output")
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / ASSET_NAME
    tmp = out_dir / (ASSET_NAME + ".tmp")
    tmp.write_bytes(data)
    tmp.replace(target)  # atomic: a run never leaves a partial image


if __name__ == "__main__":
    main()
