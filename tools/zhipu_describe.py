"""用智谱 GLM-4V 视觉模型描述一张图片的风格，供 CogView 按风格重绘。

用法：python tools/zhipu_describe.py <图片路径>
"""

import base64
import json
import os
import sys
import urllib.request


API_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"


def get_key():
    key = os.environ.get("ZHIPU_API_KEY", "").strip()
    if key:
        return key
    sys.exit("未找到 ZHIPU_API_KEY 环境变量")


def describe(image_path):
    key = get_key()
    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")
    data_url = "data:image/png;base64," + b64
    prompt = (
        "请用中文详细描述这张图片，我将根据你的描述用 AI 重新生成同风格的图片。"
        "请说明：1) 画面内容（人物/物体/场景）；2) 艺术风格（如水彩、扁平插画、"
        "手绘线稿、儿童绘本、治愈系等）；3) 配色与色调；4) 线条与笔触特点；"
        "5) 构图与人物姿态；6) 光线氛围。只描述画面中真实存在的元素，不要编造。"
    )
    body = json.dumps({
        "model": "glm-4v-flash",
        "messages": [{
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": data_url}},
                {"type": "text", "text": prompt},
            ],
        }],
    }).encode("utf-8")
    req = urllib.request.Request(
        API_URL,
        data=body,
        headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return data["choices"][0]["message"]["content"]
    except urllib.error.HTTPError as e:
        return "HTTPError " + str(e.code) + ": " + e.read().decode("utf-8", "ignore")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("用法：python tools/zhipu_describe.py <图片路径>")
    print(describe(sys.argv[1]))
