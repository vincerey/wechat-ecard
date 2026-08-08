"""把用户提供的封面参考图处理成贺卡竖版背景。

原图 800x944（浅色底，主体在下半部分）：
1. 等比放大到宽 1080，底部对齐放入 1080x2160 画布；
2. 顶部空白用原图背景色延展填充；
3. 整体轻度锐化，提升清晰度。

用法：python tools/prepare_cover.py [源图路径]
输出：assets/cover.png
"""

import os
import sys

from PIL import Image, ImageFilter


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE = os.path.join(ROOT, "refs", "reference-cover.png")
OUT = os.path.join(ROOT, "assets", "cover.png")
W, H = 1080, 2160  # 竖版 1:2


def edge_color(im):
    """取原图顶部边缘区域的背景主色。"""
    w, h = im.size
    strip = im.crop((int(w * 0.05), int(h * 0.03), int(w * 0.95), int(h * 0.10)))
    px = list(strip.convert("RGB").getdata())
    n = len(px)
    return tuple(sum(c[i] for c in px) // n for i in range(3))


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else SOURCE
    if not os.path.exists(src):
        sys.exit(f"源图不存在：{src}")

    im = Image.open(src).convert("RGB")
    scale = W / im.width
    im = im.resize((W, int(im.height * scale)), Image.LANCZOS)

    canvas = Image.new("RGB", (W, H), edge_color(im))
    # 主体在原图下半部分，底部对齐放入，顶部留出干净背景
    canvas.paste(im, (0, H - im.height))
    # 轻度锐化提升清晰度（插画风格，避免过度）
    canvas = canvas.filter(ImageFilter.UnsharpMask(radius=2, percent=110, threshold=3))
    canvas.save(OUT)
    print(f"OK {OUT}: {canvas.size}, {os.path.getsize(OUT)} bytes")


if __name__ == "__main__":
    main()
