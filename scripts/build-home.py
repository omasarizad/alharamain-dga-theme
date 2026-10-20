#!/usr/bin/env python3
"""Build index.html: the Al-Haramain homepage rebuilt with Platforms Code.

Run from the repo root: python3 scripts/build-home.py
Input:  data/content.json (from scripts/extract-content.py)
Output: index.html

Every UI element is a Platforms Code web component (@platformscode/core) or
layout CSS built on its tokens (css/home.css). No styles from the original site.
"""
import html
import json
from pathlib import Path

PC_CORE = "https://cdn.jsdelivr.net/npm/@platformscode/core@0.0.53/dist/core"
PC_ICONS = "https://cdn.jsdelivr.net/npm/@platformscode/icons@0.0.11/dist/svg"
ORIGIN = "https://alharamain-app-beta.it4islam.com"
LOGO = ORIGIN + "/_next/static/media/HeaderLogo.04gd8s9fp0yqt.svg"
LOGO_WHITE = ORIGIN + "/_next/static/media/Logo.2kxvzq5udaci_.svg"
HERO_IMAGE = ORIGIN + "/images/lessons-bg.webp"

PLACE_KEY = {"المسجد الحرام": "haram", "المسجد النبوي": "nabawi"}
MEDIA_ICON = {"فيديو": "video-01", "صوت": "headphones", "نص": "file-01"}
NAV_ICON = {
    "الرئيسية": "home-01", "الدروس": "teacher", "المحاضرات": "presentation-01",
    "الدورات": "certificate-01", "السلاسل العلمية": "book-open-01", "الخطب": "mosque-01",
    "التلاوات": "quran-01", "المكتبة": "library", "الحج والعمرة": "kaaba-01",
    "الأذان": "mosque-02", "المختارات": "star",
}
LESSON_GROUP = ("الدروس", "المحاضرات", "الدورات", "السلاسل العلمية")
STAT_ICON = {"إجمالي التلاوات": "quran-01", "أدعية القنوت": "prayer-rug-01", "القارئ": "user", "مصحف مسجل": "mic-01"}


def e(s):
    return html.escape(s or "", quote=True)


def icon(name, size=20, cls=""):
    """Platforms Code icon, loaded by URL from @platformscode/icons."""
    c = f' class="{cls}"' if cls else ""
    return f'<dga-icon src="{PC_ICONS}/{name}-stroke.svg" size="{size}"{c} aria-hidden="true"></dga-icon>'


FALLBACK_IMAGE = {"haram": ORIGIN + "/images/maka.webp", "nabawi": ORIGIN + "/images/madina.webp"}


def card(item, show_place=True):
    place = PLACE_KEY.get(item["place"], "")
    img = item.get("image") or ""
    if not img.startswith("http"):  # some source cards have no image
        img = FALLBACK_IMAGE.get(place, FALLBACK_IMAGE["haram"])
    meta = []
    if item.get("date"):
        meta.append(f'<span class="meta">{icon("calendar-03", 16)}<time>{e(item["date"])}</time></span>')
    if show_place and item.get("place"):
        meta.append(f'<span class="meta">{icon("mosque-01", 16)}{e(item["place"])}</span>')
    for m in item.get("media", []):
        meta.append(f'<span class="meta">{icon(MEDIA_ICON.get(m, "file-01"), 16)}{e(m)}</span>')
    if item.get("count"):
        meta.append(f'<span class="meta">{icon("book-02", 16)}{e(item["count"])}</span>')
    tags = "".join(f'<dga-tag label="{e(t)}" variant="neutral" size="sm"></dga-tag>' for t in item.get("tags", [])[:3])
    scholar = f'<p class="card-scholar text-sm-regular">{e(item["scholar"])}</p>' if item.get("scholar") else ""
    return f"""
      <dga-card-v2 class="content-card" effect="stroke" width="100%" min-width="0" data-place="{place}">
        <dga-card-content slot="card-content">
          <img class="card-img" src="{e(img)}" alt="" loading="lazy" decoding="async" width="400" height="250">
          <div class="card-meta text-xs-regular">{''.join(meta)}</div>
          <dga-card-title><a href="#" data-out-of-scope>{e(item['title'])}</a></dga-card-title>
          {scholar}
          {f'<div class="card-tags">{tags}</div>' if tags else ''}
        </dga-card-content>
      </dga-card-v2>"""


def section_head(sec, key, action=True):
    btn = (f'<dga-button-v2 class="see-all" label="عرض الكل" variant="secondary-outline" size="md" '
           f'trail-icon data-out-of-scope></dga-button-v2>') if action else ""
    return f"""
    <div class="section-head">
      <div>
        <h2 class="display-xs-bold" id="h-{key}">{e(sec['title'])}</h2>
        <p class="text-md-regular section-sub">{e(sec['subtitle'])}</p>
      </div>
      {btn}
    </div>"""


def place_tabs(key):
    return f"""
    <dga-tabs-v2 class="place-tabs" value="all" data-filter="{key}" accessible-label="تصفية حسب المكان">
      <dga-tab value="all" label="الكل"></dga-tab>
      <dga-tab value="haram" label="المسجد الحرام"></dga-tab>
      <dga-tab value="nabawi" label="المسجد النبوي"></dga-tab>
    </dga-tabs-v2>"""


def grid(items, key, **kw):
    return f'<div class="card-grid" id="grid-{key}">{"".join(card(i, **kw) for i in items)}</div>'


def build(d):
    S = d["sections"]
    primary = [n for n in d["nav"] if n not in LESSON_GROUP]
    primary.insert(1, "الدروس والمحاضرات")
    nav_items = "".join(
        f'<dga-header-menu-item label="{e(n)}" href="{"./" if i == 0 else "#"}"'
        f'{" selected" if i == 0 else " data-out-of-scope"}></dga-header-menu-item>'
        for i, n in enumerate(primary)
    )
    drawer_items = "".join(
        f'<dga-drawer-nav-item href="{"./" if i == 0 else "#"}" icon="{NAV_ICON.get(n, "circle")}"'
        f'{" active" if i == 0 else " data-out-of-scope"}>{e(n)}</dga-drawer-nav-item>'
        for i, n in enumerate(d["nav"])
    )
    stats = "".join(
        f"""<div class="stat">
          <dga-featured-icon size="lg" color="brand" variant="light" icon="{STAT_ICON.get(s['label'], 'star')}"></dga-featured-icon>
          <div><p class="display-xs-bold stat-value">+{e(s['value'])}</p><p class="text-sm-medium stat-label">{e(s['label'])}</p></div>
        </div>"""
        for s in S["tilawat"].get("stats", [])
    )
    f = d["footer"]

    return f"""<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>منصة الحرمين | نموذج كود المنصات</title>
<meta name="description" content="نموذج تجريبي غير رسمي: إعادة بناء الصفحة الرئيسية لمنصة الحرمين باستخدام مكوّنات كود المنصات">
<link rel="preconnect" href="https://cdn.jsdelivr.net">
<link rel="stylesheet" href="{PC_CORE}/core.css">
<link rel="stylesheet" href="css/home.css">
<script>
  /* @platformscode/core ships no icon SVGs; resolve every icon name to
     @platformscode/icons on the CDN. Must run before core.esm.js loads. */
  window.GDSIcons = {{ map: new (class extends Map {{
    get(k) {{ return super.get(k) || "{PC_ICONS}/" + (/-(stroke|solid)$/.test(k) ? k : k + "-stroke") + ".svg"; }}
  }})() }};
</script>
<script type="module" src="{PC_CORE}/core.esm.js"></script>
<script src="js/home.js" defer></script>
</head>
<body>
<a class="skip-link" href="#main">تخطَّ إلى المحتوى</a>

<div class="proto-banner text-sm-medium" role="note">
  نموذج تجريبي غير رسمي: الصفحة الرئيسية لمنصة الحرمين مبنية بمكوّنات كود المنصات (DGA) · ليس الموقع الرسمي
</div>

<dga-header-v2 sticky divider>
  <a class="brand" href="./" aria-label="منصة الحرمين، الرئيسية"><img src="{LOGO}" alt="منصة الحرمين" width="190" height="56"></a>
  <dga-header-menu-v2 class="desktop-nav" label="القائمة الرئيسية">{nav_items}</dga-header-menu-v2>
  <dga-header-actions label="أدوات">
    <dga-header-search-action label="بحث" placeholder="ابحث في المنصة" search-label="بحث" close-label="إغلاق البحث" speech-lang="ar"></dga-header-search-action>
    <dga-header-action class="lang-action" label="English" icon="globe" data-out-of-scope></dga-header-action>
    <dga-header-action class="menu-action" label="القائمة" icon="menu-01" aria-controls="nav-drawer"></dga-header-action>
  </dga-header-actions>
</dga-header-v2>

<dga-drawer-v2 id="nav-drawer" placement="start" size="sm" label="القائمة الرئيسية">
  <dga-drawer-header show-close-button close-label="إغلاق القائمة"><span class="text-lg-bold">منصة الحرمين</span></dga-drawer-header>
  <dga-drawer-body>
    <dga-drawer-nav label="القائمة الرئيسية">{drawer_items}</dga-drawer-nav>
  </dga-drawer-body>
</dga-drawer-v2>

<main id="main">
  <section class="hero" aria-labelledby="hero-title" style="--hero-image:url('{HERO_IMAGE}')">
    <div class="container hero-inner">
      <dga-tag label="رسالة وهداية" variant="on-color" size="md"></dga-tag>
      <h1 id="hero-title" class="display-lg-bold">منصة الحرمين</h1>
      <p class="text-xl-regular hero-sub">الدروس والمحاضرات والخطب والتلاوات من المسجد الحرام والمسجد النبوي في مكان واحد.</p>
      <form class="hero-search" role="search" data-out-of-scope-form>
        <dga-search-box placeholder="ابحث عن درس، خطبة، تلاوة، أو شيخ" size="lg" speech-lang="ar" accessible-label="ابحث في المنصة"></dga-search-box>
        <dga-button-v2 label="بحث" variant="primary" size="lg" type="submit" on-color></dga-button-v2>
      </form>
    </div>
  </section>

  <div class="container">
    <dga-inline-alert class="live-alert" type="info" colored lead-text="البث المباشر للدروس" helper-text="تابع الدروس العلمية المنقولة مباشرة من المسجد الحرام والمسجد النبوي." is-close-button="false"></dga-inline-alert>
  </div>

  <section class="section container" aria-labelledby="h-memory">
    {section_head(S['memory'], 'memory')}
    {place_tabs('memory')}
    {grid(S['memory']['items'], 'memory')}
  </section>

  <section class="section section--tinted" aria-labelledby="h-lessons">
    <div class="container">
      {section_head(S['lessons'], 'lessons')}
      {place_tabs('lessons')}
      {grid(S['lessons']['items'][:8], 'lessons')}
    </div>
  </section>

  <section class="section container" aria-labelledby="h-speeches">
    {section_head(S['speeches'], 'speeches')}
    {grid(S['speeches']['items'], 'speeches')}
  </section>

  <section class="section section--brand" aria-labelledby="h-tilawat">
    <div class="container">
      {section_head(S['tilawat'], 'tilawat')}
      <div class="stats">{stats}</div>
      {grid(S['tilawat']['items'], 'tilawat')}
    </div>
  </section>

  <section class="section container" aria-labelledby="h-selected">
    {section_head(S['selected'], 'selected')}
    <dga-tabs-v2 value="video" accessible-label="نوع المحتوى" data-out-of-scope-tabs>
      <dga-tab value="video" label="مرئي" icon="video-01"></dga-tab>
      <dga-tab value="text" label="نصي" icon="file-01"></dga-tab>
    </dga-tabs-v2>
    {grid(S['selected']['items'], 'selected', show_place=False)}
  </section>
</main>

<dga-footer id="site-footer" background="DarkGreen"
  main-title="منصة الحرمين"
  main-description="{e(f['about'])}"
  main-image="{LOGO_WHITE}"
  copyright="{e(f['copyright'])}"></dga-footer>

<script type="application/json" id="footer-data">{json.dumps({
    "groupLinks": [
        {"title": "المحتوى", "links": [{"name": n, "target": "#"} for n in d["nav"][1:6]]},
        {"title": "المزيد", "links": [{"name": n, "target": "#"} for n in d["nav"][6:]]},
        {"title": f.get("partners_title") or "شركاء النجاح", "links": [{"name": "تبيان", "target": "#"}]},
    ],
}, ensure_ascii=False)}</script>
</body>
</html>
"""


def main():
    d = json.loads(Path("data/content.json").read_text(encoding="utf-8"))
    Path("index.html").write_text(build(d), encoding="utf-8")
    n = sum(len(s["items"]) for s in d["sections"].values())
    print(f"index.html: {len(d['sections'])} sections, {n} cards")


if __name__ == "__main__":
    main()
