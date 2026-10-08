import hashlib
import json
import math
import os
import pickle
from functools import lru_cache
from pathlib import Path

from flask import Flask, jsonify, render_template, request, url_for
from markupsafe import Markup
from werkzeug.exceptions import HTTPException
from werkzeug.middleware.proxy_fix import ProxyFix

from src.features import RAW_COLUMNS, prepare_input
from src.i18n import (
    DEFAULT_LANG, LANGUAGE_NAMES, LANGUAGES, TEXTS, export, fmt_dec, fmt_int, fmt_pct, text,
)

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "model" / "loan_model.pkl"
INFO_PATH = BASE_DIR / "model" / "model_info.json"

CIBIL_THRESHOLD = 550
# Sayısal alanlar için üst sınır. Eğitim verisindeki en büyük tutar ~4·10⁷;
# bu sınır, modelin float32'ye çevirirken taşma hatası vermesini engeller.
MAX_VALUE = 1e15
CHOICE_FIELDS = ("education", "self_employed")
REPO_URL = "https://github.com/GeneralBuSa/kreditahmin"

with open(MODEL_PATH, "rb") as f:
    BUNDLE = pickle.load(f)

with open(INFO_PATH, encoding="utf-8") as f:
    MODEL_INFO = json.load(f)

class KrediApp(Flask):
    def get_send_file_max_age(self, filename):
        # Sürüm parametresi (?v=...) olan dosyaların adresi içerik değişince değişir;
        # bu yüzden tarayıcı onları bir yıl boyunca tekrar sormadan kullanabilir.
        if request.args.get("v"):
            return 31536000
        # CSS'in içinden çağrılan font ve görseller: geliştirirken hiç, yayında 1 gün önbellek.
        return None if self.debug else 86400


app = KrediApp(__name__)
# Normal bir başvuru 1 KB'tan küçük; daha büyük istekler okunmadan 413 ile reddedilir.
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024
# Paylaşım önizlemesindeki (Open Graph) tam adresler için. Boşsa isteğin adresi kullanılır.
app.config["SITE_URL"] = os.environ.get("SITE_URL", "").rstrip("/")
# Render gibi platformlar HTTPS'i önündeki sunucuda karşılar; doğru https:// adresi üretmek için.
# Yalnızca protokol başlığına güvenilir; Host başlığı değiştirilemez.
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1)

# İçerik Güvenlik Politikası: script, stil, font ve görseller yalnızca sitenin kendisinden.
# Şablonlardaki style="..." öznitelikleri (grafik konumları) için 'unsafe-inline' gerekir;
# script'ler için gerekmez, sayfalarda satır içi script yoktur.
CSP = "; ".join([
    "default-src 'self'",
    "script-src 'self'",
    "style-src 'self' 'unsafe-inline'",
    "img-src 'self' data:",
    "font-src 'self'",
    "connect-src 'self'",
    "object-src 'none'",
    "base-uri 'none'",
    "form-action 'self'",
])
SECURITY_HEADERS = {
    # frame-ancestors <meta> ile verilemez; yalnızca başlıkta çalışır.
    "Content-Security-Policy": CSP + "; frame-ancestors 'none'",
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=(), payment=()",
    "Cross-Origin-Opener-Policy": "same-origin",
}


@app.after_request
def add_security_headers(response):
    for name, value in SECURITY_HEADERS.items():
        response.headers.setdefault(name, value)
    if request.is_secure:
        response.headers.setdefault("Strict-Transport-Security", "max-age=31536000")
    return response
VERSIONED_SUFFIXES = (".css", ".js")


@lru_cache(maxsize=64)
def file_version(filename: str, mtime: float) -> str:
    # Satır sonları normalleştirilir; böylece Windows ve Linux'ta aynı sürüm üretilir.
    data = (Path(app.static_folder) / filename).read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()[:10]


@app.url_defaults
def add_static_version(endpoint, values):
    filename = values.get("filename", "")
    if endpoint == "static" and filename.endswith(VERSIONED_SUFFIXES) and "v" not in values:
        path = Path(app.static_folder) / filename
        values["v"] = file_version(filename, path.stat().st_mtime)


def current_lang() -> str:
    """Sayfalarda adresten (/en/...), API'de ?lang= parametresinden okunur."""
    if request.path.startswith("/api/"):
        lang = request.args.get("lang")
        return lang if lang in LANGUAGES else DEFAULT_LANG
    if request.path == "/en" or request.path.startswith("/en/"):
        return "en"
    return DEFAULT_LANG


@app.context_processor
def inject_globals():
    lang = current_lang()
    endpoint = request.endpoint if request.endpoint in ("index", "about") else "index"
    return {
        # GitHub Pages için statik sürüm üretilirken True olur (scripts/build_static.py).
        "static_site": app.config.get("STATIC_SITE", False),
        "lang": lang,
        "t": lambda key, **values: Markup(TEXTS[lang][key]).format(**values),
        "fmt_int": lambda number: fmt_int(number, lang),
        "fmt_dec": lambda number, digits=1: fmt_dec(number, lang, digits),
        "pct": lambda fraction, digits=1: fmt_pct(fraction, lang, digits),
        "js_texts": {"lang": lang, **export(lang, "js.", "num.")},
        "language_options": [
            {"code": code, "name": LANGUAGE_NAMES[code], "url": url_for(endpoint, lang=code)}
            for code in LANGUAGES
        ],
        "alternate_urls": {code: url_for(endpoint, lang=code) for code in LANGUAGES},
        "site_url": app.config["SITE_URL"] or request.url_root.rstrip("/"),
        # GitHub Pages başlık gönderemediği için politika sayfaya <meta> olarak da yazılır.
        "csp": CSP,
        "repo_url": REPO_URL,
    }


def validate(payload: dict, lang: str = DEFAULT_LANG):
    """Gelen formu kontrol eder. (temiz veri, hatalar) döndürür."""
    errors = {}
    clean = {}

    for field in RAW_COLUMNS:
        value = payload.get(field)
        if value is None or str(value).strip() == "":
            errors[field] = text(lang, "api.required")
            continue

        if field in CHOICE_FIELDS:
            choices = BUNDLE["education_map"] if field == "education" else BUNDLE["self_employed_map"]
            if not isinstance(value, str) or value not in choices:
                errors[field] = text(lang, "api.choice")
            else:
                clean[field] = value
            continue

        try:
            number = float(value)
        except (TypeError, ValueError):
            number = math.nan

        # "nan", "inf" ve 1e400 gibi değerler float()'tan geçer ama model bunları işleyemez.
        if not math.isfinite(number):
            errors[field] = text(lang, "api.number")
            continue

        if number < 0:
            errors[field] = text(lang, "api.negative")
            continue

        if number > MAX_VALUE:
            errors[field] = text(lang, "api.too_large")
            continue

        clean[field] = number

    if "cibil_score" in clean and not 300 <= clean["cibil_score"] <= 900:
        errors["cibil_score"] = text(lang, "api.cibil_range")
    if "income_annum" in clean and clean["income_annum"] < 1:
        errors["income_annum"] = text(lang, "api.income_min")
    if "loan_amount" in clean and clean["loan_amount"] <= 0:
        errors["loan_amount"] = text(lang, "api.loan_min")
    if "loan_term" in clean and clean["loan_term"] < 1:
        errors["loan_term"] = text(lang, "api.term_min")
    if "no_of_dependents" in clean and clean["no_of_dependents"] != int(clean["no_of_dependents"]):
        errors["no_of_dependents"] = text(lang, "api.integer")

    return clean, errors


def range_warnings(clean: dict, lang: str = DEFAULT_LANG):
    """Eğitim verisinin dışında kalan değerler için uyarı üretir."""
    warnings = []
    ranges = MODEL_INFO.get("feature_ranges", {})
    for field in RAW_COLUMNS:
        if field in CHOICE_FIELDS or field not in ranges:
            continue
        low, high = ranges[field]
        if not low <= clean[field] <= high:
            warnings.append(text(
                lang, "api.range_warning",
                label=text(lang, f"field.{field}"), low=fmt_int(low, lang), high=fmt_int(high, lang),
            ))
    return warnings


def explain(clean: dict, features, probability: float, lang: str = DEFAULT_LANG):
    row = features.iloc[0]
    factors = []

    score = fmt_int(clean["cibil_score"], lang)
    if clean["cibil_score"] >= CIBIL_THRESHOLD:
        factors.append({
            "tone": "positive",
            "title": text(lang, "api.score_above_title", score=score),
            "text": text(lang, "api.score_above_text"),
        })
    else:
        factors.append({
            "tone": "negative",
            "title": text(lang, "api.score_below_title", score=score),
            "text": text(lang, "api.score_below_text"),
        })

    pct = fmt_int(row["yearly_payment_to_income"] * 100, lang)
    factors.append({
        "tone": "neutral",
        "title": text(lang, "api.payment_title", pct=pct),
        "text": text(lang, "api.payment_text", pct=pct, term=fmt_int(clean["loan_term"], lang)),
    })

    factors.append({
        "tone": "neutral",
        "title": text(lang, "api.loan_income_title", ratio=fmt_dec(row["loan_to_income"], lang)),
        "text": (
            text(lang, "api.assets_text", ratio=fmt_dec(1 / row["loan_to_assets"], lang))
            if row["total_assets"] > 0 else text(lang, "api.no_assets_text")
        ),
    })

    if 0.35 < probability < 0.65:
        factors.append({
            "tone": "neutral",
            "title": text(lang, "api.uncertain_title"),
            "text": text(lang, "api.uncertain_text"),
        })

    return factors


@app.route("/", defaults={"lang": "tr"})
@app.route("/en/", defaults={"lang": "en"})
def index(lang):
    return render_template("index.html", info=MODEL_INFO, active="index")


@app.route("/model", defaults={"lang": "tr"})
@app.route("/en/model", defaults={"lang": "en"})
def about(lang):
    importances = [
        {"label": text(lang, f"field.{item['feature']}"), "value": item["importance"]}
        for item in MODEL_INFO["feature_importances"]
    ]
    return render_template("about.html", info=MODEL_INFO, importances=importances, active="about")


@app.post("/api/predict")
def predict():
    lang = current_lang()
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        payload = request.form.to_dict()
    clean, errors = validate(payload, lang)
    if errors:
        return jsonify({"errors": errors}), 400

    features = prepare_input(clean, BUNDLE)
    probability = float(BUNDLE["model"].predict_proba(features)[0, 1])
    approved = probability >= 0.5

    return jsonify({
        "approved": approved,
        "probability": probability,
        "ratios": {
            "yearly_payment_to_income": float(features.iloc[0]["yearly_payment_to_income"]),
            "loan_to_income": float(features.iloc[0]["loan_to_income"]),
            "total_assets": float(features.iloc[0]["total_assets"]),
        },
        "factors": explain(clean, features, probability, lang),
        "warnings": range_warnings(clean, lang),
    })


@app.errorhandler(HTTPException)
def handle_http_error(error):
    lang = current_lang()
    kind = error.code if error.code in (404, 413, 500) else "other"
    title = text(lang, f"http.{kind}_title")
    message = text(lang, f"http.{kind}_text")
    if request.path.startswith("/api/"):
        return jsonify({"error": message}), error.code
    return render_template("error.html", code=error.code, title=title, text=message, active=None), error.code


if __name__ == "__main__":
    # Hata ayıklama modu yalnızca açıkça istenirse açılır: FLASK_DEBUG=1 python app.py
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")
