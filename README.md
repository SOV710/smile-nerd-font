# Smile Nerd Font Mono

**[English](README_en.md)** | 中文

![Font Preview](https://preview.github.sov710.org/smile-nerd-font/preview.png)

一款合成字体，将 **FiraCode Nerd Font Mono** 的拉丁字母、符号、Nerd Font 图标及编程连字与 **LXGW Wenkai Mono**（霞鹜文楷等宽）的 CJK 字形合二为一。构建过程中自动禁用 FiraCode 的 `www` 三字连字。

## 字重

字重映射定义在 `config.toml` 中，并在 `Makefile` 中作为 Make 依赖执行：

| 输出文件 | FiraCode 来源 | LXGW 来源 |
|----------|--------------|-----------|
| SmileNerdFontMono-Regular.ttf | FiraCodeNerdFontMono-Regular | LXGWWenKaiMono-Medium |
| SmileNerdFontMono-Light.ttf | FiraCodeNerdFontMono-Light | LXGWWenKaiMono-Regular |

## 前置条件

- Python >= 3.12
- [uv](https://docs.astral.sh/uv/)
- GNU Make
- [Typst](https://typst.app/) >= 0.14（可选，仅生成预览图时需要）

## 初始化

```sh
uv sync
```

## 构建

```sh
make all            # 合并 CJK 字形 + 修补 www 连字
make preview        # 生成 CJK 统一汉字 (U+4E00..U+9FFF) 的 HTML 字形网格
make live-preview   # 生成交互式实时文本预览（包含两个字重）
make clean          # 清理 build/ 和 preview/
```

输出字体写入 `build/`，预览 HTML 写入 `preview/`。

生成预览图（需要 Typst）：

```sh
typst compile --font-path ./build preview.typ preview.png --ppi 288
oxipng -o max preview.png  # 可选
```

## 脚本说明

| 脚本 | 用途 |
|------|------|
| `scripts/merge.py` | 将 LXGW Wenkai 的 CJK 字形合并到 FiraCode Nerd Font Mono |
| `scripts/patch_ligatures.py` | 禁用 `www` 三字连字（原地修改字体文件） |
| `scripts/render_preview.py` | 生成 HTML 字形网格预览页 |
| `scripts/gen_live_preview.py` | 生成带 base64 内嵌字体的交互式实时预览页 |

### merge.py

从 `config.toml` 读取字重配置，接受 `--weight regular` 或 `--weight light`。

```sh
uv run python scripts/merge.py --weight regular
```

### patch_ligatures.py

接受一个位置参数：要原地修补的 TTF 文件路径。

```sh
uv run python scripts/patch_ligatures.py build/SmileNerdFontMono-Regular.ttf
```

### render_preview.py

生成逐码点单元格的 HTML 字形网格。字体通过相对路径引用（会将字体文件复制到输出 HTML 旁边）。支持 `--compare` 进行双字体左右对比，`--range` 可重复指定多个 Unicode 范围。

```sh
uv run python scripts/render_preview.py \
  --font build/SmileNerdFontMono-Regular.ttf \
  --range 4E00:9FFF \
  --output preview/cjk.html

uv run python scripts/render_preview.py \
  --font build/SmileNerdFontMono-Regular.ttf \
  --compare assets/lxgw-wenkai/LXGWWenKaiMono-Regular.ttf \
  --range 4E00:4EFF \
  --output preview/compare.html
```

### gen_live_preview.py

生成自包含的 HTML 页面，字体以 base64 内嵌，用于交互式文本预览。接受一个或多个 `--fonts` 参数，多字体时提供下拉框切换。

```sh
uv run python scripts/gen_live_preview.py \
  --fonts build/SmileNerdFontMono-Regular.ttf build/SmileNerdFontMono-Light.ttf \
  --output preview/live.html
```

## 许可证

适用上游字体各自的许可证，详见：
- [FiraCode Nerd Font](https://github.com/ryanoasis/nerd-fonts)
- [LXGW Wenkai](https://github.com/lxgw/LxgwWenKai)
