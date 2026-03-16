PYTHON := uv run python

WEIGHTS := regular light
MERGED  := $(patsubst %,build/SmileNerdFontMono-%.ttf,Regular Light)
PATCHED := $(MERGED)

.PHONY: all clean merge patch preview

all: merge patch

merge: $(MERGED)

build/SmileNerdFontMono-Regular.ttf: assets/FiraCode/FiraCodeNerdFontMono-Regular.ttf assets/lxgw-wenkai/LXGWWenKaiMono-Regular.ttf scripts/merge.py config.toml
	@mkdir -p build
	$(PYTHON) scripts/merge.py --weight regular

build/SmileNerdFontMono-Light.ttf: assets/FiraCode/FiraCodeNerdFontMono-Light.ttf assets/lxgw-wenkai/LXGWWenKaiMono-Light.ttf scripts/merge.py config.toml
	@mkdir -p build
	$(PYTHON) scripts/merge.py --weight light

patch: merge
	$(PYTHON) scripts/patch_ligatures.py build/SmileNerdFontMono-Regular.ttf
	$(PYTHON) scripts/patch_ligatures.py build/SmileNerdFontMono-Light.ttf

preview: patch
	@mkdir -p preview
	$(PYTHON) scripts/render_preview.py --font build/SmileNerdFontMono-Regular.ttf --range 4E00:9FFF --output preview/cjk-regular.html

clean:
	rm -rf build/ preview/
