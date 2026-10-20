#!/usr/bin/env python3
"""Build index.html: the Al-Haramain homepage in Tailwind v4 with Platforms Code
tokens (tailwind/platforms-code.css).

Run from the repo root: python3 scripts/build-home.py   (then: npm run build:css)
Input:  data/content.json (from scripts/extract-content.py)
Output: index.html

Each helper below reproduces one official Platforms Code component in Tailwind
utilities, matched to the computed styles of @platformscode/core@0.0.53. The
element carries data-pc="<official tag>" so components.html can compare it with
the official one. Developers copy these class lists into the real site's JSX.
"""
import html
import json
from datetime import date
from pathlib import Path

PC_ICONS = "https://cdn.jsdelivr.net/npm/@platformscode/icons@0.0.11/dist/svg"
ORIGIN = "https://alharamain-app-beta.it4islam.com"
LOGO = ORIGIN + "/_next/static/media/HeaderLogo.04gd8s9fp0yqt.svg"
TIBYAN_LOGO = ORIGIN + "/_next/static/media/ty-logo.1xz5pe5m0wvvz.svg"
HERO_IMAGE = ORIGIN + "/images/lessons-bg.webp"
FALLBACK_IMAGE = {"haram": ORIGIN + "/images/maka.webp", "nabawi": ORIGIN + "/images/madina.webp"}

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

CONTAINER = "mx-auto w-full max-w-[1280px] px-4 sm:px-6 xl:px-8"


def e(s):
    return html.escape(s or "", quote=True)


# ---- Platforms Code components in Tailwind ---------------------------------

def icon(name, size=5, cls=""):
    """Platforms Code icon (dga-icon). CSS mask, so it takes the text color."""
    url = f"{PC_ICONS}/{name}-stroke.svg"
    return (f'<span data-pc="dga-icon" aria-hidden="true" class="inline-block size-{size} shrink-0 bg-current {cls}" '
            f'style="mask:url({url}) center/contain no-repeat;-webkit-mask:url({url}) center/contain no-repeat"></span>')


def button(label, variant="primary", size="md", attrs='type="button"', lead=""):
    """dga-button-v2. md = 32px/text-sm, lg = 40px/text-md; radius-sm (4px)."""
    sizes = {"md": "h-8 px-3 text-sm", "lg": "h-10 px-4 text-md"}
    variants = {
        "primary": "bg-primary-600 text-white hover:bg-primary-700 active:bg-primary-800",
        "on-color": "bg-white text-black hover:bg-neutral-100 active:bg-neutral-200",
        "secondary-outline": "bg-transparent text-black ring-1 ring-inset ring-neutral-300 hover:bg-neutral-100 active:bg-neutral-200",
    }
    return (f'<button data-pc="dga-button-v2" {attrs} class="inline-flex shrink-0 items-center justify-center gap-1 '
            f'rounded-sm font-medium transition-colors {sizes[size]} {variants[variant]}">{lead}<span>{e(label)}</span></button>')


def tag(label, variant="neutral", size="sm"):
    """dga-tag. sm = 20px/text-2xs semibold; md = 24px/text-xs medium."""
    sizes = {"sm": "h-5 px-3 text-2xs font-semibold", "md": "h-6 px-3 text-xs font-medium"}
    variants = {
        "neutral": "border border-neutral-200 bg-neutral-50 text-neutral-800",
        "success": "border border-success-200 bg-success-50 text-success-700",
        "on-color": "bg-white/20 text-white",
    }
    return f'<span data-pc="dga-tag" class="inline-flex items-center justify-center gap-1 rounded-sm {sizes[size]} {variants[variant]}">{e(label)}</span>'


def featured_icon(name, size="lg", color="brand"):
    """dga-featured-icon (circle, light). xl = 56px/28px icon, lg = 48px/24px, md = 40px/20px."""
    box, ico = {"xl": ("size-14", 7), "lg": ("size-12", 6), "md": ("size-10", 5)}[size]
    colors = {"brand": "bg-primary-50 text-primary-600", "info": "bg-info-50 text-info-700"}[color]
    return f'<span data-pc="dga-featured-icon" class="inline-flex {box} shrink-0 items-center justify-center rounded-full {colors}">{icon(name, ico)}</span>'


def tabs(items, key, selected, label, out_of_scope=()):
    """dga-tabs-v2 + dga-tab. 44px row, 3px primary underline on the selected tab."""
    out = []
    for value, text, ico in items:
        sel = value == selected
        extra = " data-out-of-scope" if value in out_of_scope else ""
        out.append(
            f'<button data-pc="dga-tab" type="button" role="tab" aria-selected="{str(sel).lower()}" data-value="{value}"{extra} '
            'class="relative inline-flex shrink-0 items-center gap-2 px-4 py-3 text-sm font-medium text-neutral-600 transition-colors '
            'hover:bg-neutral-100 hover:text-black aria-selected:font-semibold aria-selected:text-black '
            'after:absolute after:inset-x-4 after:bottom-0 after:h-[3px] after:rounded-full after:bg-transparent '
            'hover:after:bg-neutral-300 aria-selected:after:bg-primary-600 aria-selected:hover:bg-transparent '
            'focus-visible:outline-3 focus-visible:-outline-offset-3 focus-visible:outline-black">'
            f'{icon(ico, 4) if ico else ""}{e(text)}</button>')
    return (f'<div data-pc="dga-tabs-v2" role="tablist" aria-label="{e(label)}" data-filter="{key}" '
            f'class="mb-6 flex overflow-x-auto border-b border-neutral-200">{"".join(out)}</div>')


def search_box(placeholder, size="lg", name="q"):
    """dga-search-box. lg = 40px, 1px neutral-400 border, radius-sm, 20px icons."""
    h = {"lg": "h-10", "md": "h-8"}[size]
    return (f'<label data-pc="dga-search-box" class="flex {h} w-full items-center gap-2 rounded-sm border border-neutral-400 bg-white ps-4 pe-2 '
            'text-black focus-within:border-primary-600 focus-within:ring-3 focus-within:ring-primary-500/20">'
            f'{icon("search-01", 5)}<span class="sr-only">{e(placeholder)}</span>'
            f'<input type="search" name="{name}" placeholder="{e(placeholder)}" '
            'class="h-full min-w-0 flex-1 bg-transparent text-md text-neutral-700 placeholder:text-neutral-500 focus:outline-none">'
            f'<span title="بحث صوتي">{icon("mic-01", 5)}</span></label>')


def inline_alert(title, text, color="info"):
    """dga-inline-alert (colored info). radius-md, 16px/24px padding, md featured icon."""
    return (f'<div data-pc="dga-inline-alert" role="status" class="flex items-start gap-3 rounded-md border border-info-200 bg-info-25 px-6 py-4 text-neutral-700">'
            f'{featured_icon("live-streaming-02", "md", color)}'
            f'<div><p class="mb-1 text-md font-semibold">{e(title)}</p><p class="text-sm">{e(text)}</p></div></div>')


def card(item, show_place=True):
    """dga-card-v2 (stroke) + dga-card-content + dga-card-title. radius-lg, 1px neutral-300, p-4."""
    place = PLACE_KEY.get(item["place"], "")
    img = item.get("image") or ""
    if not img.startswith("http"):  # some source cards have no image
        img = FALLBACK_IMAGE.get(place, FALLBACK_IMAGE["haram"])
    meta = []
    if item.get("date"):
        meta.append(f'<span class="inline-flex items-center gap-1">{icon("calendar-03", 4)}<time>{e(item["date"])}</time></span>')
    if show_place and item.get("place"):
        meta.append(f'<span class="inline-flex items-center gap-1">{icon("mosque-01", 4)}{e(item["place"])}</span>')
    for m in item.get("media", []):
        meta.append(f'<span class="inline-flex items-center gap-1">{icon(MEDIA_ICON.get(m, "file-01"), 4)}{e(m)}</span>')
    if item.get("count"):
        meta.append(f'<span class="inline-flex items-center gap-1">{icon("book-02", 4)}{e(item["count"])}</span>')
    tags = "".join(tag(t) for t in item.get("tags", [])[:3])
    scholar = f'<p class="mt-1 text-sm text-primary-600">{e(item["scholar"])}</p>' if item.get("scholar") else ""
    return f"""
      <article data-pc="dga-card-v2" data-place="{place}" class="flex h-full min-w-0 flex-col rounded-lg border border-neutral-300 bg-white p-4 transition-shadow hover:shadow-md">
        <div data-pc="dga-card-content" class="flex flex-1 flex-col">
          <img src="{e(img)}" alt="" loading="lazy" decoding="async" width="400" height="250" class="aspect-[16/10] w-full rounded-md bg-neutral-100 object-cover">
          <div class="mt-3 flex flex-wrap gap-x-3 gap-y-1 text-xs text-neutral-500">{''.join(meta)}</div>
          <h3 data-pc="dga-card-title" class="mt-3 text-lg font-bold text-neutral-700">
            <a href="#" data-out-of-scope class="line-clamp-2 hover:text-primary-600 hover:underline hover:underline-offset-3">{e(item['title'])}</a>
          </h3>
          {scholar}
          {f'<div class="mt-auto flex flex-wrap gap-1 pt-3">{tags}</div>' if tags else ''}
        </div>
      </article>"""


# ---- Page sections -----------------------------------------------------------

def section_head(sec, key):
    """Section title as in the SDGA Home Page Template: display-sm bold title and a
    text-md description, with the secondary action at the far end."""
    return f"""
    <div class="mb-8 flex flex-col items-start justify-between gap-4 sm:flex-row">
      <div class="flex flex-col gap-6">
        <h2 id="h-{key}" class="text-display-sm font-bold text-black">{e(sec['title'])}</h2>
        <p class="max-w-[964px] text-md text-black">{e(sec['subtitle'])}</p>
      </div>
      {button("عرض الكل", "secondary-outline", "lg", 'type="button" data-out-of-scope')}
    </div>"""


PLACE_TABS = [("all", "الكل", None), ("haram", "المسجد الحرام", None), ("nabawi", "المسجد النبوي", None)]


def grid(items, key, **kw):
    return (f'<div id="grid-{key}" class="grid grid-cols-[repeat(auto-fill,minmax(min(100%,272px),1fr))] gap-6">'
            f'{"".join(card(i, **kw) for i in items)}</div>')


def header(d):
    """dga-header-v2: 72px, white, bottom divider, sticky. Selected item is filled primary-600."""
    primary = [n for n in d["nav"] if n not in LESSON_GROUP]
    primary.insert(1, "الدروس والمحاضرات")
    items = "".join(
        f'<li><a data-pc="dga-header-menu-item" href="{"./" if i == 0 else "#"}"'
        + (' aria-current="page" class="inline-flex h-18 items-center rounded-xs bg-primary-600 px-6 text-md font-semibold whitespace-nowrap text-white"'
           if i == 0 else
           ' data-out-of-scope class="inline-flex h-18 items-center rounded-xs px-6 text-md font-medium whitespace-nowrap text-black hover:bg-neutral-100"')
        + f'>{e(n)}</a></li>'
        for i, n in enumerate(primary)
    )
    action = "inline-flex h-18 items-center gap-1 rounded-xs px-3 text-md font-medium text-black hover:bg-neutral-100 sm:px-6"
    return f"""
<header data-pc="dga-header-v2" class="sticky top-0 z-40 border-b border-neutral-200 bg-white">
  <div class="flex h-18 items-center justify-between gap-4 px-4 xl:px-8">
    <a href="./" class="shrink-0" aria-label="منصة الحرمين، الرئيسية"><img src="{LOGO}" alt="منصة الحرمين" width="190" height="56" class="h-10 w-auto sm:h-12"></a>
    <nav data-pc="dga-header-menu-v2" aria-label="القائمة الرئيسية" class="hidden flex-1 min-[1100px]:block">
      <ul class="flex">{items}</ul>
    </nav>
    <div data-pc="dga-header-actions" role="group" aria-label="أدوات" class="flex items-center">
      <button data-pc="dga-header-search-action" type="button" data-out-of-scope class="{action}">{icon("search-01", 6)}<span class="max-sm:sr-only">بحث</span></button>
      <button data-pc="dga-header-action" type="button" data-out-of-scope class="{action} max-sm:hidden">{icon("globe", 6)}<span>English</span></button>
      <button data-pc="dga-header-action" type="button" id="menu-button" aria-controls="nav-drawer" aria-expanded="false" class="{action} min-[1100px]:hidden">{icon("menu-01", 6)}<span>القائمة</span></button>
    </div>
  </div>
</header>"""


def drawer(d):
    """dga-drawer-v2 (start, sm = 320px) + dga-drawer-nav-item (36px, text-sm semibold, 6px indicator)."""
    items = "".join(
        f'<li><a data-pc="dga-drawer-nav-item" href="{"./" if i == 0 else "#"}"'
        + (' aria-current="page"' if i == 0 else " data-out-of-scope")
        + ' class="group flex h-9 items-center gap-2 rounded-sm px-4 text-sm font-semibold text-neutral-800 hover:bg-neutral-100 aria-[current=page]:bg-primary-50 aria-[current=page]:text-primary-700">'
        + '<span class="h-6 w-1.5 rounded-full bg-transparent group-aria-[current=page]:bg-primary-600"></span>'
        + f'{icon(NAV_ICON.get(n, "circle"), 4)}<span>{e(n)}</span></a></li>'
        for i, n in enumerate(d["nav"])
    )
    return f"""
<dialog data-pc="dga-drawer-v2" id="nav-drawer" aria-labelledby="drawer-title"
  class="fixed inset-y-0 start-0 m-0 h-dvh max-h-none w-80 max-w-[calc(100%-48px)] bg-white text-neutral-800 shadow-2xl backdrop:bg-black/50">
  <div data-pc="dga-drawer-header" class="flex items-center justify-between border-b border-neutral-200 px-6 py-4">
    <p id="drawer-title" class="text-lg font-bold">منصة الحرمين</p>
    <button type="button" data-close class="inline-flex size-8 items-center justify-center rounded-sm text-black hover:bg-neutral-100" aria-label="إغلاق القائمة">{icon("multiplication-sign", 5)}</button>
  </div>
  <nav data-pc="dga-drawer-nav" aria-label="القائمة الرئيسية" class="p-6"><ul class="flex flex-col gap-1">{items}</ul></nav>
</dialog>"""


def footer(d):
    """Footer, as in the SDGA Figma library (UI Shell - Footer, RTL, Dark green).

    Link columns, a contact column (social media + accessibility tools with
    32px outline icon buttons), then a legal row: underlined links, copyright,
    privacy and terms, and the logo on white. Below 640px the contact column
    becomes one row, and the legal row stacks and centers.
    Dark green = --colors-green-900 -> bg-success-900.
    """
    f = d["footer"]
    groups = [
        ("المحتوى", d["nav"][1:6]),
        ("المزيد", d["nav"][6:]),
        (f.get("partners_title") or "شركاء النجاح", ["تبيان"]),
    ]
    social = [("new-twitter", "إكس"), ("youtube", "يوتيوب"), ("instagram", "إنستغرام"), ("snapchat", "سناب شات")]
    a11y = [("eye", "تباين الألوان"), ("search-add", "تكبير الخط"), ("search-minus", "تصغير الخط")]
    legal_links = ["عن المنصة", "اتصل بنا", "الأسئلة الشائعة", "خريطة الموقع"]

    def label(text):
        return f'<p class="border-b border-white/30 pb-2 text-md font-semibold sm:font-medium">{e(text)}</p>'

    def links(names, cls=""):
        return "".join(f'<li><a href="#" data-out-of-scope class="hover:underline {cls}">{e(n)}</a></li>' for n in names)

    def icon_buttons(items):
        return "".join(
            f'<li><a href="#" data-out-of-scope aria-label="{e(n)}" class="inline-flex size-8 items-center justify-center rounded-sm border border-white/30 hover:bg-white/10">{icon(i, 5)}</a></li>'
            for i, n in items
        )

    cols = "".join(
        f'<div class="flex min-w-[180px] flex-1 flex-col gap-2">{label(t)}<ul class="flex flex-col gap-2 text-sm">{links(names)}</ul></div>'
        for t, names in groups
    )
    contact = "".join(
        f'<div class="flex flex-1 flex-col gap-2">{label(t)}<ul class="flex flex-wrap gap-2">{icon_buttons(items)}</ul></div>'
        for t, items in (("تواصل معنا", social), ("أدوات الإتاحة والوصول", a11y))
    )
    return f"""
<footer data-pc="dga-footer" class="bg-success-900 px-4 text-white sm:px-8">
  <div class="mx-auto flex max-w-[1280px] flex-col gap-10 pt-10 pb-6 sm:gap-12">
    <nav aria-label="روابط التذييل" class="flex flex-wrap gap-6 py-4 sm:pb-10">
      {cols}
      <div class="flex w-full flex-row-reverse gap-8 sm:w-auto sm:min-w-[180px] sm:flex-1 sm:flex-col">{contact}</div>
    </nav>
    <div class="flex flex-col items-center gap-10 py-4 sm:flex-row sm:gap-6">
      <div class="flex w-full flex-col items-center gap-8 sm:flex-1 sm:items-start sm:gap-6">
        <ul class="flex flex-wrap justify-center gap-4 text-sm">{links(legal_links, "underline")}</ul>
        <div class="flex flex-col items-center gap-2 text-center sm:items-start sm:text-start">
          <p class="text-sm font-semibold">{e(f['copyright'])}</p>
          <ul class="flex flex-wrap gap-4 text-sm">{links(["سياسة الخصوصية", "الشروط والأحكام"])}</ul>
        </div>
      </div>
      <div class="flex shrink-0 items-center bg-white px-1 py-[5px]"><img src="{LOGO}" alt="منصة الحرمين" class="h-8 w-auto"></div>
    </div>
  </div>
</footer>"""


def build(d):
    S = d["sections"]
    stats = "".join(
        f"""<div class="flex flex-col items-center gap-6 rounded-lg p-4 text-center">
          {featured_icon(STAT_ICON.get(s['label'], 'star'), "xl")}
          <div class="flex flex-col gap-2"><p class="text-display-lg tracking-tight text-primary-800 tabular-nums">+{e(s['value'])}</p><p class="text-md text-neutral-800">{e(s['label'])}</p></div>
        </div>"""
        for s in S["tilawat"].get("stats", [])
    )
    return f"""<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>منصة الحرمين | نموذج كود المنصات</title>
<meta name="description" content="نموذج تجريبي غير رسمي: الصفحة الرئيسية لمنصة الحرمين بأسلوب كود المنصات (Tailwind)">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@400;500;600;700&display=swap">
<link rel="stylesheet" href="css/app.css">
<script src="js/home.js" defer></script>
<script src="js/proto-bar.js" defer></script>
</head>
<body class="bg-white font-sans text-neutral-700 antialiased">
<a href="#main" class="sr-only z-50 rounded-sm bg-primary-600 px-4 py-2 text-white focus:not-sr-only focus:fixed focus:start-4 focus:top-2">تخطَّ إلى المحتوى</a>

<div role="note" class="flex min-h-8 items-center bg-neutral-100 px-4 py-1.5 text-sm font-medium text-black sm:px-8">
  نموذج تجريبي غير رسمي لمنصة الحرمين بأسلوب كود المنصات · ليس الموقع الرسمي
</div>
{header(d)}
{drawer(d)}

<main id="main">
  <section aria-labelledby="hero-title" class="relative isolate bg-primary-900 bg-cover bg-center text-white"
    style="background-image:linear-gradient(to left,rgb(16 70 49/.92),rgb(20 87 58/.75)),url('{HERO_IMAGE}')">
    <div class="{CONTAINER} flex flex-col items-start gap-4 pt-10 pb-16 sm:pt-16 sm:pb-24">
      {tag("رسالة وهداية", "on-color", "md")}
      <h1 id="hero-title" class="text-display-md font-bold sm:text-display-lg">منصة الحرمين</h1>
      <p class="max-w-[46ch] text-xl text-white/80">الدروس والمحاضرات والخطب والتلاوات من المسجد الحرام والمسجد النبوي في مكان واحد.</p>
      <form role="search" class="mt-4 flex w-full max-w-[720px] flex-col gap-2 sm:flex-row">
        {search_box("ابحث عن درس، خطبة، تلاوة، أو شيخ")}
        {button("بحث", "on-color", "lg", 'type="submit"')}
      </form>
    </div>
  </section>

  <div class="{CONTAINER} relative -mt-8">
    {inline_alert("البث المباشر للدروس", "تابع الدروس العلمية المنقولة مباشرة من المسجد الحرام والمسجد النبوي.")}
  </div>

  <section aria-labelledby="h-memory" class="{CONTAINER} py-10 sm:py-16">
    {section_head(S['memory'], 'memory')}
    {tabs(PLACE_TABS, 'memory', 'all', 'تصفية حسب المكان')}
    {grid(S['memory']['items'], 'memory')}
  </section>

  <section aria-labelledby="h-lessons" class="bg-neutral-50 py-10 sm:py-16">
    <div class="{CONTAINER}">
      {section_head(S['lessons'], 'lessons')}
      {tabs(PLACE_TABS, 'lessons', 'all', 'تصفية حسب المكان')}
      {grid(S['lessons']['items'][:8], 'lessons')}
    </div>
  </section>

  <section aria-labelledby="h-speeches" class="{CONTAINER} py-10 sm:py-16">
    {section_head(S['speeches'], 'speeches')}
    {grid(S['speeches']['items'], 'speeches')}
  </section>

  <section aria-labelledby="h-tilawat" class="bg-neutral-50 py-10 sm:py-16">
    <div class="{CONTAINER}">
      {section_head(S['tilawat'], 'tilawat')}
      <div class="mx-auto mb-10 grid max-w-[992px] grid-cols-2 gap-4 sm:grid-cols-4 sm:gap-8">{stats}</div>
      {grid(S['tilawat']['items'], 'tilawat')}
    </div>
  </section>

  <section aria-labelledby="h-selected" class="{CONTAINER} py-10 sm:py-16">
    {section_head(S['selected'], 'selected')}
    {tabs([("video", "مرئي", "video-01"), ("text", "نصي", "file-01")], 'selected', 'video', 'نوع المحتوى', out_of_scope=("text",))}
    {grid(S['selected']['items'], 'selected', show_place=False)}
  </section>

  <section aria-labelledby="h-partners" class="bg-neutral-50 py-10">
    <div class="{CONTAINER} flex flex-col gap-8">
      <h2 id="h-partners" class="text-display-sm font-bold text-black">{e(d['footer'].get('partners_title') or 'شركاء النجاح')}</h2>
      <ul class="flex flex-wrap gap-4">
        <li><a href="#" data-out-of-scope class="flex h-[120px] w-[136px] items-center justify-center rounded-lg border border-neutral-300 bg-white p-4 hover:border-neutral-400"><img src="{TIBYAN_LOGO}" alt="تبيان" width="104" height="59" class="w-[104px]"></a></li>
      </ul>
    </div>
  </section>

  <div class="bg-white py-4">
    <p class="{CONTAINER} text-sm text-black">تاريخ آخر تعديل: {date.today():%d/%m/%Y}</p>
  </div>
</main>
{footer(d)}

<div id="toast-region" aria-live="polite" class="pointer-events-none fixed inset-x-4 bottom-24 z-50 flex justify-end sm:inset-x-8"></div>
<template id="toast-template">
  <div data-pc="dga-notification-toast" role="status" class="pointer-events-auto flex w-full max-w-[484px] items-start gap-3 rounded-md bg-white px-6 py-4 shadow-3xl">
    {featured_icon("information-circle", "md", "info")}
    <div class="flex-1"><p class="text-md font-semibold text-neutral-800">خارج نطاق النموذج التجريبي</p>
      <p class="text-sm text-neutral-700">هذا النموذج يشمل الصفحة الرئيسية فقط.</p>
      <p class="text-start text-xs text-neutral-500" dir="ltr">Out of prototype scope: homepage only.</p></div>
    <button type="button" data-close class="inline-flex size-8 shrink-0 items-center justify-center rounded-sm text-black hover:bg-neutral-100" aria-label="إغلاق">{icon("multiplication-sign", 5)}</button>
  </div>
</template>
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
