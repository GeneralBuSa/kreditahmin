/*
 * Tarayıcıda çalışan tahmin motoru (GitHub Pages sürümü için).
 *
 * Flask uygulamasındaki /api/predict ile aynı işi yapar: formu doğrular,
 * feature engineering uygular, Gradient Boosting modelini çalıştırır ve
 * kararın gerekçelerini üretir. Model ağaçları ve metinler (src/i18n.py)
 * scripts/build_static.py tarafından model.json'a aktarılır.
 */
(() => {
  const CIBIL_THRESHOLD = 550;
  const MAX_VALUE = 1e15; // app.py'deki MAX_VALUE ile aynı.
  const RAW_COLUMNS = [
    "no_of_dependents", "education", "self_employed", "income_annum", "loan_amount",
    "loan_term", "cibil_score", "residential_assets_value", "commercial_assets_value",
    "luxury_assets_value", "bank_asset_value",
  ];
  const CHOICE_FIELDS = ["education", "self_employed"];

  let modelPromise = null;
  function loadModel() {
    if (!modelPromise && window.KREDI_MODEL) modelPromise = Promise.resolve(window.KREDI_MODEL);
    if (!modelPromise) {
      const url = document.querySelector('meta[name="kredi-model"]').content;
      modelPromise = fetch(url).then((r) => {
        if (!r.ok) throw new Error("model.json yüklenemedi");
        return r.json();
      });
    }
    return modelPromise;
  }

  // src/i18n.py'deki text, fmt_int ve fmt_dec ile aynı.
  const text = (m, key, values = {}) => m[key].replace(/\{(\w+)\}/g, (_, name) => values[name]);
  const fmtInt = (n, m) => Math.round(n).toString().replace(/\B(?=(\d{3})+(?!\d))/g, m["num.thousands"]);
  const fmtDec = (n, m) => n.toFixed(1).replace(".", m["num.decimal"]);

  function validate(payload, model, m) {
    const errors = {};
    const clean = {};
    for (const field of RAW_COLUMNS) {
      const value = payload[field];
      if (value === undefined || value === null || String(value).trim() === "") {
        errors[field] = text(m, "api.required");
        continue;
      }
      if (CHOICE_FIELDS.includes(field)) {
        const map = field === "education" ? model.education_map : model.self_employed_map;
        if (typeof value !== "string" || !(value in map)) errors[field] = text(m, "api.choice");
        else clean[field] = value;
        continue;
      }
      const number = Number(value);
      if (!Number.isFinite(number)) { errors[field] = text(m, "api.number"); continue; }
      if (number < 0) { errors[field] = text(m, "api.negative"); continue; }
      if (number > MAX_VALUE) { errors[field] = text(m, "api.too_large"); continue; }
      clean[field] = number;
    }
    if ("cibil_score" in clean && !(clean.cibil_score >= 300 && clean.cibil_score <= 900)) {
      errors.cibil_score = text(m, "api.cibil_range");
    }
    if ("income_annum" in clean && clean.income_annum < 1) errors.income_annum = text(m, "api.income_min");
    if ("loan_amount" in clean && clean.loan_amount <= 0) errors.loan_amount = text(m, "api.loan_min");
    if ("loan_term" in clean && clean.loan_term < 1) errors.loan_term = text(m, "api.term_min");
    if ("no_of_dependents" in clean && !Number.isInteger(clean.no_of_dependents)) errors.no_of_dependents = text(m, "api.integer");
    return { clean, errors };
  }

  // src/features.py içindeki add_features ile aynı.
  function addFeatures(c, model) {
    const row = {
      ...c,
      education: model.education_map[c.education],
      self_employed: model.self_employed_map[c.self_employed],
    };
    row.total_assets = c.residential_assets_value + c.commercial_assets_value + c.luxury_assets_value + c.bank_asset_value;
    row.loan_to_income = c.loan_amount / c.income_annum;
    row.loan_to_assets = c.loan_amount / (row.total_assets === 0 ? 1 : row.total_assets);
    row.yearly_payment_to_income = (c.loan_amount / c.loan_term) / c.income_annum;
    return row;
  }

  // scikit-learn ağaçları girdiyi float32'ye çevirerek karşılaştırır; aynısını yapıyoruz.
  function predictProba(row, model) {
    const x = model.features.map((f) => Math.fround(row[f]));
    let raw = model.init;
    for (const tree of model.trees) {
      let node = 0;
      while (tree.left[node] !== -1) {
        node = x[tree.feature[node]] <= tree.threshold[node] ? tree.left[node] : tree.right[node];
      }
      raw += model.learning_rate * tree.value[node];
    }
    return 1 / (1 + Math.exp(-raw));
  }

  function rangeWarnings(clean, model, m) {
    const warnings = [];
    for (const field of RAW_COLUMNS) {
      const range = model.feature_ranges[field];
      if (CHOICE_FIELDS.includes(field) || !range) continue;
      const [low, high] = range;
      if (!(clean[field] >= low && clean[field] <= high)) {
        warnings.push(text(m, "api.range_warning", {
          label: text(m, `field.${field}`), low: fmtInt(low, m), high: fmtInt(high, m),
        }));
      }
    }
    return warnings;
  }

  function explain(clean, row, probability, m) {
    const factors = [];
    const score = fmtInt(clean.cibil_score, m);
    if (clean.cibil_score >= CIBIL_THRESHOLD) {
      factors.push({
        tone: "positive",
        title: text(m, "api.score_above_title", { score }),
        text: text(m, "api.score_above_text"),
      });
    } else {
      factors.push({
        tone: "negative",
        title: text(m, "api.score_below_title", { score }),
        text: text(m, "api.score_below_text"),
      });
    }
    const pct = fmtInt(row.yearly_payment_to_income * 100, m);
    factors.push({
      tone: "neutral",
      title: text(m, "api.payment_title", { pct }),
      text: text(m, "api.payment_text", { pct, term: fmtInt(clean.loan_term, m) }),
    });
    factors.push({
      tone: "neutral",
      title: text(m, "api.loan_income_title", { ratio: fmtDec(row.loan_to_income, m) }),
      text: row.total_assets > 0
        ? text(m, "api.assets_text", { ratio: fmtDec(1 / row.loan_to_assets, m) })
        : text(m, "api.no_assets_text"),
    });
    if (probability > 0.35 && probability < 0.65) {
      factors.push({
        tone: "neutral",
        title: text(m, "api.uncertain_title"),
        text: text(m, "api.uncertain_text"),
      });
    }
    return factors;
  }

  async function predict(payload, lang = "tr") {
    const model = await loadModel();
    const m = model.messages[lang] || model.messages.tr;
    const { clean, errors } = validate(payload, model, m);
    if (Object.keys(errors).length) return { ok: false, data: { errors } };
    const row = addFeatures(clean, model);
    const probability = predictProba(row, model);
    return {
      ok: true,
      data: {
        approved: probability >= 0.5,
        probability,
        ratios: {
          yearly_payment_to_income: row.yearly_payment_to_income,
          loan_to_income: row.loan_to_income,
          total_assets: row.total_assets,
        },
        factors: explain(clean, row, probability, m),
        warnings: rangeWarnings(clean, model, m),
      },
    };
  }

  window.KrediPredictor = { predict, _addFeatures: addFeatures, _predictProba: predictProba, _loadModel: loadModel };
})();
