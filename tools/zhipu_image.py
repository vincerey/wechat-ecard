"""使用智谱 CogView 生成贺卡插画背景。

依赖：环境变量 ZHIPU_API_KEY（智谱开放平台 https://open.bigmodel.cn 的 API Key）
用法：python tools/zhipu_image.py
生成：assets/cover.png（封面：小王子拿着玫瑰）、assets/inner.png（内页：星座风小狮子+蛋糕）
"""

import json
import os
import sys
import time
import urllib.request


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets")
API_URL = "https://open.bigmodel.cn/api/paas/v4/images/generations"
MODEL = os.environ.get("ZHIPU_MODEL", "cogview-3-flash")  # 可用 cogview-4-250304（付费）
SIZE = "720x1440"                  # 手机竖屏

PROMPTS = {
    "cover.png": (
        "手机竖屏电子贺卡封面插画，儿童绘本/治愈系插画风格：一位金色短发的小男孩，"
        "头戴黄色小皇冠，身后飘着一条黄色围巾，穿着简洁的绿色系衣服，坐在地上，"
        "双手温柔地捧着一朵盛开的红色玫瑰花，微微低头专注地看着玫瑰，表情可爱纯真。"
        "背景是干净明亮的浅色（米白/浅奶油色），散布着几颗小星星和几个小行星图案，"
        "色彩明亮柔和，线条简洁流畅，配色以绿色、黄色、红色为主，温馨梦幻。"
        "构图：小男孩坐在画面下方三分之一处，上方留出干净的浅色区域用于叠加标题文字。"
        "不要出现任何文字，无水印。"
    ),
    "inner.png": (
        "手机竖屏电子贺卡内页背景，星座主题：深蓝色夜空，散布着柔和的星星和银白色的星座连线"
        "（狮子座星图）。一只非常可爱的卡通小狮子，圆脸、大眼睛、浅金色毛发、戴着小皇冠，"
        "坐在一个漂亮的生日蛋糕旁边，蛋糕上插着点燃的彩色蜡烛并点缀星星，小狮子笑眯眯地看着蜡烛。"
        "画面浪漫梦幻，四周有柔和的光晕，扁平可爱插画风格，唯美治愈。"
        "构图：小狮子和蛋糕放在画面下半部分，上半部分留出星空区域方便叠加文字卡片。"
        "不要出现任何文字。"
    ),
}


def get_key():
    key = os.environ.get("ZHIPU_API_KEY", "").strip()
    if key:
        return key
    # 兜底：读取本地 key 文件（可选）
    key_file = os.path.join(ROOT, "zhipu_key.txt")
    if os.path.exists(key_file):
        key = open(key_file, encoding="utf-8").read().strip()
    if not key:
        sys.exit("未找到 ZHIPU_API_KEY：请先设置环境变量，或把 key 保存到 zhipu_key.txt")
    return key


def generate_one(key, filename, prompt, retries=2):
    body = json.dumps({
        "model": MODEL,
        "prompt": prompt,
        "size": SIZE,
        "watermark": False,  # 关闭 CogView 自动水印
        "watermark_enabled": False,
    }).encode("utf-8")
    req = urllib.request.Request(
        API_URL,
        data=body,
        headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"},
        method="POST",
    )
    for attempt in range(1, retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=180) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            url = data["data"][0]["url"]
            out = os.path.join(ASSETS, filename)
            with urllib.request.urlopen(url, timeout=180) as img:
                raw = img.read()
            with open(out, "wb") as f:
                f.write(raw)
            print(f"OK {filename}: {len(raw)} bytes")
            return True
        except Exception as e:  # noqa: BLE001
            print(f"[{attempt}/{retries}] {filename} 失败: {e}")
            time.sleep(3)
    return False


def main():
    key = get_key()
    os.makedirs(ASSETS, exist_ok=True)
    only = sys.argv[1] if len(sys.argv) > 1 else None
    ok = True
    for filename, prompt in PROMPTS.items():
        if only and filename != only:
            continue
        ok = generate_one(key, filename, prompt) and ok
    if not ok:
        sys.exit("有图片生成失败，请检查 key / 网络 / 模型额度后重试")
    print("全部生成完成：assets/cover.png, assets/inner.png")


if __name__ == "__main__":
    main()
