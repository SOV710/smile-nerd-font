# Smile Nerd Font Mono

English | **[中文](README.md)**

![Font Preview](https://preview.github.sov710.org/smile-nerd-font/preview.png)

A composite font combining **FiraCode Nerd Font Mono** (Latin, symbols, Nerd Font icons, ligatures) with **LXGW Wenkai Mono** (CJK glyphs). The `www` triple-ligature from FiraCode is automatically disabled during the build.

## Weights

Weight mappings are defined in `config.toml` and enforced as Make dependencies in `Makefile`:

| Output | FiraCode Source | LXGW Source |
|--------|----------------|-------------|
| SmileNerdFontMono-Regular.ttf | FiraCodeNerdFontMono-Regular | LXGWWenKaiMono-Medium |
| SmileNerdFontMono-Light.ttf | FiraCodeNerdFontMono-Light | LXGWWenKaiMono-Regular |

## Prerequisites

- Python >= 3.12
- [uv](https://docs.astral.sh/uv/)
- GNU Make
- [Typst](https://typst.app/) >= 0.14 (optional, only needed to generate preview image)

## Setup

```sh
uv sync
```

## Build

```sh
make all            # merge CJK glyphs + patch www ligature
make preview        # generate HTML glyph grid for CJK Unified (U+4E00..U+9FFF)
make live-preview   # generate interactive live text preview (both weights)
make clean          # remove build/ and preview/
```

Output fonts are written to `build/`. Preview HTML files are written to `preview/`.

To generate the preview image (requires Typst):

```sh
typst compile --font-path ./build preview.typ preview.png --ppi 288
oxipng -o max preview.png  # optional
```

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/merge.py` | Merge CJK glyphs from LXGW Wenkai into FiraCode Nerd Font Mono |
| `scripts/patch_ligatures.py` | Disable the `www` triple-ligature (modifies font in-place) |
| `scripts/render_preview.py` | Generate HTML glyph grid preview pages |
| `scripts/gen_live_preview.py` | Generate interactive live text preview with base64-embedded fonts |

### merge.py

Reads weight configuration from `config.toml`. Accepts `--weight regular` or `--weight light`.

```sh
uv run python scripts/merge.py --weight regular
```

### patch_ligatures.py

Takes a single positional argument: the TTF file path to patch in-place.

```sh
uv run python scripts/patch_ligatures.py build/SmileNerdFontMono-Regular.ttf
```

### render_preview.py

Generates an HTML glyph grid with per-codepoint cells. Fonts are referenced via relative paths (copies font files next to the output HTML). Supports optional `--compare` for side-by-side two-font comparison. `--range` can be repeated for multiple Unicode ranges.

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

Generates a self-contained HTML page with base64-embedded fonts for interactive text preview. Accepts one or more `--fonts` arguments. When multiple fonts are provided, a dropdown allows switching between them.

```sh
uv run python scripts/gen_live_preview.py \
  --fonts build/SmileNerdFontMono-Regular.ttf build/SmileNerdFontMono-Light.ttf \
  --output preview/live.html
```

## License

Upstream font licenses apply. See the respective projects for details:
- [FiraCode Nerd Font](https://github.com/ryanoasis/nerd-fonts)
- [LXGW Wenkai](https://github.com/lxgw/LxgwWenKai)
