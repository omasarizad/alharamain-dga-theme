/*
 * Prototype bottom bar, shared by every page (index, components, changes).
 * Self-contained: injects its own styles, so it works on pages that don't
 * load Platforms Code. Colors use Platforms Code tokens with their official
 * values as fallbacks.
 */
(function () {
  "use strict";
  var LINKS = [
    { href: "index.html", match: ["", "index.html"], ar: "الرئيسية" },
    { href: "components.html", match: ["components.html"], ar: "المكوّنات" },
    { href: "changes.html", match: ["changes.html"], ar: "التغييرات" },
    { href: "https://github.com/omasarizad/alharamain-dga-theme", ar: "المستودع", external: true },
  ];
  var page = location.pathname.split("/").pop();

  var css =
    ".proto-bar{position:fixed;inset-inline:0;bottom:0;z-index:9000;display:flex;align-items:center;justify-content:center;gap:4px;" +
    "padding:4px 16px calc(4px + env(safe-area-inset-bottom));background:var(--colors-neutral-900,#111927);color:var(--colors-base-white,#fff);" +
    "font:500 13px/20px 'IBM Plex Sans Arabic','IBM Plex Sans',system-ui,sans-serif;box-shadow:0 -4px 16px rgba(16,24,40,.18)}" +
    ".proto-bar__tag{margin-inline-end:8px;padding:0 8px;border-radius:4px;background:var(--colors-primary-sa-flag-600-primary,#1b8354);font-size:12px;white-space:nowrap}" +
    ".proto-bar a{display:inline-flex;align-items:center;padding:4px 12px;border-radius:4px;white-space:nowrap;color:var(--colors-neutral-300,#d2d6db);text-decoration:none}" +
    ".proto-bar a:hover{background:rgba(255,255,255,.08);color:#fff}" +
    ".proto-bar a[aria-current=page]{background:rgba(255,255,255,.12);color:#fff;box-shadow:inset 0 -2px 0 var(--colors-primary-sa-flag-400,#54c08a)}" +
    ".proto-bar a:focus-visible{outline:2px solid #fff;outline-offset:2px}" +
    "body{padding-bottom:40px}" +
    "@media (max-width:599px){.proto-bar__tag{display:none}.proto-bar a{padding:4px 8px}}";

  function mount() {
    var style = document.createElement("style");
    style.textContent = css;
    document.head.appendChild(style);

    var nav = document.createElement("nav");
    nav.className = "proto-bar";
    nav.dir = "rtl";
    nav.setAttribute("aria-label", "صفحات النموذج التجريبي");
    nav.innerHTML = '<span class="proto-bar__tag">نموذج تجريبي</span>';
    LINKS.forEach(function (l) {
      var a = document.createElement("a");
      a.href = l.href;
      a.textContent = l.ar;
      if (l.external) { a.target = "_blank"; a.rel = "noopener"; }
      if (l.match && l.match.indexOf(page) !== -1) a.setAttribute("aria-current", "page");
      nav.appendChild(a);
    });
    document.body.appendChild(nav);
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", mount);
  else mount();
})();
