"""自动移除智谱 CogView 图片右下角的“AI生成”文字水印。

原理：水印是半透明的灰色文字，会在局部产生“通道差异很小的高幅残差”，
据此检测出字形像素，再用周围未遮挡像素的中值填补。

用法：python tools/remove_watermark.py <图片路径>
"""

import os
import sys

import numpy as np
from PIL import Image, ImageFilter


def detect_glyph_mask(im, zone):
    """在 zone=(x0,y0,x1,y1) 区域内检测文字形残差块。"""
    x0, y0, x1, y1 = zone
    region = np.asarray(im.crop(zone), dtype=np.int16)
    bg = np.asarray(im.crop(zone).filter(ImageFilter.MedianFilter(15)), dtype=np.int16)
    res = region - bg
    mag = np.sqrt((res ** 2).sum(axis=2))
    spread = res.std(axis=2)
    cand = (mag > 22) & (spread < 14)

    hgt, wdt = cand.shape
    seen = np.zeros_like(cand, dtype=bool)
    keep = np.zeros_like(cand, dtype=bool)
    for y in range(hgt):
        for x in range(wdt):
            if not cand[y, x] or seen[y, x]:
                continue
            stack = [(x, y)]
            seen[y, x] = True
            pts = []
            while stack:
                cx, cy = stack.pop()
                pts.append((cx, cy))
                for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                    if 0 <= nx < wdt and 0 <= ny < hgt and cand[ny, nx] and not seen[ny, nx]:
                        seen[ny, nx] = True
                        stack.append((nx, ny))
            # 字形大小的紧凑块（避开大片毛发纹理）
            if 12 <= len(pts) <= 500:
                for px, py in pts:
                    keep[py, px] = True
    return keep


def inpaint(arr, mask, radius=8, passes=4):
    """用周围未遮挡像素的中值填补 mask 区域。"""
    h, w, _ = arr.shape
    cur = arr.copy()
    mm = mask.copy()
    for _ in range(passes):
        idxs = np.argwhere(mm)
        if len(idxs) == 0:
            break
        for py, px in idxs:
            ys = slice(max(0, py - radius), min(h, py + radius + 1))
            xs = slice(max(0, px - radius), min(w, px + radius + 1))
            win = cur[ys, xs]
            winm = mm[ys, xs]
            good = win[~winm]
            if len(good) == 0:
                continue
            cur[py, px] = np.median(good, axis=0)
        # 收缩掩膜：只处理上一轮被填补像素的邻域
        from PIL import Image as _I
        mimg = _I.fromarray((mm * 255).astype(np.uint8))
        mm = np.asarray(mimg.filter(ImageFilter.MaxFilter(3)), dtype=bool)
    return cur


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "inner.png"
    )
    im = Image.open(path).convert("RGB")
    w, h = im.size
    zone = (int(w * 0.82), int(h * 0.88), w, h)  # 右下角区域
    mask = detect_glyph_mask(im, zone)
    x0, y0, x1, y1 = zone
    full = np.zeros((h, w), dtype=bool)
    full[y0:y1, x0:x1] = mask
    print("watermark pixels:", int(full.sum()))
    if full.sum() == 0:
        print("未检测到水印字形，未做修改")
        return
    arr = np.asarray(im)
    arr = inpaint(arr, full)
    Image.fromarray(arr).save(path)
    ys, xs = np.argwhere(full).T
    print(f"已修复区域: x {xs.min()}-{xs.max()}, y {ys.min()}-{ys.max()}")


if __name__ == "__main__":
    main()
