(() => {
  const form = document.getElementById("application");
  if (!form) return;

  const THRESHOLD = 550;
  // Metinler src/i18n.py'den gelir (base.html sayfaya gömer).
  const T = window.KREDI_I18N;
  const interpolate = (template, values) => template.replace(/\{(\w+)\}/g, (_, key) => values[key]);
  const range = document.getElementById("cibil_score_range");
  const scoreInput = document.getElementById("cibil_score");
  const scoreOutput = document.getElementById("score-output");
  const scoreStatus = document.getElementById("score-status");
  const submitButton = document.getElementById("submit-button");
  const status = document.getElementById("form-status");
  const badge = document.getElementById("slip-badge");

  const intFormat = new Intl.NumberFormat(T["num.locale"], { maximumFractionDigits: 0 });
  const decFormat = new Intl.NumberFormat(T["num.locale"], { maximumFractionDigits: 1, minimumFractionDigits: 1 });
  const percent = (value) => interpolate(T["num.percent"], { value });

  const EXAMPLES = {
    approved: {
      cibil_score: 778, loan_amount: 29900000, loan_term: 12, income_annum: 9600000,
      no_of_dependents: 2, education: "Graduate", self_employed: "No",
      residential_assets_value: 2400000, commercial_assets_value: 17600000,
      luxury_assets_value: 22700000, bank_asset_value: 8000000,
    },
    rejected: {
      cibil_score: 417, loan_amount: 12200000, loan_term: 8, income_annum: 4100000,
      no_of_dependents: 0, education: "Not Graduate", self_employed: "Yes",
      residential_assets_value: 2700000, commercial_assets_value: 2200000,
      luxury_assets_value: 8800000, bank_asset_value: 3300000,
    },
  };

  const MONEY_FIELDS = Array.from(form.querySelectorAll("[data-money]")).map((el) => el.name);
  const ASSET_FIELDS = ["residential_assets_value", "commercial_assets_value", "luxury_assets_value", "bank_asset_value"];
  const CHOICE_FIELDS = ["education", "self_employed"];

  /* ---------- Sayı biçimlendirme ---------- */

  const digitsOnly = (text) => String(text).replace(/\D/g, "");

  function readNumber(name) {
    const el = form.elements[name];
    if (!el) return null;
    const digits = digitsOnly(el.value);
    return digits === "" ? null : Number(digits);
  }

  // Yazarken binlik ayraç ekler, imleci aynı rakamın yanında tutar.
  function formatMoneyInput(input) {
    const before = input.value;
    const caret = input.selectionStart ?? before.length;
    const digitsBeforeCaret = digitsOnly(before.slice(0, caret)).length;
    const digits = digitsOnly(before).replace(/^0+(?=\d)/, "");
    const formatted = digits === "" ? "" : intFormat.format(Number(digits));
    input.value = formatted;

    let seen = 0;
    let pos = 0;
    while (pos < formatted.length && seen < digitsBeforeCaret) {
      if (/\d/.test(formatted[pos])) seen += 1;
      pos += 1;
    }
    if (document.activeElement === input) input.setSelectionRange(pos, pos);
  }

  function setMoney(name, value) {
    form.elements[name].value = intFormat.format(value);
  }

  /* ---------- Kredi skoru ---------- */

  function renderScore(score) {
    const above = score >= THRESHOLD;
    scoreOutput.textContent = score;
    scoreOutput.dataset.side = above ? "above" : "below";
    scoreStatus.dataset.side = above ? "above" : "below";
    scoreStatus.textContent = above ? T["js.score_above"] : T["js.score_below"];
    const pct = ((score - 300) / 600) * 100;
    range.style.setProperty("--fill", `${pct}%`);
  }

  function setScore(score) {
    range.value = score;
    scoreInput.value = score;
    renderScore(score);
  }

  range.addEventListener("input", () => {
    scoreInput.value = range.value;
    renderScore(Number(range.value));
    markStale();
  });

  /* ---------- Seçim ve sayaç ---------- */

  form.querySelectorAll(".stepper__button").forEach((button) => {
    button.addEventListener("click", () => {
      const input = button.parentElement.querySelector("input");
      const current = Number(digitsOnly(input.value) || 0);
      input.value = Math.min(10, Math.max(0, current + Number(button.dataset.step)));
      input.dispatchEvent(new Event("input", { bubbles: true }));
    });
  });

  /* ---------- Canlı oranlar ---------- */

  function updateRatios() {
    const income = readNumber("income_annum");
    const amount = readNumber("loan_amount");
    const term = readNumber("loan_term");
    const assets = ASSET_FIELDS.map(readNumber);

    document.getElementById("ratio-payment").textContent =
      income && amount && term ? percent(intFormat.format((amount / term / income) * 100)) : "—";
    document.getElementById("ratio-income").textContent =
      income && amount ? interpolate(T["js.years"], { value: decFormat.format(amount / income) }) : "—";
    document.getElementById("ratio-assets").textContent = assets.some((a) => a !== null)
      ? `${intFormat.format(assets.reduce((sum, a) => sum + (a || 0), 0))} ₹`
      : "—";
  }

  function markStale() {
    const filled = document.getElementById("result-filled");
    if (!filled.hidden) {
      filled.classList.add("is-stale");
      badge.textContent = T["js.badge_stale"];
      badge.dataset.state = "stale";
    }
  }

  form.addEventListener("input", (event) => {
    const target = event.target;
    if (target.matches("[data-money]")) formatMoneyInput(target);
    if (target.name === "loan_term" || target.name === "no_of_dependents") {
      target.value = digitsOnly(target.value).slice(0, 2);
    }
    if (target.name) {
      target.removeAttribute("aria-invalid");
      const error = form.querySelector(`[data-error-for="${target.name}"]`);
      if (error) error.textContent = "";
    }
    updateRatios();
    markStale();
  });

  /* ---------- Örnekler ---------- */

  document.querySelectorAll("[data-example]").forEach((button) => {
    button.addEventListener("click", () => {
      const example = EXAMPLES[button.dataset.example];
      Object.entries(example).forEach(([name, v]) => {
        if (name === "cibil_score") return setScore(v);
        if (CHOICE_FIELDS.includes(name)) {
          form.querySelector(`input[name="${name}"][value="${v}"]`).checked = true;
          return;
        }
        if (MONEY_FIELDS.includes(name)) return setMoney(name, v);
        form.elements[name].value = v;
      });
      clearErrors();
      updateRatios();
      form.requestSubmit();
    });
  });

  /* ---------- Hatalar ---------- */

  function clearErrors() {
    form.querySelectorAll("[data-error-for]").forEach((el) => (el.textContent = ""));
    form.querySelectorAll("[aria-invalid]").forEach((el) => el.removeAttribute("aria-invalid"));
    status.textContent = "";
  }

  function resetResult() {
    document.getElementById("result-empty").hidden = false;
    document.getElementById("result-filled").hidden = true;
    badge.textContent = T["js.badge_waiting"];
    delete badge.dataset.state;
  }

  function showErrors(errors) {
    resetResult();
    let first = null;
    Object.entries(errors).forEach(([name, message]) => {
      const target = form.querySelector(`[data-error-for="${name}"]`);
      if (target) target.textContent = message;
      const input = name === "cibil_score" ? range : form.querySelector(`[name="${name}"]`);
      if (input) {
        input.setAttribute("aria-invalid", "true");
        first = first || input;
      }
    });
    status.textContent = T["js.form_invalid"];
    if (first) first.focus();
  }

  /* ---------- Sonuç ---------- */

  function renderResult(data) {
    document.getElementById("result-empty").hidden = true;
    const filled = document.getElementById("result-filled");
    filled.hidden = false;
    filled.classList.remove("is-stale");

    const approved = data.approved;
    badge.textContent = approved ? T["js.badge_approve"] : T["js.badge_reject"];
    badge.dataset.state = approved ? "approve" : "reject";

    const stamp = document.getElementById("stamp");
    stamp.className = `stamp ${approved ? "stamp--approve" : "stamp--reject"}`;
    document.getElementById("stamp-text").textContent = approved ? T["js.stamp_approve"] : T["js.stamp_reject"];
    void stamp.offsetWidth;
    stamp.classList.add("is-landing");

    document.getElementById("verdict-headline").textContent = approved ? T["js.verdict_approve"] : T["js.verdict_reject"];

    const pct = data.probability * 100;
    document.getElementById("probability-text").textContent = percent(decFormat.format(pct));
    const fill = document.getElementById("probability-fill");
    fill.className = `meter__fill ${approved ? "meter__fill--approve" : "meter__fill--reject"}`;
    fill.style.width = `${Math.max(pct, 1)}%`;

    const factors = document.getElementById("factors");
    factors.innerHTML = "";
    data.factors.forEach((factor) => {
      const li = document.createElement("li");
      li.dataset.tone = factor.tone;
      const title = document.createElement("strong");
      title.textContent = factor.title;
      const text = document.createElement("p");
      text.textContent = factor.text;
      li.append(title, text);
      factors.append(li);
    });

    const warnings = document.getElementById("warnings");
    warnings.innerHTML = "";
    data.warnings.forEach((message) => {
      const li = document.createElement("li");
      li.textContent = message;
      warnings.append(li);
    });

    if (window.matchMedia("(max-width: 1024px)").matches) {
      const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
      document.querySelector(".slip").scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "start" });
    }
  }

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    clearErrors();

    const payload = {};
    new FormData(form).forEach((v, k) => {
      if (CHOICE_FIELDS.includes(k)) payload[k] = v;
      else payload[k] = digitsOnly(v) === "" ? "" : Number(digitsOnly(v));
    });

    submitButton.disabled = true;
    submitButton.textContent = T["js.submitting"];
    try {
      let ok;
      let data;
      if (window.KrediPredictor) {
        // GitHub Pages sürümü: model tarayıcıda çalışır.
        ({ ok, data } = await window.KrediPredictor.predict(payload, T.lang));
      } else {
        // Flask sürümü: tahmin sunucuda yapılır.
        const response = await fetch(form.dataset.endpoint || "/api/predict", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
        ok = response.ok;
        data = await response.json();
      }
      if (!ok) {
        if (data.errors) showErrors(data.errors);
        else status.textContent = data.error || T["js.generic_error"];
        return;
      }
      renderResult(data);
    } catch (error) {
      status.textContent = T["js.network_error"];
    } finally {
      submitButton.disabled = false;
      submitButton.textContent = T["js.submit"];
    }
  });

  setScore(Number(range.value));
  updateRatios();
})();
