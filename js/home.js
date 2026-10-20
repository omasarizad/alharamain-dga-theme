/*
 * Homepage behaviour:
 * 1. Place tabs (الكل / المسجد الحرام / المسجد النبوي) filter their card grid.
 * 2. Footer link groups are passed to <dga-footer> as a JS property.
 * 3. Prototype scope guard: anything marked data-out-of-scope (links, buttons,
 *    the search form) shows a Platforms Code toast instead of navigating.
 */
(function () {
  "use strict";

  /* ---- 1. Place filter ---------------------------------------------- */
  function applyFilter(key, value) {
    var grid = document.getElementById("grid-" + key);
    if (!grid) return;
    var shown = 0;
    grid.querySelectorAll(".content-card").forEach(function (card) {
      var match = value === "all" || card.dataset.place === value;
      card.hidden = !match;
      if (match) shown++;
    });
    var empty = grid.querySelector(".empty-state");
    if (!shown && !empty) {
      empty = document.createElement("p");
      empty.className = "empty-state text-md-regular";
      empty.textContent = "لا يوجد محتوى لهذا المكان في النموذج التجريبي.";
      grid.appendChild(empty);
    }
    if (empty) empty.hidden = shown > 0;
  }

  document.addEventListener("click", function (e) {
    var tab = e.target.closest && e.target.closest(".place-tabs dga-tab");
    if (!tab) return;
    var tabs = tab.closest(".place-tabs");
    applyFilter(tabs.dataset.filter, tab.getAttribute("value"));
  });
  // Keyboard / programmatic changes, if the component emits a change event
  ["dgaChange", "dgaTabChange", "change"].forEach(function (name) {
    document.addEventListener(name, function (e) {
      var tabs = e.target.closest && e.target.closest(".place-tabs");
      if (!tabs) return;
      var v = (e.detail && (e.detail.value || e.detail)) || tabs.value;
      if (typeof v === "string") applyFilter(tabs.dataset.filter, v);
    });
  });

  /* ---- Mobile nav drawer --------------------------------------------- */
  document.addEventListener("click", function (e) {
    var btn = e.target.closest && e.target.closest(".menu-action");
    if (!btn) return;
    var drawer = document.getElementById("nav-drawer");
    drawer.open = true;
    btn.setAttribute("aria-expanded", "true");
  });
  document.addEventListener("closeClick", function (e) {
    if (e.target.id !== "nav-drawer") return;
    e.target.open = false;
    var btn = document.querySelector(".menu-action");
    if (btn) { btn.setAttribute("aria-expanded", "false"); btn.focus(); }
  });

  /* ---- 2. Footer data ----------------------------------------------- */
  customElements.whenDefined("dga-footer").then(function () {
    var footer = document.getElementById("site-footer");
    var data = JSON.parse(document.getElementById("footer-data").textContent);
    footer.NavLinks = true;          // group links only render when this is set
    footer.groupLinks = data.groupLinks;
  });

  /* ---- 3. Prototype scope guard ------------------------------------- */
  var toast;
  function showScopeToast() {
    if (toast) toast.remove();
    toast = document.createElement("dga-notification-toast");
    toast.id = "scope-toast";
    toast.setAttribute("type", "info");
    toast.setAttribute("lead-text", "خارج نطاق النموذج التجريبي");
    toast.setAttribute("description", "هذا النموذج يشمل الصفحة الرئيسية فقط.");
    toast.setAttribute("has-helper-text", "");
    toast.setAttribute("helper-text", "Out of prototype scope: homepage only.");
    toast.setAttribute("v-postion", "bottom");
    toast.setAttribute("h-postion", "left");
    toast.setAttribute("duration", "3500");
    toast.setAttribute("close-button", "");
    toast.setAttribute("close-label", "إغلاق");
    document.body.appendChild(toast);
    // Fallback auto-dismiss in case duration is not honoured
    setTimeout(function () { if (toast && toast.isConnected) toast.remove(); }, 4000);
  }

  document.addEventListener("click", function (e) {
    var el = e.target.closest && e.target.closest("[data-out-of-scope], [data-out-of-scope-tabs] dga-tab:not([value='video'])");
    if (!el) return;
    e.preventDefault();
    e.stopPropagation();
    showScopeToast();
  }, true);

  document.addEventListener("submit", function (e) {
    e.preventDefault();
    showScopeToast();
  }, true);

  // Header search submits (Enter) via its own component event
  document.addEventListener("keydown", function (e) {
    if (e.key !== "Enter") return;
    var path = e.composedPath ? e.composedPath() : [];
    if (path.some(function (n) { return n.tagName === "DGA-HEADER-SEARCH-ACTION" || n.tagName === "DGA-SEARCH-BOX"; })) {
      e.preventDefault();
      showScopeToast();
    }
  }, true);
})();
