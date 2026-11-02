"""Shared palette, fonts and GitHub GraphQL client for the profile panel scripts."""
import json
import os
import urllib.request

# Palette shared by every panel.
BG, PANEL, RULE = "#0d0c08", "#16140d", "#2b2820"
INK, MUTED, DIM, ACC = "#efe7d7", "#a9a18f", "#77705f", "#c8d958"
HEAT = ["#1c1911", "#3b3d1e", "#6b7a2a", "#9db23f", "#c8d958"]

SANS = "Inter,-apple-system,'Segoe UI',Helvetica,Arial,sans-serif"
MONO = "'JetBrains Mono',ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"

USER = os.environ.get("GH_USER", "jayounghoyos")


def graphql(query, **variables):
    """Run a GraphQL query against the GitHub API and return its `data` object."""
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query, "variables": variables}).encode(),
        headers={"Authorization": f"bearer {os.environ['GITHUB_TOKEN']}",
                 "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    if data.get("errors"):
        raise SystemExit(f"GraphQL errors: {data['errors']}")
    return data["data"]


def load(query, **variables):
    """Return the query result, or a saved response when FAKE=<path.json> is set (offline preview)."""
    if os.environ.get("FAKE"):
        with open(os.environ["FAKE"], encoding="utf-8") as f:
            return json.load(f)
    return graphql(query, **variables)


def write(svg, default_out):
    out = os.environ.get("OUT", default_out)
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(svg)
    print("wrote", out)
