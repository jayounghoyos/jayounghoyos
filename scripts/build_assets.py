"""Build the static profile panels: assets/portfolio.svg and assets/toolchain.svg.

Run by hand after editing STACK or the copy below:

    python3 scripts/build_assets.py

Tool glyphs come from Simple Icons (CC0), pinned to one release on jsDelivr and
inlined into the SVG, because GitHub renders README images without network access.
"""
import html
import re
import urllib.request
from pathlib import Path

from profile_kit import ACC, BG, INK, MUTED, PANEL, SANS

ROOT = Path(__file__).resolve().parent.parent
ICONS = "https://cdn.jsdelivr.net/npm/simple-icons@13.21.0/icons/{}.svg"


PORTFOLIO_URL = "portafolio-web-nine-lyart.vercel.app"

# (layer, note, accent field?, [(label, simple-icons slug or None)])
STACK = [
    ("Machine learning", "Models and perception", False, [
        ("PyTorch", "pytorch"), ("TensorFlow", "tensorflow"), ("scikit-learn", "scikitlearn"),
        ("NumPy", "numpy"), ("OpenCV", "opencv")]),
    ("Robotics", "Middleware, CAD and boards", True, [
        ("ROS", "ros"), ("LeRobot", "huggingface"), ("Onshape", None),
        ("Arduino", "arduino"), ("Raspberry Pi", "raspberrypi")]),
    ("Languages", "Daily drivers", False, [
        ("Python", "python"), ("C++", "cplusplus"), ("TypeScript", "typescript"),
        ("Java", "openjdk"), ("SQL", "db")]),
    ("Web", "Front ends and dashboards", False, [
        ("Next.js", "nextdotjs"), ("React", "react"), ("Node", "nodedotjs"),
        ("Tailwind", "tailwindcss"), ("Vercel", "vercel")]),
    ("Infrastructure", "Builds and deployment", False, [
        ("Docker", "docker"), ("Postgres", "postgresql"), ("Linux", "linux"),
        ("GitHub Actions", "githubactions")]),
]

# Drawn stand-ins where Simple Icons has no mark: a CAD cube (Onshape) and a database (SQL).
DRAWN = {
    None: '<path d="M12 2.5 20.5 7.25v9.5L12 21.5 3.5 16.75v-9.5zM3.5 7.25 12 12l8.5-4.75M12 12v9.5" '
          'fill="none" stroke="{c}" stroke-width="1.8" stroke-linejoin="round"/>',
    "db": '<g fill="none" stroke="{c}" stroke-width="1.8"><ellipse cx="12" cy="5.5" rx="8" ry="3"/>'
          '<path d="M4 5.5v13c0 1.66 3.58 3 8 3s8-1.34 8-3v-13M4 12c0 1.66 3.58 3 8 3s8-1.34 8-3"/></g>',
}

_cache = {}


def glyph(slug, colour):
    if slug in DRAWN:
        return DRAWN[slug].format(c=colour)
    if slug not in _cache:
        with urllib.request.urlopen(ICONS.format(slug), timeout=20) as r:
            svg = r.read().decode()
        _cache[slug] = re.search(r'<path d="([^"]+)"', svg).group(1)
    return f'<path d="{_cache[slug]}" fill="{colour}"/>'


def style(extra=""):
    return (f"<style>.s{{font-family:{SANS}}}"
            ".in{animation:in .7s cubic-bezier(.2,.7,.2,1) both}"
            "@keyframes in{from{opacity:0;transform:translateY(14px)}}"
            "@media (prefers-reduced-motion:reduce){.in{animation:none}}"
            f"{extra}</style>")


def toolchain():
    W, x0, x1 = 900, 28, 872
    band_h, gap, top = 64, 6, 128
    chips_x, slot, icon = 256, 122, 20
    H = top + len(STACK) * band_h + (len(STACK) - 1) * gap + 28

    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         style(),
         f'<rect width="{W}" height="{H}" fill="{BG}"/>',
         f'<text x="{x0}" y="66" class="s in" font-size="34" font-weight="600" fill="{INK}" '
         f'letter-spacing="-.7">What the machines are built with.</text>',
         f'<text x="{x0}" y="98" class="s in" font-size="15" fill="{INK}" style="animation-delay:.06s">'
         'Five layers, from the model that decides to the machine it runs on.</text>']

    for i, (layer, note, accent, tools) in enumerate(STACK):
        y = top + i * (band_h + gap)
        fill, ink, sub = (ACC, BG, "#3b3d1e") if accent else (PANEL, INK, MUTED)
        s.append(f'<g class="in" style="animation-delay:{.14 + i * .08:.2f}s">')
        s.append(f'<rect x="{x0}" y="{y}" width="{x1 - x0}" height="{band_h}" fill="{fill}"/>')
        s.append(f'<text x="{x0 + 20}" y="{y + 29}" class="s" font-size="16" font-weight="600" '
                 f'fill="{ink}">{html.escape(layer)}</text>')
        s.append(f'<text x="{x0 + 20}" y="{y + 47}" class="s" font-size="12" fill="{sub}">'
                 f'{html.escape(note)}</text>')
        cy = y + band_h / 2
        for j, (label, slug) in enumerate(tools):
            cx = chips_x + j * slot
            s.append(f'<g transform="translate({cx} {cy - icon / 2:.1f}) scale({icon / 24:.4f})">'
                     f'{glyph(slug, ink)}</g>')
            s.append(f'<text x="{cx + icon + 9}" y="{cy + 4.5:.1f}" class="s" font-size="14" '
                     f'fill="{ink}">{html.escape(label)}</text>')
        s.append('</g>')
    s.append('</svg>')
    return "".join(s)


def portfolio():
    W, H = 900, 64
    return "".join([
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
        style(".go{animation:go 1.8s ease-in-out infinite alternate}"
              "@keyframes go{to{transform:translateX(6px)}}"
              "@media (prefers-reduced-motion:reduce){.go{animation:none}}"),
        f'<rect width="{W}" height="{H}" fill="{ACC}"/>',
        f'<text x="28" y="39" class="s in" font-size="18" font-weight="600" fill="{BG}" letter-spacing="-.2">'
        'Projects, CAD and write-ups live on my portfolio</text>',
        f'<text x="836" y="39" class="s in" font-size="16" fill="{BG}" '
        f'text-anchor="end" style="animation-delay:.08s">{PORTFOLIO_URL}</text>',
        f'<g class="go"><path d="M846 32h22m-8-8 8 8-8 8" fill="none" stroke="{BG}" '
        'stroke-width="2.4" stroke-linecap="square"/></g>',
        '</svg>'])


if __name__ == "__main__":
    for name, build in (("toolchain.svg", toolchain), ("portfolio.svg", portfolio)):
        path = ROOT / "assets" / name
        path.write_text(build(), encoding="utf-8")
        print("wrote", path.relative_to(ROOT))
