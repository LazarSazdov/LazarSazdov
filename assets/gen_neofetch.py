"""Generate the animated neofetch-style card at assets/neofetch.svg.

Usage: python assets/gen_neofetch.py <svg-with-embedded-JetBrains-Mono> assets/neofetch.svg
The first argument can be the previous assets/neofetch.svg itself; the embedded fonts are reused from it.
"""
import io
import re
import sys
import random
from xml.sax.saxutils import escape

EXAMPLE_SVG = sys.argv[1]
OUT = sys.argv[2]

# Reuse the OFL-licensed JetBrains Mono woff2 embedded in the example so the card renders identically on GitHub.
src = io.open(EXAMPLE_SVG, encoding="utf-8", errors="replace").read()
fonts = re.findall(r"font-weight:(\d+);src:url\((data:font/woff2;base64,[^)]+)\)", src)
font_faces = "".join(
    f"@font-face{{font-family:JBM;font-weight:{w};src:url({u}) format('woff2')}}" for w, u in fonts
)

random.seed(7)

# ---------- layout ----------
W, H = 900, 470
FS = 14          # font size
LH = 18          # line height
CW = 8.4         # approx char width for JetBrains Mono at 14px
ART_X, ART_Y = 36, 96
INFO_X = 330
INFO_Y = 96

# ---------- ASCII pine tree ----------
tree = r"""
            ^
           /^\
          /^^^\
         /^^^^^\
        /^^^^^^^\
          /^^^\
         /^^^^^\
        /^^^^^^^\
       /^^^^^^^^^\
      /^^^^^^^^^^^\
         /^^^^^\
        /^^^^^^^\
       /^^^^^^^^^\
      /^^^^^^^^^^^\
     /^^^^^^^^^^^^^\
    /^^^^^^^^^^^^^^^\
           |||
           |||
  ~~~~~~~~~|||~~~~~~~~~
 .,:.,.:.,.:.,.:.,.:.,.
""".strip("\n").split("\n")

SHADES = ["g0", "g1", "g2"]  # dark -> light greens

def art_lines():
    out = []
    for r, line in enumerate(tree):
        y = ART_Y + r * LH
        parts = []
        for c, ch in enumerate(line):
            if ch == " ":
                continue
            x = ART_X + c * CW
            if ch == "^":
                cls = random.choice(SHADES)
                glyph = random.choice("^^^^*'")
            elif ch in "/\\":
                cls = "g1"
                glyph = ch
            elif ch == "|":
                cls = "bark"
                glyph = ch
            elif ch == "~":
                cls = "grass"
                glyph = ch
            else:
                cls = "soil"
                glyph = ch
            parts.append(f'<text class="{cls}" x="{x:.1f}" y="{y}">{escape(glyph)}</text>')
        out.append("".join(parts))
    return "\n".join(out)

# falling leaves: a handful of glyphs that drift down and fade, on staggered delays
def leaves():
    out = []
    for i in range(7):
        x = ART_X + random.uniform(40, 200)
        y = ART_Y + random.uniform(20, 180)
        delay = random.uniform(0, 7)
        dur = random.uniform(6, 9)
        glyph = random.choice(["*", "'", ".", ","])
        out.append(
            f'<text class="leaf" x="{x:.1f}" y="{y:.1f}" '
            f'style="animation-delay:{delay:.1f}s;animation-duration:{dur:.1f}s">{glyph}</text>'
        )
    return "\n".join(out)

# fireflies: tiny glowing dots that blink at different rhythms
def fireflies():
    out = []
    for i in range(10):
        x = ART_X + random.uniform(10, 230)
        y = ART_Y + random.uniform(-10, 330)
        delay = random.uniform(0, 4)
        dur = random.uniform(2.2, 4.5)
        out.append(
            f'<circle class="fly" cx="{x:.1f}" cy="{y:.1f}" r="1.6" '
            f'style="animation-delay:{delay:.1f}s;animation-duration:{dur:.1f}s"/>'
        )
    return "\n".join(out)

# ---------- neofetch info ----------
INFO = [
    ("Role",      "Backend Software Engineer @ Ominimo"),
    ("Education", "BSc Software Engineering · FTN Novi Sad"),
    ("GPA",       "9.84 / 10.00"),
    ("Location",  "Novi Sad, Serbia"),
    None,
    ("Languages", "C/C++ · Java · Python · C# · TypeScript · SQL"),
    ("Backend",   "Spring · ASP.NET · Node · FastAPI · Django · Laravel"),
    ("Frontend",  "React · Angular · TypeScript · Tailwind"),
    ("ML",        "PyTorch · TensorFlow · JAX · XGBoost · LightGBM"),
    ("Infra",     "Docker · Kubernetes · AWS · Linux · CI/CD"),
    ("Web3",      "Solidity · Foundry · Sui Move · zero-knowledge proofs"),
    None,
    ("Focus",     "backend systems · web3 · competitive programming"),
    ("Speaks",    "Serbian (native) · English (proficient)"),
]

def info_block():
    out = []
    y = INFO_Y
    # header: user@host + underline, typed in first
    out.append(f'<text class="ap" style="animation-delay:0.2s" x="{INFO_X}" y="{y}">'
               f'<tspan class="user">lazar</tspan><tspan class="dim">@</tspan><tspan class="host">novi-sad</tspan></text>')
    y += LH
    out.append(f'<text class="ap dim" style="animation-delay:0.4s" x="{INFO_X}" y="{y}">{"─" * 14}</text>')
    y += LH
    delay = 0.6
    for item in INFO:
        if item is None:
            y += LH * 0.6
            continue
        k, v = item
        out.append(
            f'<text class="ap" style="animation-delay:{delay:.1f}s" x="{INFO_X}" y="{y:.0f}">'
            f'<tspan class="key">{escape(k)}</tspan><tspan class="dim">{" " * (10 - len(k))}</tspan>'
            f'<tspan class="val">{escape(v)}</tspan></text>'
        )
        y += LH
        delay += 0.18
    # colour swatches, neofetch style
    y += LH * 0.5
    sw = ["#0b3d2e", "#14532d", "#1f8a4c", "#2ea043", "#3fb950", "#56d364", "#7ee787", "#aff5b4"]
    for i, c in enumerate(sw):
        out.append(f'<rect class="ap" style="animation-delay:{delay + i*0.06:.2f}s" '
                   f'x="{INFO_X + i*26}" y="{y - 11}" width="22" height="14" rx="3" fill="{c}"/>')
    y += LH * 1.6
    # prompt with blinking cursor
    out.append(
        f'<text class="ap" style="animation-delay:{delay + 0.6:.1f}s" x="{INFO_X}" y="{y:.0f}">'
        f'<tspan class="user">lazar</tspan><tspan class="dim">@</tspan><tspan class="host">novi-sad</tspan>'
        f'<tspan class="dim"> ❯ </tspan><tspan class="val blink">█</tspan></text>'
    )
    return "\n".join(out)

style = f"""
{font_faces}
text{{font-family:JBM,'JetBrains Mono',ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:{FS}px;white-space:pre;fill:#cfe8d6}}
.title{{fill:#7a9a86;font-size:12px}}
.user,.host{{fill:#3fb950;font-weight:700}}
.key{{fill:#56d364;font-weight:700}}
.val{{fill:#d8f0de}}
.dim{{fill:#5b7a66}}
.g0{{fill:#1f8a4c}} .g1{{fill:#2ea043}} .g2{{fill:#56d364}}
.bark{{fill:#8b5e3c;font-weight:700}}
.grass{{fill:#2ea043}}
.soil{{fill:#5b7a66}}
.leaf{{fill:#aff5b4;opacity:0;animation-name:fall;animation-timing-function:linear;animation-iteration-count:infinite}}
.fly{{fill:#aff5b4;opacity:0;animation-name:glow;animation-timing-function:ease-in-out;animation-iteration-count:infinite}}
.ap{{opacity:0;animation:ap .35s ease-out forwards}}
.blink{{animation:blink 1.06s steps(1,end) infinite}}
.sway{{transform-box:fill-box;transform-origin:50% 100%;animation:sway 6s ease-in-out infinite}}
@keyframes ap{{to{{opacity:1}}}}
@keyframes blink{{50%{{opacity:0}}}}
@keyframes fall{{0%{{opacity:0;transform:translate(0,0)}}10%{{opacity:.9}}90%{{opacity:.6}}100%{{opacity:0;transform:translate(14px,110px)}}}}
@keyframes glow{{0%,100%{{opacity:0}}50%{{opacity:.95}}}}
@keyframes sway{{0%,100%{{transform:rotate(-1deg)}}50%{{transform:rotate(1deg)}}}}
@media (prefers-reduced-motion:reduce){{*{{animation-duration:0s!important;animation-delay:0s!important}}.ap{{opacity:1}}.leaf,.fly{{opacity:.5}}}}
"""

svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="ttl dsc">
<title id="ttl">lazar@novi-sad — neofetch</title>
<desc id="dsc">neofetch-style card: an ASCII pine tree with falling leaves and fireflies next to role, education, GPA and tech stack.</desc>
<style>{style}</style>
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#0a1710"/>
    <stop offset="1" stop-color="#0f2419"/>
  </linearGradient>
  <linearGradient id="bar" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#102c1f"/>
    <stop offset="1" stop-color="#0d2218"/>
  </linearGradient>
</defs>
<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="14" fill="url(#bg)" stroke="#1f8a4c" stroke-opacity=".55"/>
<path d="M0.5 14 a14 14 0 0 1 14 -13.5 h{W-29} a14 14 0 0 1 14 13.5 v30 h-{W-1} z" fill="url(#bar)"/>
<circle cx="24" cy="22" r="6" fill="#1f8a4c"/><circle cx="44" cy="22" r="6" fill="#2ea043"/><circle cx="64" cy="22" r="6" fill="#56d364"/>
<text class="title" x="{W/2}" y="26" text-anchor="middle">lazar@novi-sad — neofetch — 100×22</text>
<g class="sway">
{art_lines()}
</g>
{leaves()}
{fireflies()}
{info_block()}
</svg>
"""
io.open(OUT, "w", encoding="utf-8", newline="\n").write(svg)
print("wrote", OUT, len(svg), "chars, fonts embedded:", len(fonts))
