/* Üst bardaki anahtarlar: tema (aydınlık | karanlık) ve dil (TR | EN). */
(() => {
  const root = document.documentElement;
  const reduceMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------- Tema ---------- */

  const themeButtons = document.querySelectorAll("[data-theme-value]");
  const prefersDark = () => window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
  const current = () => root.getAttribute("data-theme") || (prefersDark() ? "dark" : "light");

  function sync() {
    const theme = current();
    themeButtons.forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.themeValue === theme)));
    document.querySelectorAll('meta[name="theme-color"]').forEach((m) =>
      m.setAttribute("content", theme === "dark" ? "#000000" : "#f5f6f8"));
  }

  themeButtons.forEach((button) => {
    button.addEventListener("click", () => {
      const next = button.dataset.themeValue;
      if (next === current()) return;
      root.classList.add("theme-switching");
      root.setAttribute("data-theme", next);
      try { localStorage.setItem("kreditahmin-theme", next); } catch (e) {}
      sync();
      window.setTimeout(() => root.classList.remove("theme-switching"), 320);
    });
  });

  sync();

  /* ---------- Dil ---------- */

  const langSwitch = document.querySelector(".switch[data-active]");
  if (!langSwitch) return;
  const options = Array.from(langSwitch.querySelectorAll(".switch__option"));
  const initial = langSwitch.dataset.active;

  function select(index) {
    langSwitch.dataset.active = String(index);
    options.forEach((o, i) => (i === index ? o.setAttribute("aria-current", "true") : o.removeAttribute("aria-current")));
  }

  // Seçenek bir bağlantı; önce gösterge kayar, sonra diğer dildeki sayfaya geçilir.
  options.forEach((link, index) => {
    link.addEventListener("click", (event) => {
      if (link.getAttribute("aria-current") === "true") {
        event.preventDefault();
        return;
      }
      if (reduceMotion || event.ctrlKey || event.metaKey || event.shiftKey || event.button !== 0) return;
      event.preventDefault();
      select(index);
      window.setTimeout(() => { window.location.href = link.href; }, 200);
    });
  });

  // Geri tuşuyla önbellekten dönülürse anahtar bu sayfanın diline geri alınır.
  window.addEventListener("pageshow", (event) => {
    if (event.persisted) select(Number(initial));
  });
})();
