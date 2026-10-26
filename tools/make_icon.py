#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把 AI 生成的「圆角方块 + 白底」草稿图，加工成 macOS 可用的 app 图标母版。

AI 出图的问题：
  1. 四周是白底，不是透明 —— 直接打 icns 装进 Dock，四角会出现白方块；
  2. 圆角方块几乎铺满 1024 画布，而 macOS 的图标网格要求内容占 ~824/1024，
     四周留出 ~100px 阴影空间，否则在 Dock 里比别的 app 明显大一圈；
  3. AI 画的圆角曲率不一定是苹果那种连续曲率（squircle）。

这个脚本做三件事：
  裁掉白边 → 缩放到 824 → 用超椭圆（squircle）当蒙版重新抠形 → 加投影 → 输出 RGBA PNG。

用法：
    python tools/make_icon.py <源图.png> <输出.png>
    python tools/make_icon.py --preview <输出.png>      # 顺便出一张 Dock 效果预览
"""

import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

# macOS 图标网格：1024 画布里，圆角方块本体占 824，四周各留 100 给投影。
CANVAS = 1024
BODY = 824
SHADOW_OFFSET = 10          # 投影向下偏移
SHADOW_BLUR = 18            # 投影模糊半径
SHADOW_ALPHA = 0.30         # 投影不透明度
SQUIRCLE_N = 5.0            # 超椭圆指数，苹果连续圆角大约在 4.5~5
WHITE_CUT = 12              # 与纯白的差值小于这个值算背景
# AI 出图的圆角比苹果的更圆（实测沿对角线它的彩色起点在 79px，苹果的 squircle 在 66px），
# 直接套苹果形状会把 AI 边缘那圈浅灰描边留在里面，形成一圈白边。
# 所以先按苹果形状取蒙版，再往里缩 ERODE 像素，保证蒙版完全落在彩色区域内部。
# ERODE 用「1024 源图」尺度计。
# 注意：剪影尺寸恒等于 BODY（不随 ERODE 变），ERODE 改的只是内容缩放比 ——
# E 越大内容放得越大，蒙版边界落到源图上越靠里。24 对应边界落在源图 d≈91（彩色从 80 起），留 11px 余量。
ERODE = 24


def trim_white(im: Image.Image) -> Image.Image:
    """裁掉四周白底，只留下圆角方块本体。

    AI 出的图多数是「满幅」的：圆角方块上下左右都顶到画布边缘，只有四个角是白的。
    这种情况下按包围盒裁等于没裁，照原样用就行 —— 反正四个角随后会被蒙版切掉。
    """
    rgb = np.asarray(im.convert("RGB")).astype(np.int16)
    # 距离纯白的最大通道差；白底 ≈ 0，方块内部远大于阈值
    diff = (255 - rgb).max(axis=2)
    ys, xs = np.where(diff > WHITE_CUT)
    if len(xs) == 0:
        raise SystemExit("源图整张都是白的，没找到圆角方块")
    box = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
    w, h = box[2] - box[0], box[3] - box[1]
    if w >= im.width * 0.98 and h >= im.height * 0.98:
        print(f"  满幅出图（{im.width}×{im.height}），四角白底交给蒙版处理")
        return im
    print(f"  裁掉白边：{im.size} → {w}×{h}")
    return im.crop(box)


def squircle_mask(size: int, n: float = SQUIRCLE_N, ss: int = 4) -> Image.Image:
    """超椭圆 |x|^n + |y|^n = 1 当蒙版，4 倍超采样再缩回来，边缘才不锯齿。"""
    s = size * ss
    c = (s - 1) / 2.0
    y, x = np.mgrid[0:s, 0:s]
    nx = (x - c) / c
    ny = (y - c) / c
    inside = (np.abs(nx) ** n + np.abs(ny) ** n) <= 1.0
    m = Image.fromarray((inside * 255).astype(np.uint8), "L")
    return m.resize((size, size), Image.LANCZOS)


def build(src: Path, dst: Path) -> Image.Image:
    im = trim_white(Image.open(src))

    # 内容按 BODY + 2*ERODE 缩放；蒙版直接按 BODY 尺寸生成再居中贴进去，
    # 效果等于把苹果形状往里缩 ERODE，露在外面的剪影正好是 BODY。
    # （不要用 MinFilter 做内缩：卷积窗口在图像边界会被裁掉，边上一圈缩不进去，
    #   结果就是顶部/底部留一条半透明带 —— 踩过。）
    box = BODY + ERODE * 2
    body = im.resize((box, box), Image.LANCZOS).convert("RGBA")

    mask = Image.new("L", (box, box), 0)
    mask.paste(squircle_mask(BODY), (ERODE, ERODE))
    body.putalpha(mask)

    off = (CANVAS - box) // 2

    # 投影：拿方块形状本身做剪影，模糊后压在半透明黑上
    silhouette = Image.new("RGBA", (box, box), (0, 0, 0, 255))
    silhouette.putalpha(mask.point(lambda v: int(v * SHADOW_ALPHA)))
    shadow = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    shadow.paste(silhouette, (off, off + SHADOW_OFFSET), silhouette)
    shadow = shadow.filter(ImageFilter.GaussianBlur(SHADOW_BLUR))

    canvas = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    canvas = Image.alpha_composite(canvas, shadow)
    canvas.paste(body, (off, off), body)
    canvas.save(dst)
    print(f"  已写出：{dst}（{CANVAS}×{CANVAS} RGBA，剪影 {BODY}px，四周留 {off + ERODE}px）")
    return canvas


def preview(master: Path, dst: Path) -> None:
    """做一张「浅色底 + 深色底」的效果预览，顺便把 32/64 小尺寸也放进去。"""
    ic = Image.open(master).convert("RGBA")
    sizes = [256, 128, 64, 32]
    pad = 20
    w = pad + sum(s + pad for s in sizes)
    h = pad * 3 + 256 + 256
    sheet = Image.new("RGB", (w, h), (255, 255, 255))
    # 上半浅色、下半深色，检查透明角和投影在两种背景下都正常
    sheet.paste(Image.new("RGB", (w, 256 + pad * 2), (28, 28, 30)), (0, 256 + pad * 2))

    for row, top in enumerate((pad, 256 + pad * 2 + pad)):
        x = pad
        for s in sizes:
            tile = ic.resize((s, s), Image.LANCZOS)
            sheet.paste(tile, (x, top), tile)
            x += s + pad
    sheet.save(dst)
    print(f"  预览：{dst}")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) < 2:
        raise SystemExit(__doc__)
    src, dst = Path(args[0]), Path(args[1])
    print(f"处理 {src.name}")
    build(src, dst)
    if "--preview" in sys.argv:
        preview(dst, dst.with_name(dst.stem + "-preview.png"))
