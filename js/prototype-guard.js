/*
 * Prototype scope guard.
 * Only the homepage is part of this prototype. Every link to another page is
 * disabled (href removed at build time, kept in data-out-of-scope) and shows
 * a toast instead. Forms (search) are blocked the same way.
 */
(function () {
  var MESSAGE = "هذه الصفحة خارج نطاق النموذج التجريبي";
  var SUB = "Out of prototype scope: only the homepage is included.";
  var toast, timer;

  function show() {
    if (!toast) {
      toast = document.createElement("div");
      toast.className = "proto-toast";
      toast.setAttribute("role", "status");
      toast.setAttribute("aria-live", "polite");
      toast.innerHTML =
        '<svg aria-hidden="true" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 8v4M12 16h.01"/></svg>' +
        "<div><strong></strong><span></span></div>";
      toast.querySelector("strong").textContent = MESSAGE;
      toast.querySelector("span").textContent = SUB;
      toast.querySelector("span").setAttribute("dir", "ltr");
      document.body.appendChild(toast);
    }
    toast.classList.add("is-visible");
    clearTimeout(timer);
    timer = setTimeout(function () { toast.classList.remove("is-visible"); }, 3200);
  }

  document.addEventListener("click", function (e) {
    var a = e.target.closest && e.target.closest("[data-out-of-scope]");
    if (!a) return;
    e.preventDefault();
    show();
  }, true);

  document.addEventListener("submit", function (e) {
    e.preventDefault();
    show();
  }, true);
})();
