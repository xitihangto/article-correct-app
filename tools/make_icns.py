#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把 1024×1024 的图标母版打成 macOS 用的 AppIcon.icns。

    python tools/make_icns.py docs/icon/icon-master.png Resources/AppIcon.icns

做两件小事：
  1. 按 macOS 要求的十档尺寸逐档缩放（不是让系统自己缩，16/32 那两档差别很明显）；
  2. 小尺寸（≤64）补一点锐化 —— 插画类图标缩下去会糊成一团，锐化一下轮廓才立得住。
"""

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageFilter

# 文件名 → 像素边长。@2x 是给 Retina 用的，必须单独出，不能靠系统插值。
SPEC = {
    "icon_16x16.png": 16,
    "icon_16x16@2x.png": 32,
    "icon_32x32.png": 32,
    "icon_32x32@2x.png": 64,
    "icon_128x128.png": 128,
    "icon_128x128@2x.png": 256,
    "icon_256x256.png": 256,
    "icon_256x256@2x.png": 512,
    "icon_512x512.png": 512,
    "icon_512x512@2x.png": 1024,
}


def main(src: Path, dst: Path) -> None:
    master = Image.open(src).convert("RGBA")
    if master.size != (1024, 1024):
        raise SystemExit(f"母版必须是 1024×1024，现在是 {master.size}")

    with tempfile.TemporaryDirectory() as tmp:
        iconset = Path(tmp) / "AppIcon.iconset"
        iconset.mkdir()
        for name, px in SPEC.items():
            tile = master.resize((px, px), Image.LANCZOS)
            if px <= 64:
                # 半径和强度都压得很小，只提轮廓，不要出现白边
                tile = tile.filter(ImageFilter.UnsharpMask(radius=0.6, percent=90, threshold=0))
            tile.save(iconset / name)
        print(f"  已生成 {len(SPEC)} 档尺寸")

        dst.parent.mkdir(parents=True, exist_ok=True)
        if dst.exists():
            dst.unlink()
        r = subprocess.run(["iconutil", "-c", "icns", str(iconset), "-o", str(dst)],
                           capture_output=True, text=True)
        if r.returncode != 0:
            raise SystemExit(f"iconutil 失败：{r.stderr.strip()}")

    print(f"  已写出：{dst}（{dst.stat().st_size // 1024} KB）")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    main(Path(sys.argv[1]), Path(sys.argv[2]))
