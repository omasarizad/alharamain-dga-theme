#!/usr/bin/env python3
"""Generate components.html: every Platforms Code component the homepage uses,
with the attributes we set, the official prop docs, a live preview and links
to the component's source in the published package, so anyone can verify the
implementation.

Run from the repo root: python3 scripts/build-components.py
Reads index.html and the @platformscode/core package (downloaded with
`npm pack` into .cache/ if it isn't there yet).
"""
import html
import json
import re
import subprocess
import tarfile
from collections import OrderedDict
from pathlib import Path

from bs4 import BeautifulSoup

VERSION = "0.0.53"
PKG = f"@platformscode/core@{VERSION}"
CDN = f"https://cdn.jsdelivr.net/npm/{PKG}"
BROWSE = f"https://www.jsdelivr.com/package/npm/@platformscode/core?version={VERSION}&path="
PC_ICONS = "https://cdn.jsdelivr.net/npm/@platformscode/icons@0.0.11/dist/svg"
CACHE = Path(".cache/platformscode-core")

REFERENCES = [
    ("Platforms Code: templates guideline (the client's reference)", "https://design.dga.gov.sa/guidelines/templates",
     "Not reachable from our network (times out), so it hasn't been verified automatically. Open it in your browser."),
    ("Platforms Code: design system site", "https://design.dga.gov.sa/", "Same as above."),
    (f"npm: {PKG}", "https://www.npmjs.com/package/@platformscode/core",
     "Official web components, MIT, published by AZM (azmx.sa). npm blocks automated checks."),
    ("npm: @platformscode/icons@0.0.11", "https://www.npmjs.com/package/@platformscode/icons",
     "Icon set used by dga-icon. License: UNLICENSED, loaded at runtime and not redistributed."),
    ("Package source browser (jsDelivr)", BROWSE + "dist%2Fcollection%2Fcomponents",
     "Verified 200. Every component's compiled source and CSS for the exact version we load."),
    ("TypeScript API: components.d.ts", f"{CDN}/dist/types/components.d.ts",
     "Verified 200. Full typed list of every component, prop and event."),
    ("Figma: Components Library: Platforms Code", "https://www.figma.com/community/file/1392264328585493958/components-library-platforms-code",
     "Official Figma community kit. Figma blocks automated checks."),
]

# Simple, self-contained previews. Complex shells (header, drawer, footer)
# link to the live homepage instead.
PREVIEW = {
    "dga-button-v2": '<dga-button-v2 label="عرض الكل" variant="secondary-outline"></dga-button-v2> <dga-button-v2 label="بحث" variant="primary"></dga-button-v2>',
    "dga-tag": '<dga-tag label="الخطب" variant="neutral" size="sm"></dga-tag> <dga-tag label="رسالة وهداية" variant="success"></dga-tag>',
    "dga-tabs-v2": '<dga-tabs-v2 value="all"><dga-tab value="all" label="الكل"></dga-tab><dga-tab value="haram" label="المسجد الحرام"></dga-tab><dga-tab value="nabawi" label="المسجد النبوي"></dga-tab></dga-tabs-v2>',
    "dga-tab": "<em>Shown inside dga-tabs-v2 above.</em>",
    "dga-search-box": '<dga-search-box placeholder="ابحث عن درس، خطبة، تلاوة، أو شيخ" speech-lang="ar" accessible-label="بحث"></dga-search-box>',
    "dga-inline-alert": '<dga-inline-alert type="info" colored lead-text="البث المباشر للدروس" helper-text="تابع الدروس العلمية المنقولة مباشرة." is-close-button="false"></dga-inline-alert>',
    "dga-featured-icon": '<dga-featured-icon size="lg" color="brand" variant="light" icon="quran-01"></dga-featured-icon> <dga-featured-icon size="lg" color="brand" variant="light" icon="mic-01"></dga-featured-icon>',
    "dga-icon": f'<dga-icon src="{PC_ICONS}/calendar-03-stroke.svg" size="24"></dga-icon> <dga-icon src="{PC_ICONS}/mosque-01-stroke.svg" size="24"></dga-icon> <dga-icon src="{PC_ICONS}/headphones-stroke.svg" size="24"></dga-icon>',
    "dga-card-v2": '<dga-card-v2 effect="stroke" width="280px"><dga-card-content slot="card-content"><img src="https://alharamain-app-beta.it4islam.com/images/maka.webp" alt="" style="width:100%;aspect-ratio:16/10;object-fit:cover;border-radius:8px"><dga-card-title>أذان الفجر</dga-card-title><p style="margin:4px 0 0;color:var(--text-primary)">الشيخ عبدالحفيظ خوج</p></dga-card-content></dga-card-v2>',
    "dga-card-content": "<em>Shown inside dga-card-v2.</em>",
    "dga-card-title": "<em>Shown inside dga-card-v2.</em>",
}
SEE_HOME = {
    "dga-header-v2": "Header at the top of the homepage",
    "dga-header-menu-v2": "Header menu (desktop, 1100px and wider)",
    "dga-header-menu-item": "Header menu items",
    "dga-header-actions": "Header actions (search, language, menu)",
    "dga-header-search-action": "Header search",
    "dga-header-action": "Header language and menu buttons",
    "dga-drawer-v2": "Mobile menu: narrow the window below 1100px and tap القائمة",
    "dga-drawer-header": "Mobile menu header",
    "dga-drawer-body": "Mobile menu body",
    "dga-drawer-nav": "Mobile menu navigation",
    "dga-drawer-nav-item": "Mobile menu items",
    "dga-footer": "Footer at the bottom of the homepage",
    "dga-notification-toast": "Click any card title on the homepage",
}


def ensure_package():
    if (CACHE / "package").exists():
        return CACHE / "package"
    CACHE.mkdir(parents=True, exist_ok=True)
    out = subprocess.run(["npm", "pack", PKG, "--silent", "--pack-destination", str(CACHE)],
                         capture_output=True, text=True, check=True).stdout.strip().splitlines()[-1]
    with tarfile.open(CACHE / out) as t:
        if hasattr(tarfile, "data_filter"):   # Python 3.12+
            t.extractall(CACHE, filter="data")
        else:
            t.extractall(CACHE)
    return CACHE / "package"


def unescape(m):
    """Decode a JSON string literal captured by a regex match (or '')."""
    if not m:
        return ""
    try:
        return json.loads(f'"{m.group(1)}"')
    except ValueError:
        return m.group(1)


def component_index(pkg):
    """tag -> {file, folder, summary, props{attr: {...}}}"""
    idx = {}
    for f in (pkg / "dist/collection/components").rglob("*.js"):
        s = f.read_text(encoding="utf-8")
        m = re.search(r'static get is\(\) \{ return "([^"]+)"', s)
        if not m:
            continue
        doc = re.search(r"/\*\*(.*?)\*/\s*export class", s, re.S)
        summary = ""
        if doc:
            lines = [re.sub(r"^\s*\* ?", "", l) for l in doc.group(1).splitlines()]
            summary = " ".join(l for l in lines if l and not l.startswith("@")).strip()
            summary = re.split(r"(?<=\.)\s", summary, maxsplit=2)
            summary = " ".join(summary[:2])
        props = {}
        pm = re.search(r"static get properties\(\) \{\s*return (\{.*?\n\s{8}\});", s, re.S)
        if pm:
            for name, body in re.findall(r'\n\s{12}"(\w+)": \{(.*?)\n\s{12}\}', pm.group(1), re.S):
                attr = re.search(r'"attribute": "([^"]+)"', body)
                typ = re.search(r'"original": "((?:[^"\\]|\\.)*)"', body)
                dflt = re.search(r'"defaultValue": "((?:[^"\\]|\\.)*)"', body)
                text = re.search(r'"docs": \{\s*"tags": \[.*?\],\s*"text": "((?:[^"\\]|\\.)*)"', body, re.S)
                key = attr.group(1) if attr else name
                props[key] = {
                    "prop": name,
                    "type": unescape(typ),
                    "default": unescape(dflt),
                    "docs": unescape(text),
                }
        rel = f.relative_to(pkg).as_posix()
        idx[m.group(1)] = {"file": rel, "folder": f.parent.relative_to(pkg).as_posix(), "summary": summary, "props": props}
    return idx


def usage(index_html):
    soup = BeautifulSoup(index_html, "html.parser")
    used = OrderedDict()
    for el in soup.find_all(re.compile(r"^dga-")):
        u = used.setdefault(el.name, {"count": 0, "attrs": OrderedDict(), "where": OrderedDict()})
        u["count"] += 1
        for k, v in el.attrs.items():
            if k.startswith("data-") or k in ("class", "slot", "id", "style"):
                continue
            val = " ".join(v) if isinstance(v, list) else v
            u["attrs"].setdefault(k, val if len(val) < 60 else val[:57] + "…")
        sec = el.find_parent("section")
        where = (sec.find(["h1", "h2"]).get_text(strip=True) if sec and sec.find(["h1", "h2"])
                 else "Header" if el.find_parent("dga-header-v2") or el.name.startswith("dga-header")
                 else "Mobile menu" if el.find_parent("dga-drawer-v2") or el.name.startswith("dga-drawer")
                 else "Footer" if el.name == "dga-footer" else "Page")
        u["where"][where] = True
    # created at runtime by js/home.js
    used["dga-notification-toast"] = {"count": 1, "attrs": OrderedDict(type="info", **{"lead-text": "خارج نطاق النموذج التجريبي", "v-postion": "bottom", "duration": "3500"}), "where": OrderedDict({"Runtime (js/home.js)": True})}
    return used


def e(s):
    return html.escape(str(s or ""), quote=True)


def render(used, idx):
    toc, blocks = [], []
    for tag, u in used.items():
        info = idx.get(tag)
        toc.append(f'<a href="#{tag}"><code>{tag}</code> <span>{u["count"]}×</span></a>')
        rows = []
        for attr, val in u["attrs"].items():
            p = (info or {}).get("props", {}).get(attr)
            if p:
                rows.append(f'<tr><td><code>{e(attr)}</code></td><td><code>{e(val) or "true"}</code></td>'
                            f'<td><code>{e(p["type"])}</code></td><td><code>{e(p["default"])}</code></td><td>{e(p["docs"])}</td></tr>')
            else:
                rows.append(f'<tr class="warn"><td><code>{e(attr)}</code></td><td><code>{e(val)}</code></td>'
                            f'<td colspan="3">Not a documented prop of this component (HTML/ARIA attribute or passed through).</td></tr>')
        table = (f'<table><thead><tr><th>Attribute we set</th><th>Value</th><th>Official type</th><th>Default</th><th>Official docs</th></tr></thead>'
                 f'<tbody>{"".join(rows)}</tbody></table>') if rows else '<p class="muted">No attributes. Defaults only.</p>'
        if tag in PREVIEW:
            preview = f'<div class="preview" dir="rtl">{PREVIEW[tag]}</div>'
        else:
            preview = f'<p class="muted">Live on the <a href="index.html">homepage</a>: {e(SEE_HOME.get(tag, "see homepage"))}.</p>'
        if info:
            src = (f'<a href="{CDN}/{info["file"]}">Source ({info["file"].split("/")[-1]})</a> · '
                   f'<a href="{BROWSE}{info["folder"].replace("/", "%2F")}">Folder on jsDelivr</a>')
            summary = f'<p>{e(info["summary"])}</p>' if info["summary"] else ""
            status = '<span class="ok">✓ Found in @platformscode/core ' + VERSION + "</span>"
        else:
            src, summary = "", ""
            status = '<span class="bad">✗ Not found in the package</span>'
        blocks.append(f"""
<section class="comp" id="{tag}">
  <header><h2><code>&lt;{tag}&gt;</code></h2>{status}</header>
  <p class="meta">Used {u['count']}× · {e(' · '.join(u['where']))}</p>
  {summary}
  {preview}
  {table}
  <p class="links">{src}</p>
</section>""")
    found = sum(1 for t in used if t in idx)
    refs = "".join(f'<li><a href="{u}">{e(t)}</a><span>{e(n)}</span></li>' for t, u, n in REFERENCES)
    return TEMPLATE.format(
        CDN=CDN, PC_ICONS=PC_ICONS, VERSION=VERSION, COUNT=len(used), FOUND=found,
        TOTAL=sum(u["count"] for u in used.values()), REFS=refs, TOC="".join(toc), BLOCKS="".join(blocks),
    )


TEMPLATE = """<!doctype html>
<html lang="en" dir="ltr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>Components Used</title>
<link rel="stylesheet" href="{CDN}/dist/core/core.css">
<script>
  window.GDSIcons = {{ map: new (class extends Map {{
    get(k) {{ return super.get(k) || "{PC_ICONS}/" + (/-(stroke|solid)$/.test(k) ? k : k + "-stroke") + ".svg"; }}
  }})() }};
</script>
<script type="module" src="{CDN}/dist/core/core.esm.js"></script>
<script src="js/proto-bar.js" defer></script>
<style>
  body {{ margin: 0; background: var(--background-body); color: var(--text-primary-paragraph); font: 15px/1.6 "IBM Plex Sans", "IBM Plex Sans Arabic", system-ui, sans-serif; }}
  main {{ max-width: 1040px; margin: 0 auto; padding: var(--spacing-8) var(--spacing-4) var(--spacing-16); }}
  h1 {{ font-size: 30px; line-height: 38px; margin: 0 0 var(--spacing-2); color: var(--text-display); }}
  .lead {{ color: var(--text-secondary-paragraph); margin: 0 0 var(--spacing-6); }}
  .summary {{ display: flex; flex-wrap: wrap; gap: var(--spacing-3); margin-bottom: var(--spacing-8); }}
  .summary div {{ background: var(--background-card); border: 1px solid var(--border-neutral-secondary); border-radius: var(--radius-md); padding: var(--spacing-3) var(--spacing-4); }}
  .summary b {{ display: block; font-size: 24px; color: var(--text-display); }}
  .panel {{ background: var(--background-card); border: 1px solid var(--border-neutral-secondary); border-radius: var(--radius-lg); padding: var(--spacing-5) var(--spacing-6); margin-bottom: var(--spacing-8); }}
  .panel h2 {{ font-size: 18px; margin: 0 0 var(--spacing-3); color: var(--text-display); }}
  .refs {{ margin: 0; padding: 0; list-style: none; }}
  .refs li {{ padding: var(--spacing-2) 0; border-top: 1px solid var(--border-neutral-tertiary); }}
  .refs li:first-child {{ border-top: 0; }}
  .refs span {{ display: block; font-size: 13px; color: var(--text-secondary-paragraph); }}
  a {{ color: var(--text-primary); }}
  .toc {{ display: flex; flex-wrap: wrap; gap: var(--spacing-2); }}
  .toc a {{ text-decoration: none; padding: 4px 10px; border: 1px solid var(--border-neutral-primary); border-radius: var(--radius-full); font-size: 13px; color: var(--text-display); background: var(--background-white); }}
  .toc a span {{ color: var(--text-secondary-paragraph); }}
  .comp {{ background: var(--background-card); border: 1px solid var(--border-neutral-secondary); border-radius: var(--radius-lg); padding: var(--spacing-5) var(--spacing-6); margin-bottom: var(--spacing-4); scroll-margin-top: 16px; }}
  .comp header {{ display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: var(--spacing-2); }}
  .comp h2 {{ margin: 0; font-size: 18px; color: var(--text-display); }}
  code {{ font-family: "IBM Plex Mono", ui-monospace, monospace; font-size: 13px; }}
  .meta, .muted {{ color: var(--text-secondary-paragraph); font-size: 13px; }}
  .ok {{ color: var(--text-success); font-size: 13px; font-weight: 600; }}
  .bad {{ color: var(--text-error); font-size: 13px; font-weight: 600; }}
  .preview {{ display: flex; flex-wrap: wrap; gap: var(--spacing-3); align-items: center; padding: var(--spacing-5); margin: var(--spacing-3) 0; background: var(--background-neutral-50); border: 1px dashed var(--border-neutral-primary); border-radius: var(--radius-md); font-family: "IBM Plex Sans Arabic", sans-serif; }}
  .preview > dga-tabs-v2, .preview > dga-search-box, .preview > dga-inline-alert {{ flex: 1 1 100%; }}
  table {{ width: 100%; border-collapse: collapse; margin-top: var(--spacing-3); font-size: 13px; display: block; overflow-x: auto; }}
  th, td {{ text-align: start; vertical-align: top; padding: 6px 8px; border-bottom: 1px solid var(--border-neutral-tertiary); }}
  th {{ color: var(--text-secondary-paragraph); font-weight: 600; white-space: nowrap; }}
  td:nth-child(2) code {{ unicode-bidi: plaintext; font-family: "IBM Plex Sans Arabic", "IBM Plex Mono", sans-serif; }}
  tr.warn td {{ background: var(--background-warning-light); }}
  .links {{ margin: var(--spacing-3) 0 0; font-size: 13px; }}
</style>
</head>
<body>
<main>
  <h1>Components used</h1>
  <p class="lead">Every Platforms Code component on the <a href="index.html">homepage</a>, generated from <code>index.html</code> and the official package <code>@platformscode/core@{VERSION}</code>. For each one: where it's used, the attributes we set checked against the official prop docs, a live preview, and a link to its source in the published package.</p>

  <div class="summary">
    <div><b>{COUNT}</b>components</div>
    <div><b>{TOTAL}</b>instances on the page</div>
    <div><b>{FOUND}/{COUNT}</b>found in the official package</div>
  </div>

  <section class="panel" aria-labelledby="refs-h">
    <h2 id="refs-h">Platforms Code references</h2>
    <ul class="refs">{REFS}</ul>
  </section>

  <section class="panel" aria-labelledby="toc-h">
    <h2 id="toc-h">Index</h2>
    <nav class="toc" aria-label="Components">{TOC}</nav>
  </section>

  {BLOCKS}
</main>
</body>
</html>
"""


def main():
    pkg = ensure_package()
    idx = component_index(pkg)
    used = usage(Path("index.html").read_text(encoding="utf-8"))
    Path("components.html").write_text(render(used, idx), encoding="utf-8")
    missing = [t for t in used if t not in idx]
    undocumented = sum(1 for t, u in used.items() for a in u["attrs"] if t in idx and a not in idx[t]["props"])
    print(f"components.html: {len(used)} components, {len(missing)} missing {missing}, {undocumented} undocumented attrs")


if __name__ == "__main__":
    main()
