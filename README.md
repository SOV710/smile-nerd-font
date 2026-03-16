# Smile Nerd Font Mono

A composite font combining **FiraCode Nerd Font Mono** (Latin, symbols, Nerd Font icons, ligatures) with **LXGW Wenkai Mono** (CJK glyphs) for a pleasant coding experience with Chinese text.

## Weights

- **Regular** — FiraCode NF Mono Regular + LXGW Wenkai Mono Regular
- **Light** — FiraCode NF Mono Light + LXGW Wenkai Mono Light

## Prerequisites

- Python >= 3.12
- [uv](https://docs.astral.sh/uv/)

## Setup

```sh
uv sync
```

## Build

```sh
make all       # merge + patch ligatures
make preview   # generate HTML preview for CJK range
make clean     # remove build/ and preview/
```

Output fonts are written to `build/`.

## License

Upstream font licenses apply. See the respective projects for details:
- [FiraCode Nerd Font](https://github.com/ryanoasis/nerd-fonts)
- [LXGW Wenkai](https://github.com/lxgw/LxgwWenKai)
