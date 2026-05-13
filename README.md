# AI Marketing 素材生成器

一个桌面版素材生成工具：读取文本、图片、视频素材，批量生成营销文案变体，并可把文案压到图片上输出海报图。

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
python -m venv .venv
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

## 本次视觉升级

- 新增「视觉样式」：现代海报卡片、强描边无底、底部渐变标题、柔和玻璃卡片。
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
