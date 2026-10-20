#!/usr/bin/env python3
"""Generate changes.html: a readable log of every commit with its diff.

Run from the repo root: python3 scripts/build-changes.py
CI runs it on every push to main before deploying GitHub Pages.
"""
import html
import subprocess
from pathlib import Path

MAX_LINE = 300          # minified CSS/HTML is one huge line; clip it
MAX_DIFF_LINES = 400    # per file


def git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True, check=True).stdout


def commits():
    sep, end = "\x1f", "\x1e"
    fmt = sep.join(["%H", "%h", "%an", "%aI", "%s", "%b"]) + end
    for rec in git("log", f"--format={fmt}").split(end):
        rec = rec.strip("\n")
        if rec:
            full, short, author, date, subject, body = rec.split(sep)
            yield dict(full=full, short=short, author=author, date=date, subject=subject, body=body.strip())


def file_diffs(sha):
    """Yield (path, status, added, removed, diff_lines) for one commit."""
    stats = {}
    for line in git("show", "--numstat", "--format=", sha).splitlines():
        a, r, path = line.split("\t", 2)
        stats[path] = (a, r)
    status = dict(
        reversed(line.split("\t", 1))
        for line in git("show", "--name-status", "--format=", sha).splitlines()
    )
    for path, (a, r) in stats.items():
        diff = git("show", "--format=", "--unified=2", sha, "--", path).splitlines()
        body = [l for l in diff if not l.startswith(("diff --git", "index ", "--- ", "+++ "))]
        yield path, status.get(path, "M"), a, r, body


def render_diff(lines):
    out = []
    for l in lines[:MAX_DIFF_LINES]:
        cls = {"+": "add", "-": "del", "@": "hunk"}.get(l[:1], "ctx")
        text = l if len(l) <= MAX_LINE else l[:MAX_LINE] + f"  … [+{len(l) - MAX_LINE} chars]"
        out.append(f'<span class="{cls}">{html.escape(text)}</span>')
    if len(lines) > MAX_DIFF_LINES:
        out.append(f'<span class="hunk">… {len(lines) - MAX_DIFF_LINES} more lines (see git)</span>')
    return "\n".join(out)


def main():
    remote = git("config", "--get", "remote.origin.url").strip() if subprocess.run(
        ["git", "config", "--get", "remote.origin.url"], capture_output=True).returncode == 0 else ""
    repo_url = remote.removesuffix(".git").replace("git@github.com:", "https://github.com/")
    labels = {"A": "added", "M": "modified", "D": "deleted", "R": "renamed"}

    items = []
    for c in commits():
        files = []
        for path, st, a, r, body in file_diffs(c["full"]):
            files.append(
                f'<details><summary><span class="st st-{st[0]}">{labels.get(st[0], st)}</span>'
                f'<code>{html.escape(path)}</code><span class="num"><b class="add">+{a}</b> '
                f'<b class="del">−{r}</b></span></summary><pre>{render_diff(body)}</pre></details>'
            )
        link = f'<a href="{repo_url}/commit/{c["full"]}">{c["short"]}</a>' if repo_url else c["short"]
        body = "".join(
            f"<p>{html.escape(p)}</p>" for p in c["body"].split("\n\n")
            if p and not p.startswith("Co-Authored-By")
        )
        items.append(
            f'<article><header><h2>{html.escape(c["subject"])}</h2>'
            f'<div class="meta">{link} · {html.escape(c["author"])} · '
            f'<time datetime="{c["date"]}">{c["date"][:16].replace("T", " ")}</time></div></header>'
            f'{body}<div class="files">{"".join(files)}</div></article>'
        )

    page = TEMPLATE.replace("{{ITEMS}}", "\n".join(items)).replace("{{COUNT}}", str(len(items)))
    page = page.replace("{{REPO}}", f'<a href="{repo_url}">{repo_url.split("github.com/")[-1]}</a> · ' if repo_url else "")
    Path("changes.html").write_text(page, encoding="utf-8")
    print(f"changes.html: {len(items)} commits")


TEMPLATE = """<!doctype html>
<html lang="en" dir="ltr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>Code Changes</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono&display=swap" rel="stylesheet">
<style>
:root {
  --bg: #f9fafb; --surface: #fff; --text: #1f2a37; --muted: #6c727e; --line: #e5e7eb;
  --primary: #1b8354; --add-bg: #ecfdf3; --add: #067647; --del-bg: #fef3f2; --del: #b42318; --hunk: #156fee;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --bg: #0c111b; --surface: #18212f; --text: #e5e7eb; --muted: #9da4ae; --line: #2b3643;
    --primary: #54c08a; --add-bg: #0b2a1c; --add: #75e0a7; --del-bg: #3a1311; --del: #fda29b; --hunk: #84caff;
  }
}
:root[data-theme="dark"] {
  --bg: #0c111b; --surface: #18212f; --text: #e5e7eb; --muted: #9da4ae; --line: #2b3643;
  --primary: #54c08a; --add-bg: #0b2a1c; --add: #75e0a7; --del-bg: #3a1311; --del: #fda29b; --hunk: #84caff;
}
* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--text); font: 15px/1.6 "IBM Plex Sans", system-ui, sans-serif; }
main { max-width: 960px; margin: 0 auto; padding: 32px 16px 64px; }
h1 { font-size: 28px; margin: 0 0 4px; }
.lead { color: var(--muted); margin: 0 0 32px; }
a { color: var(--primary); }
article { background: var(--surface); border: 1px solid var(--line); border-radius: 8px; padding: 20px; margin-bottom: 16px; }
article h2 { font-size: 18px; margin: 0; }
.meta { color: var(--muted); font-size: 13px; margin: 2px 0 8px; }
.meta a { font-family: "IBM Plex Mono", monospace; }
article p { margin: 8px 0; white-space: pre-line; }
.files { margin-top: 12px; border-top: 1px solid var(--line); }
details { border-bottom: 1px solid var(--line); }
summary { cursor: pointer; padding: 8px 0; display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }
summary code { font: 13px "IBM Plex Mono", monospace; overflow-wrap: anywhere; }
.num { margin-inline-start: auto; font: 12px "IBM Plex Mono", monospace; }
.num .add { color: var(--add); } .num .del { color: var(--del); }
.st { font-size: 11px; text-transform: uppercase; letter-spacing: .04em; padding: 1px 6px; border-radius: 4px; border: 1px solid currentColor; color: var(--muted); }
.st-A { color: var(--add); } .st-D { color: var(--del); }
pre { margin: 0 0 12px; padding: 8px 0; overflow-x: auto; font: 12px/1.5 "IBM Plex Mono", monospace; background: var(--bg); border-radius: 4px; }
pre span { display: block; padding: 0 12px; white-space: pre; }
pre .add { background: var(--add-bg); color: var(--add); }
pre .del { background: var(--del-bg); color: var(--del); }
pre .hunk { color: var(--hunk); }
</style>
</head>
<body>
<main>
<h1>Code changes</h1>
<p class="lead">{{REPO}}{{COUNT}} commits, newest first. Generated from git on every push. <a href="index.html">View the page →</a></p>
{{ITEMS}}
</main>
</body>
</html>
"""

if __name__ == "__main__":
    main()
