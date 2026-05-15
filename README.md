# AI Marketing 素材生成器

一个桌面版素材生成工具：读取文本、图片、视频素材，批量生成英文 Facebook marketing 文案变体，并把文案渲染成社媒广告图。

## 快速启动

### macOS / Linux

```bash
./start.sh
```

### Windows

双击 `start.bat`，或在 PowerShell / CMD 里运行：

```bat
start.bat
```

启动脚本会自动创建 `.venv`、安装依赖，并打开桌面界面。

## 也可以用 pip 安装后启动

```bash
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
python -m pip install -e .
marketing-generator
```

## 素材目录

首次启动会自动创建：

```text
~/MarketingAssets/
├── texts/    # 放 .txt 文案素材
├── images/   # 放 jpg/png/webp 等图片
├── videos/   # 放 mp4/mov 等视频
├── fonts/    # 可选：放自定义中文字体 .ttf/.ttc/.otf
└── output/   # 生成结果
```

如果要改善中文字体效果，推荐把常用中文字体放到 `~/MarketingAssets/fonts/` 或项目内 `assets/fonts/`。也可以用环境变量指定：

```bash
MARKETING_GENERATOR_FONT=/path/to/font.ttf marketing-generator
```

## Facebook ad creative 升级

- 文案生成改为英文 Facebook ad 结构：badge / headline / benefit / CTA。
- 新增 Facebook feed 风格：Offer Card、Dark Gradient CTA、Premium Minimal。
- 不再使用 emoji 当图标，改用矢量 tag/check/arrow，避免出现方块乱码。
- 默认压图位置改为 bottom-left，更少遮挡主体。
- 色彩方案升级为广告常用 palette：Meta Blue、Direct Deal Orange、Premium Black Gold 等。
- 改善中文字体搜索，优先使用自定义字体、系统中文字体，再兜底到系统默认字体。
- 压图文字会按图片尺寸自适应换行和缩小字号，减少溢出。
- 增加圆角卡片、投影、描边、文字阴影和强调线，成品更像社媒海报。
- rendered 图片文件名包含文案变体编号，避免多个变体覆盖同一个文件。

## 打包成独立程序（可选）

如果需要分发给没有 Python 环境的电脑，可以用 PyInstaller：

```bash
python -m pip install pyinstaller
pyinstaller --name "AI-Marketing-Generator" --windowed ai_marketing_generator.py
```

打包产物会在 `dist/AI-Marketing-Generator/` 下。
