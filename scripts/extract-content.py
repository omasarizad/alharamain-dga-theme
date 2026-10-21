#!/usr/bin/env python3
"""Extract homepage content from the original snapshot into data/content.json.

Run from the repo root: python3 scripts/extract-content.py
Input: snapshot/original.html (untouched download of the live homepage).
"""
import json
import re
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

from bs4 import BeautifulSoup

ORIGIN = "https://alharamain-app-beta.it4islam.com"
SECTIONS = {
    "ذاكرة الحرمين": "memory",
    "الدروس والمحاضرات": "lessons",
    "الخطب المنبرية": "speeches",
    "التلاوات": "tilawat",
    "المختارات": "selected",
}
PLACES = ("المسجد الحرام", "المسجد النبوي")
MEDIA = ("صوت", "فيديو", "نص")


def text(el):
    return re.sub(r"\s+", " ", el.get_text(" ", strip=True)).strip() if el else ""


def image_url(img):
    """Unwrap Next.js /_next/image?url=... to the real source."""
    src = img.get("src", "") if img else ""
    if src.startswith("/_next/image"):
        src = unquote(parse_qs(urlparse(src).query).get("url", [""])[0])
    if src.startswith("/"):
        src = ORIGIN + src
    return src


def card(article):
    title_a = article.find("h2").find("a") if article.find("h2") else None
    scholar = article.find("a", attrs={"data-sut": "post-scholar"})
    body = text(article)
    tags = [
        text(a) for a in article.find_all("a")
        if a is not title_a and a is not scholar and text(a) and len(text(a)) < 40
    ]
    meta = re.search(r"(\d+)\s*(درس|درسًا|دروس|محاضرة|محاضرات)", body)
    return {
        "title": text(title_a) or text(article.find("h2")),
        "scholar": text(scholar),
        "date": text(article.find("time")),
        "place": next((p for p in PLACES if p in body), ""),
        "media": [m for m in MEDIA if re.search(rf"(^|\s){m}(\s|$)", body)],
        "tags": list(dict.fromkeys(t for t in tags if t not in PLACES)),
        "count": meta.group(0) if meta else "",
        "image": image_url(article.find("img")),
    }


def main():
    soup = BeautifulSoup(Path("snapshot/original.html").read_text(encoding="utf-8"), "html.parser")
    main_el = soup.find("main")

    # Section headings, in page order
    heads = [h for h in main_el.find_all(["h1", "h2"]) if text(h) in SECTIONS]
    data = {"sections": {}}
    for h in heads:
        sub = h.find_next("p")
        data["sections"][SECTIONS[text(h)]] = {"title": text(h), "subtitle": text(sub), "items": []}

    # Assign each article to the closest preceding section heading
    order = {id(el): i for i, el in enumerate(main_el.find_all(True))}
    head_pos = [(order[id(h)], SECTIONS[text(h)]) for h in heads]
    seen = set()
    for art in main_el.find_all("article"):
        pos = order[id(art)]
        # Tilawat cards sit before their heading in DOM order (two-column layout)
        key = max((p, k) for p, k in head_pos if p < pos)[1] if any(p < pos for p, _ in head_pos) else "memory"
        c = card(art)
        if "border-s-4" in " ".join(art.get("class", [])):
            key = "tilawat"
        sig = (key, c["title"], c["scholar"], c["image"], c["place"], c["date"], tuple(c["tags"]))
        if sig in seen:  # carousel clones
            continue
        seen.add(sig)
        data["sections"][key]["items"].append(c)

    # Tilawat stats (e.g. "+3031 إجمالي التلاوات")
    til = next(h for h in heads if SECTIONS[text(h)] == "tilawat")
    box = til.find_parent("section") or til.parent.parent
    stats = []
    for m in re.finditer(r"([\d٠-٩,+]+\+?)\s+(إجمالي التلاوات|القارئ|القراء|أدعية القنوت|مصحف مسجل)", text(box)):
        # "قارئ" reads better next to a count than "القارئ"
        stats.append({"value": m.group(1), "label": {"القارئ": "قارئ"}.get(m.group(2), m.group(2))})
    data["sections"]["tilawat"]["stats"] = stats

    # المختارات "نصي" tab: not in the rendered HTML, only in the page's data
    # payload as "selectedPostsText" (title, excerpt, topic, related lecture)
    raw = Path("snapshot/original.html").read_text(encoding="utf-8")
    start = raw.index('"selectedPostsText":') + len('"selectedPostsText":')
    posts, _ = json.JSONDecoder().raw_decode(raw[start:])
    data["sections"]["selected"]["text_items"] = [{
        "title": post["title"],
        # The site writes ﷺ as private-use U+F065 drawn by its own icon font
        "excerpt": BeautifulSoup(post["excerpt"] or "", "html.parser").get_text(" ", strip=True).replace("\uf065", "ﷺ"),
        "topic": (post.get("topics") or [{}])[0].get("title", ""),
        "related": (post.get("selectionPosts") or [{}])[0].get("title", ""),
    } for post in posts]

    # Navigation
    nav = []
    for a in soup.select("header a, nav a"):
        t = text(a)
        if t and len(t) < 30 and t not in nav and not t.startswith("http"):
            nav.append(t)
    data["nav"] = nav[:12]

    # Footer
    foot = soup.find("footer")
    data["footer"] = {
        "about": next((text(p) for p in foot.find_all("p") if len(text(p)) > 40), ""),
        "copyright": min((text(p) for p in soup.find_all("p") if "جميع الحقوق" in text(p)), key=len, default=""),
        "partners_title": "شركاء النجاح" if "شركاء النجاح" in text(soup) else "",
        "partners": [img.get("alt") for img in soup.find_all("img") if img.get("alt") and "logo" in img.get("alt").lower()][:8],
    }

    Path("data").mkdir(exist_ok=True)
    Path("data/content.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    for k, v in data["sections"].items():
        print(f"{k}: {len(v['items'])} items", "| stats:", v.get("stats", ""))
    print("nav:", data["nav"])
    print("footer:", data["footer"])


if __name__ == "__main__":
    main()
