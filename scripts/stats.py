"""Generate a portfolio-styled GitHub stats card (dist/stats.svg).

Runs in GitHub Actions with the built-in GITHUB_TOKEN; no third-party services.
Offline preview: FAKE=response.json python3 scripts/stats.py
"""
import html

from profile_kit import ACC, BG, DIM, HEAT, INK, MONO, MUTED, PANEL, RULE, SANS, USER, load, write

IGNORED = {"HTML", "CSS", "SCSS", "Shell", "Jupyter Notebook", "Makefile", "CMake", "Dockerfile", "Batchfile", "G-code"}

QUERY = """
query($login:String!){ user(login:$login){
  pullRequests{totalCount}
  repositories(first:100, ownerAffiliations:OWNER, isFork:false){
    totalCount
    nodes{ stargazerCount languages(first:10, orderBy:{field:SIZE,direction:DESC}){ edges{ size node{name} } } }
  }
  contributionsCollection{
    totalCommitContributions
    contributionCalendar{ totalContributions weeks{ contributionDays{ contributionCount } } }
  }
}}"""


def render(u):
    repos = u["repositories"]
    stars = sum(n["stargazerCount"] for n in repos["nodes"])
    langs = {}
    for n in repos["nodes"]:
        for ed in n["languages"]["edges"]:
            name = ed["node"]["name"]
            if name not in IGNORED:
                langs[name] = langs.get(name, 0) + ed["size"]
    top = sorted(langs.items(), key=lambda kv: -kv[1])[:5]
    total = sum(v for _, v in top) or 1
    cc = u["contributionsCollection"]
    weeks = cc["contributionCalendar"]["weeks"][-52:]

    W, H = 900, 330
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         f'<style>.m{{font-family:{MONO};letter-spacing:.12em}}.s{{font-family:{SANS}}}</style>',
         f'<rect width="{W}" height="{H}" fill="{BG}"/>',
         f'<text x="28" y="44" class="m" font-size="11" fill="{ACC}">TELEMETRY</text>',
         f'<text x="{W-28}" y="44" class="m" font-size="11" fill="{DIM}" text-anchor="end">@{html.escape(USER).upper()}</text>']

    # The contribution calendar covers the past year; the rest are lifetime totals. Each tile says which.
    metrics = [("CONTRIBUTIONS", "PAST YEAR", cc["contributionCalendar"]["totalContributions"]),
               ("COMMITS", "PAST YEAR", cc["totalCommitContributions"]),
               ("REPOSITORIES", "ALL TIME", repos["totalCount"]),
               ("PULL REQUESTS", "ALL TIME", u["pullRequests"]["totalCount"]),
               ("STARS", "ALL TIME", stars)]
    cw = (W - 56) / len(metrics)
    for i, (k, scope, v) in enumerate(metrics):
        x = 28 + i * cw
        s.append(f'<rect x="{x:.1f}" y="64" width="{cw-10:.1f}" height="78" fill="{PANEL}" stroke="{RULE}"/>')
        s.append(f'<text x="{x+16:.1f}" y="88" class="m" font-size="9.5" fill="{DIM}">{k}</text>')
        s.append(f'<text x="{x+16:.1f}" y="126" class="s" font-size="30" font-weight="600" fill="{INK}">{v:,}</text>')
        s.append(f'<text x="{x+cw-26:.1f}" y="126" class="m" font-size="8.5" fill="{ACC if scope == "PAST YEAR" else DIM}" '
                 f'text-anchor="end">{scope}</text>')

    # language bar
    y = 172
    s.append(f'<text x="28" y="{y}" class="m" font-size="10" fill="{DIM}">LANGUAGES BY CODE SIZE · ALL REPOSITORIES</text>')
    shades = [ACC, "#9db23f", "#6b7a2a", "#57523f", "#3b3a2a"]
    x = 28.0
    bw = W - 56
    for i, (name, v) in enumerate(top):
        w = bw * v / total
        s.append(f'<rect x="{x:.1f}" y="{y+12}" width="{max(w-2,1):.1f}" height="8" fill="{shades[i]}"/>')
        x += w
    lx = 28
    for i, (name, v) in enumerate(top):
        label = f"{name} {100*v/total:.0f}%"
        width = 40 + len(label) * 7.4
        if lx + width > W - 28 + 40:  # out of room: stop rather than run off the card
            break
        s.append(f'<rect x="{lx}" y="{y+34}" width="8" height="8" fill="{shades[i]}"/>')
        s.append(f'<text x="{lx+14}" y="{y+42}" class="m" font-size="10.5" fill="{MUTED}" letter-spacing=".06em">{html.escape(label)}</text>')
        lx += width

    # heatmap
    y0, cell, gap = 244, 9, 2.5
    s.append(f'<text x="28" y="{y0-8}" class="m" font-size="10" fill="{DIM}">ACTIVITY · PAST 52 WEEKS</text>')
    mx = max([d["contributionCount"] for wk in weeks for d in wk["contributionDays"]] + [1])
    hx = 28
    step = (W - 56) / max(len(weeks), 1)
    for wi, wk in enumerate(weeks):
        for di, d in enumerate(wk["contributionDays"]):
            c = d["contributionCount"]
            lvl = 0 if c == 0 else min(4, 1 + int(3 * c / mx))
            s.append(f'<rect x="{hx + wi*step:.1f}" y="{y0 + di*(cell*0.78+gap*0.4):.1f}" width="{step-gap:.1f}" height="{cell*0.78:.1f}" fill="{HEAT[lvl]}"/>')
    s.append("</svg>")
    return "".join(s)


if __name__ == "__main__":
    write(render(load(QUERY, login=USER)["user"]), "dist/stats.svg")
