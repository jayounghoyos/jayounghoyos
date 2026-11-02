"""Generate the "latest on the bench" card (dist/activity.svg): the most recently pushed public repos.

Runs nightly in GitHub Actions with the built-in GITHUB_TOKEN; no third-party services.
Offline preview: FAKE=response.json python3 scripts/activity.py
"""
import html
from datetime import datetime, timezone

from profile_kit import ACC, BG, INK, MUTED, PANEL, SANS, USER, load, write

COUNT = 3

QUERY = """
query($login:String!){ user(login:$login){
  repositories(first:10, ownerAffiliations:OWNER, isFork:false, privacy:PUBLIC,
               orderBy:{field:PUSHED_AT, direction:DESC}){
    nodes{
      name description pushedAt isArchived
      primaryLanguage{ name }
      defaultBranchRef{ target{ ... on Commit { messageHeadline history{ totalCount } } } }
    }
  }
}}"""


def ago(iso, now):
    days = (now - datetime.fromisoformat(iso.replace("Z", "+00:00"))).days
    if days < 1:
        return "today"
    if days < 2:
        return "yesterday"
    if days < 14:
        return f"{days} days ago"
    if days < 60:
        return f"{days // 7} weeks ago"
    if days < 730:
        return f"{days // 30} months ago"
    return f"{days // 365} years ago"


def clip(text, limit):
    text = " ".join((text or "").split())
    return text if len(text) <= limit else text[:limit - 1].rstrip() + "…"


def pick(user):
    # The profile repo itself is pushed every night by this workflow, so it never counts.
    repos = [r for r in user["repositories"]["nodes"]
             if r["name"].lower() != USER.lower() and not r["isArchived"]]
    return repos[:COUNT]


def render(repos, now):
    W, x0, x1 = 900, 28, 872
    row_h, gap, top = 92, 6, 124
    H = top + len(repos) * row_h + max(len(repos) - 1, 0) * gap + 28

    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         f"<style>.s{{font-family:{SANS}}}"
         ".in{animation:in .7s cubic-bezier(.2,.7,.2,1) both}"
         "@keyframes in{from{opacity:0;transform:translateY(14px)}}"
         "@media (prefers-reduced-motion:reduce){.in{animation:none}}</style>",
         f'<rect width="{W}" height="{H}" fill="{BG}"/>',
         f'<text x="{x0}" y="66" class="s in" font-size="34" font-weight="600" fill="{INK}" '
         f'letter-spacing="-.7">Latest on the bench.</text>',
         f'<text x="{x0}" y="98" class="s in" font-size="15" fill="{INK}" style="animation-delay:.06s">'
         f'My most recently pushed repositories, refreshed every night.</text>']

    for i, r in enumerate(repos):
        y = top + i * (row_h + gap)
        first = i == 0
        fill, ink, sub = (ACC, BG, "#3b3d1e") if first else (PANEL, INK, MUTED)
        commit = (r.get("defaultBranchRef") or {}).get("target") or {}
        lang = (r.get("primaryLanguage") or {}).get("name")
        count = (commit.get("history") or {}).get("totalCount")
        facts = " · ".join(f for f in (lang, f"{count:,} commits" if count else None) if f)

        s.append(f'<g class="in" style="animation-delay:{.14 + i * .08:.2f}s">')
        s.append(f'<rect x="{x0}" y="{y}" width="{x1 - x0}" height="{row_h}" fill="{fill}"/>')
        s.append(f'<text x="{x0 + 20}" y="{y + 32}" class="s" font-size="19" font-weight="600" '
                 f'fill="{ink}">{html.escape(clip(r["name"], 48))}</text>')
        s.append(f'<text x="{x1 - 20}" y="{y + 32}" class="s" font-size="14" fill="{ink}" '
                 f'text-anchor="end">Pushed {ago(r["pushedAt"], now)}</text>')
        s.append(f'<text x="{x0 + 20}" y="{y + 55}" class="s" font-size="14" fill="{ink}">'
                 f'{html.escape(clip(commit.get("messageHeadline") or "", 84))}</text>')
        s.append(f'<text x="{x0 + 20}" y="{y + 76}" class="s" font-size="12.5" fill="{sub}">'
                 f'{html.escape(clip(r.get("description") or "", 96))}</text>')
        if facts:
            s.append(f'<text x="{x1 - 20}" y="{y + 76}" class="s" font-size="12.5" fill="{sub}" '
                     f'text-anchor="end">{html.escape(facts)}</text>')
        s.append("</g>")
    s.append("</svg>")
    return "".join(s)


if __name__ == "__main__":
    repos = pick(load(QUERY, login=USER)["user"])
    if not repos:
        raise SystemExit("no public repositories to show")
    write(render(repos, datetime.now(timezone.utc)), "dist/activity.svg")
