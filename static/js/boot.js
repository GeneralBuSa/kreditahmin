/*
 * Sayfa çizilmeden önce çalışır (base.html <head> içinde, defer olmadan):
 *   1. Kayıtlı ya da sistemdeki temayı uygular; sayfa yanlış temada yanıp sönmez.
 *   2. Sayfaya gömülü metinleri (src/i18n.py) diğer script'lere hazırlar.
 * Satır içi <script> kullanılmadığı için İçerik Güvenlik Politikası (CSP) yalnızca
 * sitenin kendi dosyalarına izin verebilir.
 */
(() => {
  let theme = null;
  try { theme = localStorage.getItem("kreditahmin-theme"); } catch (e) {}
  if (theme !== "light" && theme !== "dark") {
    theme = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }
  document.documentElement.setAttribute("data-theme", theme);

  const texts = document.getElementById("kredi-i18n");
  window.KREDI_I18N = texts ? JSON.parse(texts.textContent) : {};
})();
