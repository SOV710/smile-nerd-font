#!/usr/bin/env python3
# render_text.py

import sys
import argparse
from PIL import Image, ImageDraw, ImageFont

def main():
    parser = argparse.ArgumentParser(description="Render text with a specified font")
    parser.add_argument("text", help="Text to render")
    parser.add_argument("-f", "--font", required=True, help="Path to .ttf/.otf font file")
    parser.add_argument("-s", "--size", type=int, default=32, help="Font size in px (default: 32)")
    parser.add_argument("-o", "--output", default="out.png", help="Output image path (default: out.png)")
    parser.add_argument("-p", "--padding", type=int, default=16, help="Padding in px (default: 16)")
    parser.add_argument("--bg", default="white", help="Background color (default: white)")
    parser.add_argument("--fg", default="black", help="Foreground color (default: black)")
    args = parser.parse_args()

    font = ImageFont.truetype(args.font, args.size)

    # 先用 dummy image 测量文本尺寸
    dummy = Image.new("RGB", (1, 1))
    draw = ImageDraw.Draw(dummy)
    bbox = draw.textbbox((0, 0), args.text, font=font)
    w = bbox[2] - bbox[0] + args.padding * 2
    h = bbox[3] - bbox[1] + args.padding * 2

    img = Image.new("RGB", (w, h), args.bg)
    draw = ImageDraw.Draw(img)
    draw.text((args.padding - bbox[0], args.padding - bbox[1]), args.text, font=font, fill=args.fg)
    img.save(args.output)
    print(f"Saved: {args.output}  ({w}x{h})")

if __name__ == "__main__":
    main()
