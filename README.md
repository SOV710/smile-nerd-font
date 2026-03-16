# Smile Nerd Font Mono

A composite font combining **FiraCode Nerd Font Mono** (Latin, symbols, Nerd Font icons, ligatures) with **LXGW Wenkai Mono** (CJK glyphs) for a pleasant coding experience with Chinese text.

The `www` triple-ligature from FiraCode is automatically disabled.

## Weights

| Output | FiraCode Source | LXGW Source |
|--------|----------------|-------------|
| SmileNerdFontMono-Regular.ttf | FiraCodeNerdFontMono-Regular | LXGWWenKaiMono-Regular |
| SmileNerdFontMono-Light.ttf | FiraCodeNerdFontMono-Light | LXGWWenKaiMono-Light |

## Prerequisites

- Python >= 3.12
- [uv](https://docs.astral.sh/uv/)
- GNU Make

## Setup

```sh
uv sync
```

## Build

```sh
make all       # merge CJK glyphs + patch www ligature
make preview   # generate HTML preview for CJK Unified (U+4E00..U+9FFF)
make clean     # remove build/ and preview/
```

Output fonts are written to `build/`.

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/merge.py` | Merge CJK glyphs from LXGW Wenkai into FiraCode Nerd Font |
| `scripts/patch_ligatures.py` | Disable the `www` triple-ligature |
| `scripts/render_preview.py` | Generate HTML glyph preview pages |

### Preview tool usage

```sh
# Single font preview
uv run python scripts/render_preview.py \
  --font build/SmileNerdFontMono-Regular.ttf \
  --range 4E00:9FFF \
  --output preview/cjk.html

# Side-by-side comparison
uv run python scripts/render_preview.py \
  --font build/SmileNerdFontMono-Regular.ttf \
  --compare assets/lxgw-wenkai/LXGWWenKaiMono-Regular.ttf \
  --range 4E00:4EFF \
  --output preview/compare.html
```

## License

Upstream font licenses apply. See the respective projects for details:
- [FiraCode Nerd Font](https://github.com/ryanoasis/nerd-fonts)
- [LXGW Wenkai](https://github.com/lxgw/LxgwWenKai)
