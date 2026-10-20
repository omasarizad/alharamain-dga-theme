#!/usr/bin/env python3
"""Generate components.html: a visual side-by-side of each Platforms Code
component we reproduced in Tailwind (assets/ours/) next to the official
component (assets/official/), with a link to the official component source.

Run from the repo root: python3 scripts/build-components.py
Screenshots come from scripts/shoot-components.js.
"""
import html
from pathlib import Path

VERSION = "0.0.53"
BROWSE = f"https://www.jsdelivr.com/package/npm/@platformscode/core?version={VERSION}&path=dist%2Fcollection%2Fcomponents%2F"

# (official tag, Arabic name, package folder)
TILES = [
    ("dga-header-v2", "الترويسة", "dga-header-v2"),
    ("dga-header-menu-item", "عنصر القائمة", "dga-header-v2"),
    ("dga-header-action", "إجراء الترويسة", "dga-header-v2"),
    ("dga-header-search-action", "بحث الترويسة", "dga-header-v2"),
    ("dga-drawer-v2", "القائمة الجانبية", "dga-drawer-v2"),
    ("dga-drawer-nav-item", "عنصر القائمة الجانبية", "dga-drawer-v2"),
    ("dga-button-v2", "الزر", "dga-button-v2"),
    ("dga-tag", "الوسم", "dga-tag"),
    ("dga-tabs-v2", "التبويبات", "dga-tabs-v2"),
    ("dga-search-box", "مربع البحث", "dga-search-box"),
    ("dga-inline-alert", "التنبيه", "dga-inline-alert"),
    ("dga-card-v2", "البطاقة", "dga-card-v2"),
    ("dga-featured-icon", "الأيقونة المميزة", "dga-featured-icon"),
    ("dga-icon", "الأيقونة", "dga-icon"),
    ("dga-notification-toast", "الإشعار", "dga-notification-toast"),
    ("dga-footer", "التذييل", "dga-footer"),
]


# Wide components get a full-row tile with ours stacked above the official one
WIDE = {"dga-header-v2", "dga-tabs-v2", "dga-search-box", "dga-inline-alert", "dga-footer", "dga-notification-toast"}


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
    <a class="link" href="{BROWSE}{folder}" target="_blank" rel="noopener">عرض المكوّن الرسمي ←</a>
  </article>""" for tag, ar, folder in TILES)

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
