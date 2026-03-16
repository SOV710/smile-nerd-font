// Smile Nerd Font Mono — Preview Showcase
// Compile: typst compile --font-path ./build preview.typ preview.png
// (assumes SmileNerdFontMono-Regular.ttf and SmileNerdFontMono-Light.ttf are in ./build)

#let gray-bg = luma(248)
#let gray-dark = luma(60)
#let gray-mid = luma(120)
#let gray-light = luma(200)
#let gray-subtle = luma(232)
#let accent = rgb("#5b7a9d")

#set page(
  width: 800pt,
  height: auto,
  margin: (x: 48pt, y: 48pt),
  fill: gray-bg,
)

#set text(
  font: "Smile Nerd Font Mono",
  size: 11pt,
  fill: gray-dark,
)

#set par(leading: 0.7em)

// ── Title ──────────────────────────────────────────────

#align(center)[
  #block(inset: (bottom: 8pt))[
    #text(size: 36pt, weight: "regular", fill: gray-dark)[Smile Nerd Font Mono]
  ]
  #block(inset: (bottom: 4pt))[
    #text(size: 11pt, fill: gray-mid)[
      FiraCode Nerd Font × LXGW WenKai Mono
    ]
  ]
  #text(size: 9pt, fill: gray-light)[
    Programming ligatures · CJK readability · Nerd Font icons
  ]
]

#v(28pt)

// ── Helper: section card ───────────────────────────────

#let card(title, body) = block(
  width: 100%,
  fill: white,
  radius: 6pt,
  stroke: 0.5pt + gray-light,
  inset: (x: 20pt, y: 16pt),
  below: 20pt,
)[
  #text(size: 8pt, fill: accent, weight: "regular")[#upper(title)]
  #v(8pt)
  #body
]

// ── ASCII Specimen ─────────────────────────────────────

#card("Latin & Digits")[
  #text(size: 16pt)[
    ABCDEFGHIJKLMNOPQRSTUVWXYZ\
    abcdefghijklmnopqrstuvwxyz\
    0123456789
  ]
]

// ── Ligatures ──────────────────────────────────────────

#card("Programming Ligatures")[
  #text(size: 18pt)[
    #raw("-> => == != === !== >= <=")
    \
    #raw(":= :: |> <| && || !! ??")
    \
    #raw("/* */ // /// #{} </ />")
    \
    #raw("++ -- ** .. ... ..<")
  ]
  #v(8pt)
  #text(size: 9pt, fill: gray-mid)[
    Note: the `www` ligature has been intentionally disabled.
  ]
  #v(2pt)
  #text(size: 18pt)[
    #raw("www http:// ftp://")
  ]
]

// ── CJK Specimen ───────────────────────────────────────

#card("CJK 中文字形")[
  #text(size: 18pt)[
    永和九年，岁在癸丑，暮春之初，会于会稽山阴之兰亭。\
    天地玄黄，宇宙洪荒。日月盈昃，辰宿列张。
  ]
  #v(8pt)
  #text(size: 18pt)[
    你说的对，但是《原神》是由米哈游自主研发的一款全新开放世界冒险游戏。\
    游戏发生在一个被称作提瓦特的幻想世界，\
    在这里，被神选中的人将被授予神之眼，导引元素之力。\
    你将扮演一位名为旅行者的神秘角色，\
    在自由的旅行中邂逅性格各异、能力独特的同伴们，\
    和他们一起击败强敌，找回失散的亲人。\
    同时，逐步发掘原神的真相。
  ]
  #v(10pt)
  #text(size: 14pt)[
    常用汉字：的一是在不了有和人这中大为上个国我以要他\
    时来用们生到作地于出会三家工动发成方同多经然后子说
  ]
]

// ── Mixed CJK + Latin ──────────────────────────────────

#card("中英文混排 Mixed Typesetting")[
  #text(size: 14pt)[
    Rust 的所有权系统（ownership system）是它最独特的特性之一。\
    通过 `fn main()` 函数，程序从这里开始执行。\
    在 Linux 内核 6.1 中，首次引入了 Rust 语言支持。
  ]
  #v(10pt)
  #text(size: 14pt)[
    「吾輩は猫である。名前はまだ無い。」——夏目漱石
  ]
]

// ── Code Block ─────────────────────────────────────────

#card("Code Sample")[
  #block(
    width: 100%,
    fill: luma(245),
    radius: 4pt,
    inset: 12pt,
  )[
    #text(size: 12pt)[
      ```rust
      fn fibonacci(n: u64) -> u64 {
          match n {
              0 => 0,
              1 => 1,
              _ => fibonacci(n - 1) + fibonacci(n - 2),
          }
      }

      fn main() {
          let result = fibonacci(10);
          println!("第10个斐波那契数是: {result}");
          // Output: 第10个斐波那契数是: 55
      }
      ```
    ]
  ]
]

// ── Nerd Font Icons ────────────────────────────────────

#card("Nerd Font Glyphs")[
  #text(size: 9pt, fill: gray-mid)[
    If your Typst environment renders these codepoints from the font:
  ]
  #v(6pt)
  #text(size: 22pt)[
                          
  ]
  #v(4pt)
  #text(size: 9pt, fill: gray-mid)[
    (nf-linux-gentoo · nf-dev-rust · nf-dev-python · nf-dev-git · nf-md-language_rust · nf-md-code_braces · nf-fa-terminal · nf-md-arch · nf-dev-vim · nf-dev-react)
  ]
]

// ── Weight Comparison ──────────────────────────────────

#card("Weight Comparison 字重对比")[
  #text(size: 14pt, weight: "regular")[
    Regular: The quick brown fox jumps — 敏捷的棕色狐狸跳过懒狗
  ]
  #v(6pt)
  #text(size: 14pt, weight: "light")[
    Light: #h(0.72em) The quick brown fox jumps — 敏捷的棕色狐狸跳过懒狗
  ]
]

// ── Fullwidth Punctuation ──────────────────────────────

#card("标点符号 Punctuation")[
  #text(size: 14pt)[
    中文标点：，。、；：？！""''【】〈〉《》（）——……\
    全角符号：＋－＝×÷＜＞％＆＠＃＄￥
  ]
]

// ── Footer ─────────────────────────────────────────────

#v(12pt)
#align(center)[
  #text(size: 8pt, fill: gray-light)[
    Generated with Typst · github.com/SOV710/smile-nerd-font
  ]
]
