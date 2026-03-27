# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

Smile Nerd Font Mono is a composite font build system. It merges CJK glyphs from LXGW Wenkai Mono into FiraCode Nerd Font Mono, then patches out the `www` ligature.

## Environment constraints

- **Python**: >= 3.12, managed by `uv`. No `pip`/`pip3`/`python -m pip` — use `uv` exclusively.
- **Shell**: fish. All shell commands must be fish-compatible.
- **All Python invocations** must use `uv run python`, both in the Makefile and when running scripts manually.
- **Do not modify the system Python environment.** Dependencies are isolated in the project-local `.venv/`.
- If a system-level package is missing, stop and report the error rather than attempting `emerge` or system config changes.

## Project structure

```
config.toml              # Font metadata, weight mappings, Unicode ranges
pyproject.toml           # Project dependencies (fonttools)
Makefile                 # Build orchestration (all Python calls via uv run)
assets/FiraCode/         # Upstream FiraCode Nerd Font Mono TTF files
assets/lxgw-wenkai/      # Upstream LXGW Wenkai Mono TTF files
scripts/merge.py         # CJK glyph merge (reads config.toml)
scripts/patch_ligatures.py  # www ligature disabler (in-place patching)
scripts/render_preview.py   # HTML glyph grid generator (relative font paths)
scripts/gen_live_preview.py # Interactive live preview (base64-embedded fonts)
build/                   # Output TTF files (gitignored)
preview/                 # Output HTML previews (gitignored)
```

## Key architectural details

### merge.py

- Uses `fonttools` (`fontTools.ttLib.TTFont`), not fontforge.
- Reads all configuration from `config.toml`: font paths, subfamily names, weight classes, and Unicode ranges.
- FiraCode UPM is 1950, LXGW UPM is 1000. Glyphs are scaled by `base_upm / cjk_upm` (1.95x).
- Both fonts use TrueType outlines (`glyf` table), not CFF.
- Only cmap format 4 (BMP) and format 12 (full Unicode) subtables are updated. Format 6 is skipped.
- Composite glyph dependencies are resolved recursively before insertion.
- `--weight` accepts `regular` or `light`.

### patch_ligatures.py

- Finds www-related lookups by **content matching**, not hardcoded indices.
- Looks for SingleSubst lookups mapping `w` to `w_w_w.liga` or `w.spacer`.
- Finds ChainContextSubst (format 1) rules referencing those lookups.
- Removes the SubstLookupRecord entries from the chain rules.
- Changes the SingleSubst mappings to self-map (`w` -> `w`).
- Idempotent: warns and exits cleanly if already patched.

### render_preview.py

- Generates static HTML with a glyph grid (one cell per codepoint).
- Fonts are loaded via relative `url()` in `@font-face`; font files are copied next to the HTML output.
- Supports `--compare` for side-by-side two-font rendering.

### gen_live_preview.py

- Generates self-contained HTML with fonts base64-embedded in `@font-face` `data:` URIs.
- Reads font family name from the TTF name table (nameID 1 + 2, platformID 3).
- Supports multiple `--fonts` with a dropdown to switch between them.
- Pure HTML + vanilla JS, no frameworks.

## config.toml

Defines:
- `[font]`: `family_name`, `version`
- `[weights.regular]` and `[weights.light]`: `firacode` path, `lxgw` path, `output` path, `subfamily`, `weight_class`
- `[unicode_ranges]`: named ranges in `XXXX:YYYY` hex format

**Important:** `merge.py` reads font paths from `config.toml`. The Makefile has corresponding dependency lines that must be kept in sync manually.

## Setup

```sh
uv sync
```

## Build targets

- `make all` — runs `merge` then `patch`
- `make merge` — builds both weights via `scripts/merge.py`
- `make patch` — runs `scripts/patch_ligatures.py` on both built fonts
- `make preview` — generates glyph grid HTML for CJK Unified range
- `make live-preview` — generates interactive live text preview with both weights
- `make clean` — removes `build/` and `preview/`

To generate the preview PNG (requires [Typst](https://typst.app/) >= 0.14, optional):

```sh
typst compile --font-path ./build preview.typ preview.png --ppi 288
```

### Running scripts directly

```sh
uv run python scripts/merge.py --weight regular
uv run python scripts/patch_ligatures.py build/SmileNerdFontMono-Regular.ttf

# Glyph grid with optional side-by-side comparison
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

## Coding conventions

- Scripts use `argparse` for CLI, `pathlib.Path` for paths, `logging` for output.
- Scripts have `if __name__ == "__main__"` entry points.
- Code comments and CLI help text are in English.
