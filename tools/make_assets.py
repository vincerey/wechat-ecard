"""生成贺卡资源：背景音乐 music.wav 与分享预览图 preview.png。

用法：python tools/make_assets.py
"""

import math
import os
import random
import struct
import wave

from PIL import Image, ImageDraw, ImageFont


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets")
os.makedirs(ASSETS, exist_ok=True)


# ---------------------------------------------------------------- 音乐
SAMPLE_RATE = 22050
NOTE = {
    "F2": 87.31, "G2": 98.00, "A2": 110.00, "C3": 130.81, "F3": 174.61, "G3": 196.00,
    "A3": 220.00, "B3": 246.94, "C4": 261.63, "D4": 293.66,
    "E4": 329.63, "F4": 349.23, "G4": 392.00, "A4": 440.00,
    "C5": 523.25, "D5": 587.33, "E5": 659.25, "G5": 783.99,
}

# 每小节：低音 + 琶音
CHORDS = [
    ("C3", ["C4", "E4", "G4", "C5", "G4", "E4"]),
    ("A2", ["A3", "C4", "E4", "A4", "E4", "C4"]),
    ("F2", ["F3", "A3", "C4", "F4", "C4", "A3"]),
    ("G2", ["G3", "B3", "D4", "G4", "D4", "B3"]),
]
BAR_SECONDS = 2.4
NOTE_SECONDS = BAR_SECONDS / 6
LOOPS = 2


def note_tone(freq, dur, amp=0.5):
    """音乐盒音色：基频 + 泛音，指数衰减包络。"""
    n = int(SAMPLE_RATE * dur)
    samples = []
    decay = 6.0 / dur
    for i in range(n):
        t = i / SAMPLE_RATE
        env = math.exp(-decay * t)
        vib = 1.0 + 0.003 * math.sin(2 * math.pi * 5.2 * t)
        s = (
            math.sin(2 * math.pi * freq * vib * t)
            + 0.32 * math.sin(2 * math.pi * freq * 2 * vib * t)
            + 0.10 * math.sin(2 * math.pi * freq * 3 * vib * t)
        )
        samples.append(amp * env * s)
    return samples


def bass_tone(freq, dur, amp=0.10):
    n = int(SAMPLE_RATE * dur)
    fade = int(SAMPLE_RATE * 0.12)
    out = []
    for i in range(n):
        t = i / SAMPLE_RATE
        s = math.sin(2 * math.pi * freq * t) + 0.3 * math.sin(2 * math.pi * freq * 2 * t)
        env = 1.0
        if i < fade:
            env = i / fade
        elif i > n - fade:
            env = (n - i) / fade
        out.append(amp * env * s)
    return out


def build_music():
    total = int(SAMPLE_RATE * BAR_SECONDS * len(CHORDS) * LOOPS)
    mix = [0.0] * total
    base = 0
    for _ in range(LOOPS):
        for bass, arpeggio in CHORDS:
            # 低音
            b = bass_tone(NOTE[bass], BAR_SECONDS + 0.4)
            for i, v in enumerate(b):
                pos = base + i
                if pos < total:
                    mix[pos] += v
            # 琶音
            for j, note in enumerate(arpeggio):
                start = base + int(j * NOTE_SECONDS * SAMPLE_RATE)
                tone = note_tone(NOTE[note], NOTE_SECONDS * 1.7, amp=0.42)
                for i, v in enumerate(tone):
                    pos = start + i
                    if pos < total:
                        mix[pos] += v
            base += int(BAR_SECONDS * SAMPLE_RATE)

    # 无缝循环：首尾淡入淡出
    fade = int(SAMPLE_RATE * 0.9)
    for i in range(fade):
        mix[i] *= i / fade
        mix[total - 1 - i] *= i / fade

    peak = max(abs(v) for v in mix) or 1.0
    scale = 0.62 / peak
    frames = b"".join(
        struct.pack("<h", int(max(-1.0, min(1.0, v * scale)) * 32767)) for v in mix
    )
    path = os.path.join(ASSETS, "music.wav")
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SAMPLE_RATE)
        w.writeframes(frames)
    print("music.wav ->", os.path.getsize(path), "bytes")


# ---------------------------------------------------------------- 预览图
def heart_points(cx, cy, scale, steps=140):
    pts = []
    for i in range(steps):
        t = i / steps * 2 * math.pi
        x = 16 * math.sin(t) ** 3
        y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        pts.append((cx + x * scale, cy - y * scale))
    return pts


def make_preview():
    W, H = 1200, 630
    img = Image.new("RGB", (W, H))
    px = img.load()
    top = (24, 15, 62)
    mid = (77, 38, 122)
    bottom = (163, 67, 142)
    for y in range(H):
        r = y / H
        if r < 0.55:
            t = r / 0.55
            c = tuple(int(top[i] + (mid[i] - top[i]) * t) for i in range(3))
        else:
            t = (r - 0.55) / 0.45
            c = tuple(int(mid[i] + (bottom[i] - mid[i]) * t) for i in range(3))
        for x in range(W):
            px[x, y] = c

    draw = ImageDraw.Draw(img, "RGBA")
    # 光晕
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((W - 420, -160, W + 160, 420), fill=(255, 215, 122, 46))
    gd.ellipse((-260, H - 360, 360, H + 260), fill=(255, 95, 143, 52))
    img = Image.alpha_composite(img.convert("RGBA"), glow)
    draw = ImageDraw.Draw(img, "RGBA")

    # 小星星
    rng = random.Random(7)
    for _ in range(90):
        x, y = rng.randrange(W), rng.randrange(H)
        a = rng.randrange(40, 130)
        draw.ellipse((x, y, x + 3, y + 3), fill=(255, 255, 255, a))

    # 爱心
    hearts = [
        (180, 150, 8, (255, 173, 196, 180)),
        (250, 480, 11, (255, 95, 143, 200)),
        (920, 140, 9, (255, 215, 122, 190)),
        (1000, 500, 13, (255, 143, 171, 210)),
        (620, 90, 6, (255, 230, 160, 170)),
        (760, 540, 7, (255, 255, 255, 150)),
    ]
    for cx, cy, s, fill in hearts:
        draw.polygon(heart_points(cx, cy, s), fill=fill)

    # 文字
    def font(size, bold=True):
        candidates = [
            r"C:\Windows\Fonts\msyhbd.ttc" if bold else r"C:\Windows\Fonts\msyh.ttc",
            r"C:\Windows\Fonts\msyh.ttc",
            r"C:\Windows\Fonts\simhei.ttf",
        ]
        for c in candidates:
            if os.path.exists(c):
                try:
                    return ImageFont.truetype(c, size)
                except OSError:
                    continue
        return ImageFont.load_default()

    def draw_text(center_y, text, fnt, fill, shadow=(0, 0, 0, 140)):
        bbox = draw.textbbox((0, 0), text, font=fnt)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        x = (W - tw) / 2 - bbox[0]
        for dy, dx in [(3, 3), (2, 2), (1, 1)]:
            draw.text((x + dx, center_y + dy), text, font=fnt, fill=shadow)
        draw.text((x, center_y), text, font=fnt, fill=fill)

    draw_text(150, "生日快乐", font(150), (255, 235, 180, 255))
    draw_text(330, "· 七夕快乐 ·", font(84), (255, 175, 200, 255))
    draw_text(470, "轻触打开，收下这份专属祝福", font(40), (255, 245, 230, 235))

    img = img.convert("RGB")
    path = os.path.join(ASSETS, "preview.png")
    img.save(path)
    print("preview.png ->", os.path.getsize(path), "bytes")


if __name__ == "__main__":
    build_music()
    make_preview()
