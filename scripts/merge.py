#!/usr/bin/env python3
"""Merge CJK glyphs from LXGW Wenkai Mono into FiraCode Nerd Font Mono."""

import argparse
import copy
import logging
from pathlib import Path

try:
    import tomllib
except ImportError:
    import tomli as tomllib

from fontTools.ttLib import TTFont

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def parse_range(range_str: str) -> tuple[int, int]:
    """Parse 'XXXX:YYYY' into (start, end) integers."""
    start, end = range_str.split(":")
    return int(start, 16), int(end, 16)


def load_config() -> dict:
    config_path = PROJECT_ROOT / "config.toml"
    with open(config_path, "rb") as f:
        return tomllib.load(f)


def get_cjk_codepoints(config: dict) -> set[int]:
    """Collect all codepoints from configured Unicode ranges."""
    codepoints = set()
    for name, range_str in config["unicode_ranges"].items():
        start, end = parse_range(range_str)
        for cp in range(start, end + 1):
            codepoints.add(cp)
        log.info("Range %s: U+%04X..U+%04X (%d codepoints)", name, start, end, end - start + 1)
    return codepoints


def scale_glyph(glyph, scale_factor):
    """Scale a TrueType glyph's coordinates by scale_factor."""
    if glyph.isComposite():
        for comp in glyph.components:
            comp.x = int(round(comp.x * scale_factor))
            comp.y = int(round(comp.y * scale_factor))
    elif glyph.numberOfContours > 0:
        coords = glyph.coordinates
        for i in range(len(coords)):
            x, y = coords[i]
            coords[i] = (int(round(x * scale_factor)), int(round(y * scale_factor)))

    # Manually scale bounding box for simple glyphs
    if not glyph.isComposite() and glyph.numberOfContours > 0:
        glyph.xMin = int(round(glyph.xMin * scale_factor))
        glyph.yMin = int(round(glyph.yMin * scale_factor))
        glyph.xMax = int(round(glyph.xMax * scale_factor))
        glyph.yMax = int(round(glyph.yMax * scale_factor))


def merge_cjk_glyphs(base_path: str, cjk_path: str, output_path: str,
                      family_name: str, subfamily: str, weight_class: int,
                      cjk_codepoints: set[int]):
    """Merge CJK glyphs from cjk_font into base_font."""
    log.info("Loading base font: %s", base_path)
    base = TTFont(base_path)
    log.info("Loading CJK font: %s", cjk_path)
    cjk = TTFont(cjk_path)

    base_upm = base["head"].unitsPerEm
    cjk_upm = cjk["head"].unitsPerEm
    scale_factor = base_upm / cjk_upm
    log.info("UPM: base=%d, CJK=%d, scale=%.4f", base_upm, cjk_upm, scale_factor)

    cjk_cmap = cjk.getBestCmap()
    base_cmap = base.getBestCmap()
    base_cmap_table = base["cmap"]

    base_glyf = base["glyf"]
    cjk_glyf = cjk["glyf"]
    base_hmtx = base["hmtx"]
    cjk_hmtx = cjk["hmtx"]

    base_glyph_order = base.getGlyphOrder()
    base_glyph_set = set(base_glyph_order)

    glyphs_added = 0
    glyphs_replaced = 0
    new_glyphs = {}       # glyph_name -> glyph object
    new_hmtx = {}         # glyph_name -> (width, lsb)
    cmap_updates = {}     # codepoint -> glyph_name
    new_glyph_names = []  # to append to glyph order
    processed_cjk_glyphs = set()  # track already-copied CJK glyph names

    def ensure_glyph(cjk_gname: str):
        """Recursively copy a glyph and its composite deps from CJK font."""
        if cjk_gname in processed_cjk_glyphs:
            return
        if cjk_gname not in cjk_glyf:
            return
        processed_cjk_glyphs.add(cjk_gname)

        src = cjk_glyf[cjk_gname]
        if src.isComposite():
            for comp in src.components:
                if comp.glyphName not in base_glyph_set and comp.glyphName not in new_glyphs:
                    ensure_glyph(comp.glyphName)
                    if comp.glyphName in cjk_glyf and comp.glyphName not in new_glyphs:
                        dep = copy.deepcopy(cjk_glyf[comp.glyphName])
                        scale_glyph(dep, scale_factor)
                        new_glyphs[comp.glyphName] = dep
                        if comp.glyphName not in base_glyph_set:
                            new_glyph_names.append(comp.glyphName)
                            base_glyph_set.add(comp.glyphName)
                        w, lsb = cjk_hmtx.metrics.get(comp.glyphName, (0, 0))
                        new_hmtx[comp.glyphName] = (int(round(w * scale_factor)),
                                                     int(round(lsb * scale_factor)))

    for cp in sorted(cjk_codepoints):
        if cp not in cjk_cmap:
            continue

        cjk_glyph_name = cjk_cmap[cp]
        if cjk_glyph_name not in cjk_glyf:
            continue

        # Determine target glyph name
        if cp in base_cmap:
            target_name = base_cmap[cp]
        else:
            target_name = cjk_glyph_name
            if target_name in base_glyph_set and target_name not in new_glyphs:
                target_name = f"cjk.{cjk_glyph_name}"

        # Ensure composite deps exist
        ensure_glyph(cjk_glyph_name)

        # Copy and scale
        glyph = copy.deepcopy(cjk_glyf[cjk_glyph_name])
        scale_glyph(glyph, scale_factor)

        if target_name in base_glyph_set or target_name in new_glyphs:
            glyphs_replaced += 1
        else:
            glyphs_added += 1
            new_glyph_names.append(target_name)
            base_glyph_set.add(target_name)

        new_glyphs[target_name] = glyph
        cmap_updates[cp] = target_name

        w, lsb = cjk_hmtx.metrics.get(cjk_glyph_name, (0, 0))
        new_hmtx[target_name] = (int(round(w * scale_factor)),
                                 int(round(lsb * scale_factor)))

    log.info("Glyphs to add: %d, to replace: %d", glyphs_added, glyphs_replaced)

    # Extend glyph order
    if new_glyph_names:
        base.setGlyphOrder(base_glyph_order + new_glyph_names)

    # Insert glyphs
    for name, glyph in new_glyphs.items():
        base_glyf[name] = glyph

    # Update hmtx
    for name, metrics in new_hmtx.items():
        base_hmtx.metrics[name] = metrics

    # Update cmap subtables (only format 4 and 12)
    for subtable in base_cmap_table.tables:
        if not hasattr(subtable, "cmap"):
            continue
        if subtable.format not in (4, 12):
            continue
        for cp, glyph_name in cmap_updates.items():
            if subtable.format == 4 and cp > 0xFFFF:
                continue
            subtable.cmap[cp] = glyph_name

    # Update name table
    update_name_table(base, family_name, subfamily)

    # Update OS/2 weight class
    base["OS/2"].usWeightClass = weight_class

    # Update maxp
    base["maxp"].numGlyphs = len(base.getGlyphOrder())

    # Ensure output directory exists
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    log.info("Saving to %s", output_path)
    base.save(str(out))
    log.info("Done. Total glyphs: %d", len(base.getGlyphOrder()))


def update_name_table(font: TTFont, family_name: str, subfamily: str):
    """Update the name table with new font family and subfamily."""
    name_table = font["name"]
    ps_name = family_name.replace(" ", "") + "-" + subfamily

    updates = {
        1: family_name,
        2: subfamily,
        3: f"{family_name} {subfamily}",
        4: f"{family_name} {subfamily}",
        6: ps_name,
        16: family_name,
        17: subfamily,
    }

    for record in name_table.names:
        if record.nameID in updates:
            name_table.setName(
                updates[record.nameID],
                record.nameID,
                record.platformID,
                record.platEncID,
                record.langID,
            )


def main():
    parser = argparse.ArgumentParser(description="Merge CJK glyphs into FiraCode Nerd Font Mono")
    parser.add_argument("--weight", required=True, choices=["regular", "light"],
                        help="Weight variant to build")
    args = parser.parse_args()

    config = load_config()
    font_config = config["font"]
    weight_config = config["weights"][args.weight]

    base_path = PROJECT_ROOT / weight_config["firacode"]
    cjk_path = PROJECT_ROOT / weight_config["lxgw"]
    output_path = PROJECT_ROOT / weight_config["output"]

    cjk_codepoints = get_cjk_codepoints(config)
    log.info("Total CJK codepoints to merge: %d", len(cjk_codepoints))

    merge_cjk_glyphs(
        base_path=str(base_path),
        cjk_path=str(cjk_path),
        output_path=str(output_path),
        family_name=font_config["family_name"],
        subfamily=weight_config["subfamily"],
        weight_class=weight_config["weight_class"],
        cjk_codepoints=cjk_codepoints,
    )


if __name__ == "__main__":
    main()
