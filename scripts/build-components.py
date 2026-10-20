#!/usr/bin/env python3
"""Generate components.html: a visual side-by-side of each Platforms Code
component we reproduced in Tailwind (assets/ours/), with a link to that
component in our copy of SDGA's Figma components library.

Run from the repo root: python3 scripts/build-components.py
Screenshots come from scripts/shoot-components.js.
"""
import html
from pathlib import Path

# Our copy of SDGA's "Components Library - Platforms Code" (figma.com/@sdga).
# Each tile opens its component set there. Viewers need access to the file.
FIGMA = "https://www.figma.com/design/F0tqyozz6pl2xnaFUdAbiu/Components-Library---Platforms-Code--Community-?node-id="

# (official tag, Arabic name, Figma node id)
TILES = [
    ("dga-header-v2", "الترويسة", "30150-148751"),
    ("dga-header-menu-item", "عنصر القائمة", "30150-148312"),
    ("dga-header-action", "إجراء الترويسة", "30150-148445"),
    ("dga-header-search-action", "بحث الترويسة", "30150-148666"),
    ("dga-drawer-v2", "القائمة الجانبية", "30150-160799"),
    ("dga-drawer-nav-item", "عنصر القائمة الجانبية", "30150-160274"),
    ("dga-button-v2", "الزر", "407-510376"),
    ("dga-tag", "الوسم", "421-110968"),
    ("dga-tabs-v2", "التبويبات", "30150-125364"),
    ("dga-search-box", "مربع البحث", "30150-90990"),
    ("dga-inline-alert", "التنبيه", "1730-46048"),
    ("dga-card-v2", "البطاقة", "30195-10358"),
    ("dga-featured-icon", "الأيقونة المميزة", "30150-148743"),
    ("dga-icon", "الأيقونة", "30150-148742"),
    ("dga-footer", "التذييل", "30150-165937"),
]

# Wide components get a full-row tile with ours stacked above the official one
WIDE = {"dga-header-v2", "dga-tabs-v2", "dga-search-box", "dga-inline-alert", "dga-footer"}


def e(s):
    return html.escape(s, quote=True)


def figure(path, label):
    if not Path(path).exists():
        return '<div class="ph">—</div>'
    return f'<a class="shot" href="{path}"><img src="{path}" alt="{e(label)}" loading="lazy"></a>'


def main():
    tiles = "".join(f"""
  <article id="{tag}" class="{'wide' if tag in WIDE else ''}">
    <h2>{e(ar)}</h2>
    {figure(f"assets/ours/{tag}.png", ar)}
    <a class="link" href="{FIGMA}{node}" target="_blank" rel="noopener">عرض المكوّن في Figma ←</a>
  </article>""" for tag, ar, node in TILES)

    Path("components.html").write_text(f"""<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>المكوّنات</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@400;600;700&display=swap">
<script src="js/proto-bar.js" defer></script>
<style>
  body {{ margin: 0; background: #f9fafb; color: #384250; font: 15px/1.6 "IBM Plex Sans Arabic", system-ui, sans-serif; }}
  main {{ max-width: 1280px; margin: 0 auto; padding: 32px 16px 48px; }}
  h1 {{ margin: 0 0 24px; font-size: 30px; line-height: 38px; color: #1f2a37; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(min(100%, 380px), 1fr)); gap: 24px; }}
  article {{ display: flex; flex-direction: column; gap: 12px; padding: 16px; background: #fff; border: 1px solid #d2d6db; border-radius: 16px; }}
  h2 {{ margin: 0; font-size: 18px; line-height: 28px; color: #1f2a37; }}
  .shot, .ph {{ display: flex; align-items: center; justify-content: center; height: 180px; padding: 12px; background: #f3f4f6; border-radius: 8px; overflow: hidden; }}
  .shot img {{ max-width: 100%; max-height: 156px; object-fit: contain; }}
  article.wide {{ grid-column: 1 / -1; }}
  article.wide .shot {{ height: auto; min-height: 80px; }}
  article.wide .shot img {{ max-height: 420px; }}
  .link {{ align-self: flex-start; font-weight: 600; color: #1b8354; }}
  .link:focus-visible, .shot:focus-visible {{ outline: 2px solid #161616; outline-offset: 2px; }}
</style>
</head>
<body>
<main>
  <h1>المكوّنات</h1>
  <div class="grid">{tiles}
  </div>
</main>
</body>
</html>
""", encoding="utf-8")
    missing = [t for t, _, _ in TILES if not (Path(f"assets/ours/{t}.png").exists() and Path(f"assets/official/{t}.png").exists())]
    print(f"components.html: {len(TILES)} components", f"missing images: {missing}" if missing else "")


if __name__ == "__main__":
    main()
