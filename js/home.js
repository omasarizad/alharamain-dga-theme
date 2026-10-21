/*
 * Homepage behaviour (vanilla JS, no framework):
 * 1. Place tabs (الكل / المسجد الحرام / المسجد النبوي) filter their card grid;
 *    content-type tabs (مرئي / نصي) switch between panels.
 * 2. Mobile nav drawer (<dialog id="nav-drawer">).
 * 3. Prototype scope guard: anything marked data-out-of-scope (links, buttons,
 *    the search form) shows the toast instead of navigating.
 */
(function () {
  "use strict";

  /* ---- 1. Place filter tabs ------------------------------------------ */
  function selectTab(tab) {
    var list = tab.closest("[role=tablist]");
    list.querySelectorAll("[role=tab]").forEach(function (t) {
      t.setAttribute("aria-selected", String(t === tab));
    });
    // Content-type tabs (مرئي / نصي) switch whole panels instead of filtering
    var panel = document.getElementById("panel-" + list.dataset.filter + "-" + tab.dataset.value);
    if (panel) {
      document.querySelectorAll('[data-panel="' + list.dataset.filter + '"]').forEach(function (p) {
        p.hidden = p !== panel;
      });
      return;
    }
    var grid = document.getElementById("grid-" + list.dataset.filter);
    if (!grid) return;
    var value = tab.dataset.value, shown = 0;
    grid.querySelectorAll("[data-place]").forEach(function (card) {
      var match = value === "all" || card.dataset.place === value;
      card.hidden = !match;
      if (match) shown++;
    });
    var empty = grid.querySelector(".empty-state");
    if (!shown && !empty) {
      empty = document.createElement("p");
      empty.className = "empty-state col-span-full rounded-md border border-dashed border-neutral-300 p-10 text-center text-md text-neutral-500";
      empty.textContent = "لا يوجد محتوى لهذا المكان في النموذج التجريبي.";
      grid.appendChild(empty);
    }
    if (empty) empty.hidden = shown > 0;
  }

  document.addEventListener("click", function (e) {
    var tab = e.target.closest("[role=tab]");
    if (tab && !tab.hasAttribute("data-out-of-scope")) selectTab(tab);
  });

  // Arrow-key navigation between tabs (WAI-ARIA tabs pattern, RTL-aware)
  document.addEventListener("keydown", function (e) {
    var tab = e.target.closest && e.target.closest("[role=tab]");
    if (!tab || (e.key !== "ArrowLeft" && e.key !== "ArrowRight")) return;
    var tabs = Array.prototype.slice.call(tab.parentElement.querySelectorAll("[role=tab]"));
    var step = (e.key === "ArrowLeft") === (document.dir === "rtl") ? 1 : -1;
    var next = tabs[(tabs.indexOf(tab) + step + tabs.length) % tabs.length];
    next.focus();
    e.preventDefault();
  });

  /* ---- 2. Mobile nav drawer ------------------------------------------ */
  var drawer = document.getElementById("nav-drawer");
  var menuButton = document.getElementById("menu-button");
  if (drawer && menuButton) {
    menuButton.addEventListener("click", function () {
      drawer.showModal();
      menuButton.setAttribute("aria-expanded", "true");
    });
    drawer.addEventListener("close", function () {
      menuButton.setAttribute("aria-expanded", "false");
      menuButton.focus();
    });
    drawer.addEventListener("click", function (e) {
      if (e.target === drawer || e.target.closest("[data-close]")) drawer.close(); // backdrop or close button
    });
  }

  /* ---- 3. Prototype scope guard -------------------------------------- */
  var region = document.getElementById("toast-region");
  var template = document.getElementById("toast-template");
  var timer;
  function showScopeToast() {
    region.innerHTML = "";
    var toast = template.content.firstElementChild.cloneNode(true);
    toast.querySelector("[data-close]").addEventListener("click", function () { toast.remove(); });
    region.appendChild(toast);
    clearTimeout(timer);
    timer = setTimeout(function () { toast.remove(); }, 3500);
  }

  document.addEventListener("click", function (e) {
    var el = e.target.closest("[data-out-of-scope]");
    if (!el) return;
    e.preventDefault();
    if (drawer && drawer.open) drawer.close();
    showScopeToast();
  }, true);

  document.addEventListener("submit", function (e) {
    e.preventDefault();
    showScopeToast();
  }, true);
})();
