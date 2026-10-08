/*
 * İçindekiler menüleri (scrollspy): ana sayfadaki form adımları ve
 * "Model nasıl çalışıyor?" sayfasındaki bölüm listesi.
 * Kaydırdıkça ekrandaki bölümün bağlantısı vurgulanır ve gösterge ona kayar:
 * dikey listede soldaki çizgi, yatay şeritte bağlantının arkasındaki hap.
 */
(() => {
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function setup(nav) {
    const links = Array.from(nav.querySelectorAll(".toc__link"));
    const sections = links.map((link) => document.getElementById(link.hash.slice(1)));
    const marker = nav.querySelector(".toc__marker");
    const list = nav.querySelector(".toc__list");
    let active = -1;

    // Bölüm başlığı ekranın üst üçte birini geçince o bölüm "okunuyor" sayılır.
    function currentIndex() {
      const line = window.innerHeight * 0.33;
      const atBottom = window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 2;
      // Sayfanın sonunda son bölüm seçilir; ama bölümler sayfanın sonuna kadar uzanıyorsa
      // (ana sayfada formun altında sonuç kartı ve alt bilgi var) bu kural uygulanmaz.
      const last = sections[sections.length - 1];
      if (atBottom && last.getBoundingClientRect().bottom <= window.innerHeight) return sections.length - 1;
      let index = 0;
      sections.forEach((section, i) => {
        if (section.getBoundingClientRect().top <= line) index = i;
      });
      return index;
    }

    function moveMarker(link) {
      const horizontal = getComputedStyle(list).display === "flex";
      marker.style.transform = `translate(${horizontal ? link.offsetLeft : 0}px, ${link.offsetTop}px)`;
      marker.style.height = `${link.offsetHeight}px`;
      marker.style.width = horizontal ? `${link.offsetWidth}px` : "";
      if (!nav.classList.contains("is-ready")) {
        // İlk konum animasyonsuz verilir; kaydırma animasyonu sonraki değişimlerde başlar.
        void marker.offsetWidth;
        nav.classList.add("is-ready");
      }
    }

    function keepVisible(link) {
      // Yatay şerit taşıyorsa sayfayı değil yalnızca şeridi kaydırır.
      if (list.scrollWidth <= list.clientWidth) return;
      const left = link.offsetLeft - (list.clientWidth - link.offsetWidth) / 2;
      list.scrollTo({ left, behavior: reduceMotion ? "auto" : "smooth" });
    }

    function update() {
      const index = currentIndex();
      if (index === active) return;
      active = index;
      links.forEach((link, i) => {
        if (i === index) link.setAttribute("aria-current", "location");
        else link.removeAttribute("aria-current");
      });
      moveMarker(links[index]);
      keepVisible(links[index]);
    }

    let scheduled = false;
    function schedule() {
      if (scheduled) return;
      scheduled = true;
      window.requestAnimationFrame(() => {
        scheduled = false;
        update();
      });
    }

    window.addEventListener("scroll", schedule, { passive: true });
    window.addEventListener("resize", () => {
      // Ekran genişliği değişince menü dikeyden yataya geçebilir; gösterge animasyonsuz yerleşir.
      nav.classList.remove("is-ready");
      active = -1;
      schedule();
    });
    // Yazı tipi yüklenince bağlantı genişlikleri değişir.
    if (document.fonts) document.fonts.ready.then(() => { active = -1; schedule(); });
    update();
  }

  document.querySelectorAll("[data-scrollspy]").forEach(setup);
})();
