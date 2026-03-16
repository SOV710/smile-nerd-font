#!/usr/bin/env python3
"""Generate an HTML preview page for font glyph rendering."""

import argparse
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)


def parse_range(range_str: str) -> tuple[int, int]:
    """Parse 'XXXX:YYYY' into (start, end) integers."""
    start, end = range_str.split(":")
    return int(start, 16), int(end, 16)


def generate_html(font_path: str, ranges: list[tuple[int, int]],
                  compare_font_path: str | None = None,
                  title: str = "Font Preview") -> str:
    """Generate a self-contained HTML preview page."""
    font_name = Path(font_path).stem
    compare_name = Path(compare_font_path).stem if compare_font_path else None
    is_compare = compare_font_path is not None

    total_codepoints = sum(end - start + 1 for start, end in ranges)
    log.info("Generating preview for %d codepoints", total_codepoints)

    # Build CSS with relative font paths
    font_rel = Path(font_path).name
    css_fonts = f"""
    @font-face {{
      font-family: 'PreviewFont';
      src: url('{font_rel}') format('truetype');
    }}"""

    if is_compare:
        compare_rel = Path(compare_font_path).name
        css_fonts += f"""
    @font-face {{
      font-family: 'CompareFont';
      src: url('{compare_rel}') format('truetype');
    }}"""

    cell_width = "120px" if is_compare else "80px"

    html_parts = [f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
    {css_fonts}
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{
      font-family: system-ui, sans-serif;
      background: #1a1a2e;
      color: #e0e0e0;
      padding: 20px;
    }}
    h1 {{ margin-bottom: 10px; font-size: 1.4em; }}
    .meta {{ color: #888; margin-bottom: 20px; font-size: 0.85em; }}
    .range-header {{
      background: #16213e;
      padding: 8px 12px;
      margin: 16px 0 8px;
      border-radius: 4px;
      font-weight: bold;
      font-size: 0.9em;
    }}
    .grid {{
      display: flex;
      flex-wrap: wrap;
      gap: 4px;
    }}
    .cell {{
      width: {cell_width};
      border: 1px solid #2a2a4a;
      border-radius: 4px;
      padding: 4px;
      text-align: center;
      background: #0f0f23;
      transition: border-color 0.15s;
    }}
    .cell:hover {{ border-color: #5555aa; }}
    .glyph {{
      font-family: 'PreviewFont', sans-serif;
      font-size: 28px;
      line-height: 1.3;
      min-height: 38px;
      display: flex;
      align-items: center;
      justify-content: center;
    }}
    .compare-row {{
      display: flex;
      gap: 8px;
      justify-content: center;
    }}
    .compare-row .glyph {{ font-size: 24px; min-height: 34px; }}
    .glyph-a {{ font-family: 'PreviewFont', sans-serif; }}
    .glyph-b {{ font-family: 'CompareFont', sans-serif; }}
    .label {{ font-size: 9px; color: #666; }}
    .codepoint {{
      font-size: 10px;
      color: #555;
      font-family: monospace;
      margin-top: 2px;
    }}
</style>
</head>
<body>
<h1>{title}</h1>
<div class="meta">
  Font: <strong>{font_name}</strong>"""]

    if is_compare:
        html_parts.append(f" vs <strong>{compare_name}</strong>")

    html_parts.append(f"""<br>
  Codepoints: {total_codepoints:,}
</div>
""")

    for start, end in ranges:
        range_name = f"U+{start:04X}..U+{end:04X}"
        count = end - start + 1
        html_parts.append(
            f'<div class="range-header">{range_name} ({count:,} codepoints)</div>\n'
            '<div class="grid">\n'
        )

        for cp in range(start, end + 1):
            char = f"&#x{cp:X};"
            cp_str = f"U+{cp:04X}" if cp <= 0xFFFF else f"U+{cp:05X}"

            if is_compare:
                html_parts.append(
                    f'<div class="cell">'
                    f'<div class="compare-row">'
                    f'<div class="glyph glyph-a">{char}</div>'
                    f'<div class="glyph glyph-b">{char}</div>'
                    f'</div>'
                    f'<div class="codepoint">{cp_str}</div>'
                    f'</div>\n'
                )
            else:
                html_parts.append(
                    f'<div class="cell">'
                    f'<div class="glyph">{char}</div>'
                    f'<div class="codepoint">{cp_str}</div>'
                    f'</div>\n'
                )

        html_parts.append("</div>\n")

    html_parts.append("</body>\n</html>")
    return "".join(html_parts)


def main():
    parser = argparse.ArgumentParser(description="Generate HTML font preview page")
    parser.add_argument("--font", required=True, help="Path to primary TTF font file")
    parser.add_argument("--compare", default=None, help="Path to second TTF font for side-by-side comparison")
    parser.add_argument("--range", required=True, action="append", dest="ranges",
                        help="Unicode range as XXXX:YYYY (can be repeated)")
    parser.add_argument("--output", required=True, help="Output HTML file path")
    parser.add_argument("--title", default=None, help="Page title")
    args = parser.parse_args()

    font_path = Path(args.font).resolve()
    if not font_path.exists():
        log.error("Font not found: %s", font_path)
        raise SystemExit(1)

    compare_path = None
    if args.compare:
        compare_path = Path(args.compare).resolve()
        if not compare_path.exists():
            log.error("Compare font not found: %s", compare_path)
            raise SystemExit(1)

    ranges = [parse_range(r) for r in args.ranges]
    title = args.title or f"Preview: {font_path.stem}"

    html = generate_html(
        font_path=str(font_path),
        ranges=ranges,
        compare_font_path=str(compare_path) if compare_path else None,
        title=title,
    )

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)

    # Copy font files next to the HTML output for relative path references
    import shutil
    output_dir = output.parent
    dest_font = output_dir / font_path.name
    if dest_font.resolve() != font_path.resolve():
        shutil.copy2(font_path, dest_font)
        log.info("Copied font to %s", dest_font)

    if compare_path:
        dest_compare = output_dir / compare_path.name
        if dest_compare.resolve() != compare_path.resolve():
            shutil.copy2(compare_path, dest_compare)
            log.info("Copied compare font to %s", dest_compare)

    output.write_text(html, encoding="utf-8")
    log.info("Written %s (%.1f KB)", output, len(html) / 1024)


if __name__ == "__main__":
    main()
