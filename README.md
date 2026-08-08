# 双层动态电子贺卡（生日 · 七夕）

纯静态、零依赖的电子贺卡，可在微信里直接点开链接浏览。两层结构：

1. **封面层**：小王子插画风格背景（拿着玫瑰的小王子）+「生日快乐 · 七夕快乐」主题，轻触任意位置打开。
2. **内页层**：星座风格背景（可爱小狮子 + 生日蛋糕）+ 文字直接嵌在背景上 + 彩带绽放 + 背景音乐（生日快乐歌·轻快版）。

## 文件结构

```text
wechat-ecard/
├── index.html          # 页面结构（含两层卡片与分享标签）
├── css/style.css       # 全部样式与动画
├── js/main.js          # 开卡 / 重开 / 音乐 / 彩带 / URL 参数
├── assets/
│   ├── music.wav       # 背景音乐（自动生成，生日快乐歌·轻快版）
│   ├── cover.png       # 封面背景（用户提供的参考图，脚本处理成竖版）
│   ├── inner.png       # 内页背景插画（星座风小狮子 + 蛋糕）
│   └── preview.png     # 微信/网页分享预览图
├── tools/
│   ├── make_assets.py  # 重新生成音乐和预览图
│   ├── prepare_cover.py# 把封面参考图处理成竖版背景
│   ├── zhipu_image.py  # 用智谱 CogView 生成插画背景（需 ZHIPU_API_KEY）
│   └── test_page.mjs   # 本地自动化测试脚本
└── README.md
```

## 如何修改内容

### 祝福文字
编辑 `index.html` 中 `.message` 里的文字，以及 `.greeting` 里的称呼、`.sign` 里的署名即可。

### 收件人姓名（链接参数）
部署后在链接后加参数即可自动填入称呼，无需改代码：

```text
https://你的用户名.github.io/wechat-ecard/?name=小美
```

支持 `name` 和 `to` 两个参数。

### 背景音乐
`tools/make_assets.py` 中 `MELODY` 是生日快乐歌的旋律（音名 + 拍数），`NOTE` 是音名频率表。修改后运行：

```powershell
python tools/make_assets.py
```

会重新生成 `assets/music.wav` 和 `assets/preview.png`。

### 主题配色
所有颜色集中在 `css/style.css` 顶部的 `:root` 变量里，改一处即可全局生效。

## 本地预览

```powershell
python -m http.server 8000
# 浏览器打开 http://127.0.0.1:8000
```

自动化验证（需要 Node + Edge/Chrome）：

```powershell
node tools/test_page.mjs
```

截图输出在 `tools/shots/`。

## 部署到 GitHub Pages

1. 新建仓库（仓库名如 `wechat-ecard`），推送本目录内容。
2. 仓库 Settings → Pages → Source 选择 `main` 分支的 `/` 目录。
3. 等待 1~2 分钟，访问：

```text
https://你的用户名.github.io/wechat-ecard/
```

## 微信分享注意事项

- 链接以 `https://` 开头即可在微信内直接点开；微信内嵌浏览器支持本页所有动画。
- 微信的链接预览卡片（标题/描述/缩略图）读取页面 `<title>`、`description` 与 `og:` 标签，部署后一般会自动抓取 `assets/preview.png`。
- 背景音乐在点击打开后才播放（符合微信对自动播放的限制），可随时暂停。
- 若想自定义微信分享卡片样式（自定义标题图片、隐藏来源信息），需要微信公众号 JS-SDK 并配置域名，普通个人页面做不到，可忽略。
