#!/usr/bin/env python3
"""Generate a live interactive text preview HTML page for font testing."""

import argparse
import base64
import logging
from html import escape
from pathlib import Path

from fontTools.ttLib import TTFont

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)

DEFAULT_TEXT = """\
The quick brown fox jumps over the lazy dog.
ABCDEFGHIJKLMNOPQRSTUVWXYZ 0123456789
fn main() { println!("Hello, 世界!"); }
let result = arr.filter(x => x > 0).map(x => x * 2);
你说的对，但是《原神》是由米哈游自主研发的一款全新开放世界冒险游戏。
春眠不觉晓，处处闻啼鸟。夜来风雨声，花落知多少。
www http:// https://example.com
-> => != === >= <= ++ -- ** // /* */\
"""


def get_font_family_name(font_path: Path) -> str:
    """Read the font family + subfamily from the name table."""
    try:
        font = TTFont(font_path, fontNumber=0)
        name_table = font["name"]
        family = None
        subfamily = None
        for record in name_table.names:
            if record.nameID == 1 and record.platformID == 3:
                family = record.toUnicode()
            elif record.nameID == 2 and record.platformID == 3:
                subfamily = record.toUnicode()
        font.close()
        if family and subfamily:
            return f"{family} {subfamily}"
        if family:
            return family
    except Exception:
        pass
    return font_path.stem


def font_to_base64(font_path: Path) -> str:
    """Read a font file and return its base64-encoded content."""
    data = font_path.read_bytes()
    return base64.b64encode(data).decode("ascii")


def generate_live_html(fonts: list[tuple[str, str, str]]) -> str:
    """Generate the live preview HTML.

    fonts: list of (css_family_name, display_label, base64_data)
    """
    # Build @font-face declarations
    font_faces = []
    for css_name, _, b64 in fonts:
        font_faces.append(
            f"@font-face {{\n"
            f"  font-family: '{css_name}';\n"
            f"  src: url('data:font/ttf;base64,{b64}') format('truetype');\n"
            f"}}"
        )
    font_faces_css = "\n".join(font_faces)

    # Build <option> tags
    options_html = "\n".join(
        f'        <option value="{css_name}">{escape(label)}</option>'
        for css_name, label, _ in fonts
    )

    # Use first font as default
    default_font = fonts[0][0]

    default_text_escaped = escape(DEFAULT_TEXT)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Smile Nerd Font Mono — Live Preview</title>
<style>
{font_faces_css}

* {{ margin: 0; padding: 0; box-sizing: border-box; }}

body {{
  font-family: system-ui, -apple-system, sans-serif;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f5f5;
  color: #333;
}}

header {{
  padding: 12px 20px;
  background: #1a1a2e;
  color: #e0e0e0;
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
}}

header h1 {{
  font-size: 1em;
  font-weight: 600;
  white-space: nowrap;
}}

.main {{
  display: flex;
  flex: 1;
  min-height: 0;
}}

.panel {{
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}}

.panel-left {{
  border-right: 1px solid #ddd;
  background: #fafafa;
}}

.controls {{
  padding: 12px 16px;
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
  border-bottom: 1px solid #eee;
  background: #fff;
  flex-shrink: 0;
}}

.control-group {{
  display: flex;
  align-items: center;
  gap: 6px;
}}

.control-group label {{
  font-size: 0.8em;
  color: #666;
  white-space: nowrap;
}}

.control-group select,
.control-group input[type="range"] {{
  font-size: 0.85em;
}}

.control-group .range-val {{
  font-size: 0.8em;
  color: #888;
  min-width: 3em;
  text-align: right;
  font-variant-numeric: tabular-nums;
}}

textarea {{
  flex: 1;
  padding: 16px;
  border: none;
  outline: none;
  resize: none;
  font-family: monospace;
  font-size: 14px;
  line-height: 1.6;
  background: #fafafa;
  color: #333;
}}

.preview {{
  flex: 1;
  padding: 24px;
  overflow: auto;
  white-space: pre-wrap;
  word-break: break-all;
  font-family: '{default_font}', monospace;
  font-size: 16px;
  line-height: 1.5;
  transition: background-color 0.2s, color 0.2s;
}}

.preview.dark {{
  background: #1e1e2e;
  color: #cdd6f4;
}}

.preview.light {{
  background: #ffffff;
  color: #1e1e2e;
}}

button.theme-toggle {{
  background: none;
  border: 1px solid #555;
  color: #e0e0e0;
  border-radius: 4px;
  padding: 4px 10px;
  cursor: pointer;
  font-size: 0.8em;
  white-space: nowrap;
}}

button.theme-toggle:hover {{
  background: rgba(255,255,255,0.1);
}}

@media (max-width: 768px) {{
  .main {{
    flex-direction: column;
  }}
  .panel-left {{
    border-right: none;
    border-bottom: 1px solid #ddd;
    max-height: 45vh;
  }}
}}
</style>
</head>
<body>
<header>
  <h1>Smile Nerd Font Mono</h1>
  <button class="theme-toggle" id="themeBtn">Dark</button>
</header>
<div class="main">
  <div class="panel panel-left">
    <div class="controls">
      <div class="control-group">
        <label for="fontSelect">Font</label>
        <select id="fontSelect">
{options_html}
        </select>
      </div>
      <div class="control-group">
        <label for="sizeRange">Size</label>
        <input type="range" id="sizeRange" min="12" max="72" value="16">
        <span class="range-val" id="sizeVal">16px</span>
      </div>
      <div class="control-group">
        <label for="lhRange">Line height</label>
        <input type="range" id="lhRange" min="10" max="30" value="15">
        <span class="range-val" id="lhVal">1.5</span>
      </div>
    </div>
    <textarea id="input">{default_text_escaped}</textarea>
  </div>
  <div class="panel">
    <div class="preview light" id="preview">{default_text_escaped}</div>
  </div>
</div>
<script>
(function() {{
  var input    = document.getElementById('input');
  var preview  = document.getElementById('preview');
  var fontSel  = document.getElementById('fontSelect');
  var sizeR    = document.getElementById('sizeRange');
  var sizeVal  = document.getElementById('sizeVal');
  var lhR      = document.getElementById('lhRange');
  var lhVal    = document.getElementById('lhVal');
  var themeBtn = document.getElementById('themeBtn');

  input.addEventListener('input', function() {{
    preview.textContent = input.value;
  }});

  fontSel.addEventListener('change', function() {{
    preview.style.fontFamily = "'" + fontSel.value + "', monospace";
  }});

  sizeR.addEventListener('input', function() {{
    preview.style.fontSize = sizeR.value + 'px';
    sizeVal.textContent = sizeR.value + 'px';
  }});

  lhR.addEventListener('input', function() {{
    var v = (lhR.value / 10).toFixed(1);
    preview.style.lineHeight = v;
    lhVal.textContent = v;
  }});

  var isDark = false;
  themeBtn.addEventListener('click', function() {{
    isDark = !isDark;
    preview.classList.toggle('dark', isDark);
    preview.classList.toggle('light', !isDark);
    themeBtn.textContent = isDark ? 'Light' : 'Dark';
  }});
}})();
</script>
</body>
</html>"""


def main():
    parser = argparse.ArgumentParser(
        description="Generate a live interactive text preview HTML page"
    )
    parser.add_argument(
        "--fonts", required=True, nargs="+", metavar="TTF",
        help="One or more TTF font file paths",
    )
    parser.add_argument(
        "--output", required=True,
        help="Output HTML file path",
    )
    args = parser.parse_args()

    fonts_data = []
    for font_path_str in args.fonts:
        font_path = Path(font_path_str).resolve()
        if not font_path.exists():
            log.error("Font not found: %s", font_path)
            raise SystemExit(1)

        label = get_font_family_name(font_path)
        css_name = f"preview-{font_path.stem}"
        log.info("Encoding %s (%s) ...", font_path.name, label)
        b64 = font_to_base64(font_path)
        log.info("  base64 size: %.1f MB", len(b64) / 1024 / 1024)
        fonts_data.append((css_name, label, b64))

    html = generate_live_html(fonts_data)

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(html, encoding="utf-8")
    log.info("Written %s (%.1f MB)", output, len(html) / 1024 / 1024)


if __name__ == "__main__":
    main()
