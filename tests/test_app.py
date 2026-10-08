import html
import json
import re
import shutil
import string
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import app  # noqa: E402
from src.i18n import LANGUAGE_NAMES, LANGUAGES, TEXTS, export  # noqa: E402

APPROVED = {
    "cibil_score": 778, "loan_amount": 29900000, "loan_term": 12, "income_annum": 9600000,
    "no_of_dependents": 2, "education": "Graduate", "self_employed": "No",
    "residential_assets_value": 2400000, "commercial_assets_value": 17600000,
    "luxury_assets_value": 22700000, "bank_asset_value": 8000000,
}
REJECTED = {
    "cibil_score": 417, "loan_amount": 12200000, "loan_term": 8, "income_annum": 4100000,
    "no_of_dependents": 0, "education": "Not Graduate", "self_employed": "Yes",
    "residential_assets_value": 2700000, "commercial_assets_value": 2200000,
    "luxury_assets_value": 8800000, "bank_asset_value": 3300000,
}


def client():
    app.config["TESTING"] = True
    return app.test_client()


def test_pages_load():
    c = client()
    assert c.get("/").status_code == 200
    assert c.get("/model").status_code == 200


def test_approved_example():
    data = client().post("/api/predict", json=APPROVED).get_json()
    assert data["approved"] is True
    assert data["probability"] > 0.9


def test_rejected_example():
    data = client().post("/api/predict", json=REJECTED).get_json()
    assert data["approved"] is False
    assert data["probability"] < 0.1


def test_missing_field_returns_error():
    payload = dict(APPROVED)
    payload.pop("income_annum")
    response = client().post("/api/predict", json=payload)
    assert response.status_code == 400
    assert "income_annum" in response.get_json()["errors"]


def test_invalid_cibil_score():
    response = client().post("/api/predict", json={**APPROVED, "cibil_score": 1200})
    assert response.status_code == 400
    assert "cibil_score" in response.get_json()["errors"]


def test_zero_assets_do_not_crash():
    payload = {**APPROVED, "residential_assets_value": 0, "commercial_assets_value": 0,
               "luxury_assets_value": 0, "bank_asset_value": 0}
    response = client().post("/api/predict", json=payload)
    assert response.status_code == 200


def test_out_of_range_warning():
    data = client().post("/api/predict", json={**APPROVED, "loan_term": 30}).get_json()
    assert any("Vade" in w for w in data["warnings"])


def test_static_model_export_matches_sklearn():
    """GitHub Pages sürümündeki model.json, pickle'daki modelle aynı sonucu vermeli."""
    import math

    import pandas as pd

    from app import BUNDLE
    from scripts.build_static import export_model
    from src.features import prepare_input

    exported = export_model()

    def predict_from_json(row):
        x = [float(row[f]) for f in exported["features"]]
        import numpy as np
        x = np.array(x, dtype=np.float32)
        raw = exported["init"]
        for tree in exported["trees"]:
            node = 0
            while tree["left"][node] != -1:
                f = tree["feature"][node]
                node = tree["left"][node] if x[f] <= tree["threshold"][node] else tree["right"][node]
            raw += exported["learning_rate"] * tree["value"][node]
        return 1 / (1 + math.exp(-raw))

    for application in (APPROVED, REJECTED):
        features = prepare_input(application, BUNDLE)
        expected = BUNDLE["model"].predict_proba(features)[0, 1]
        assert abs(predict_from_json(features.iloc[0]) - expected) < 1e-9


ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("value", ["nan", "inf", "-inf", "Infinity", "1e400", float("nan")])
def test_non_finite_numbers_return_400(value):
    response = client().post("/api/predict", json={**APPROVED, "income_annum": value})
    assert response.status_code == 400
    assert response.get_json()["errors"]["income_annum"] == "Sayı girin."


def test_too_large_number_returns_400():
    response = client().post("/api/predict", json={**APPROVED, "loan_amount": 1e30})
    assert response.status_code == 400
    assert "loan_amount" in response.get_json()["errors"]


def test_tiny_income_returns_400():
    # 0'a çok yakın gelir, oranları float32 sınırının dışına taşırıyordu.
    response = client().post("/api/predict", json={**APPROVED, "income_annum": 1e-30})
    assert response.status_code == 400
    assert "income_annum" in response.get_json()["errors"]


@pytest.mark.parametrize("payload", [[1, 2], "metin", 42])
def test_non_object_json_returns_400(payload):
    assert client().post("/api/predict", json=payload).status_code == 400


def test_non_string_choice_returns_400():
    response = client().post("/api/predict", json={**APPROVED, "education": ["Graduate"]})
    assert response.status_code == 400
    assert "education" in response.get_json()["errors"]


def test_404_page_is_turkish():
    response = client().get("/olmayan-sayfa")
    assert response.status_code == 404
    assert "Sayfa bulunamadı" in response.get_data(as_text=True)


def test_api_errors_are_json():
    response = client().get("/api/predict")
    assert response.status_code == 405
    assert "error" in response.get_json()


def test_docs_are_up_to_date():
    """docs/ klasörü (GitHub Pages) uygulamanın güncel hâliyle aynı olmalı."""
    from scripts.build_static import DOCS, export_model, render_pages

    hint = "docs/ güncel değil. `python scripts/build_static.py` çalıştırın."

    built_model = json.loads((DOCS / "model.json").read_text(encoding="utf-8"))
    assert built_model == json.loads(json.dumps(export_model())), hint

    for filename, html in render_pages().items():
        assert (DOCS / filename).read_text(encoding="utf-8") == html, f"{hint} ({filename})"

    def normalized(path):
        return path.read_bytes().replace(b"\r\n", b"\n")

    source_dir = ROOT / "static"
    for source in source_dir.rglob("*"):
        if source.is_file():
            built = DOCS / "static" / source.relative_to(source_dir)
            assert built.is_file() and normalized(built) == normalized(source), f"{hint} ({built})"


# Hem Flask'a hem tarayıcıdaki predictor.js'e gönderilip sonuçları karşılaştırılan başvurular.
PARITY_CASES = [
    APPROVED,
    REJECTED,
    {**APPROVED, "residential_assets_value": 0, "commercial_assets_value": 0,
     "luxury_assets_value": 0, "bank_asset_value": 0},
    {**APPROVED, "loan_term": 30, "cibil_score": 300},
    {**REJECTED, "cibil_score": 549},
    {**REJECTED, "cibil_score": 550},
    {k: v for k, v in APPROVED.items() if k != "income_annum"},
    {**APPROVED, "income_annum": ""},
    {**APPROVED, "cibil_score": 1200},
    {**APPROVED, "cibil_score": 299},
    {**APPROVED, "income_annum": "nan"},
    {**APPROVED, "loan_amount": "Infinity"},
    {**APPROVED, "loan_amount": "1e400"},
    {**APPROVED, "loan_amount": "abc"},
    {**APPROVED, "luxury_assets_value": -5},
    {**APPROVED, "luxury_assets_value": 1e16},
    {**APPROVED, "income_annum": 0},
    {**APPROVED, "income_annum": 0.5},
    {**APPROVED, "loan_amount": 0},
    {**APPROVED, "loan_term": 0.5},
    {**APPROVED, "no_of_dependents": 1.5},
    {**APPROVED, "education": "PhD"},
    {**APPROVED, "self_employed": ""},
]


@pytest.mark.skipif(shutil.which("node") is None, reason="Node.js kurulu değil")
@pytest.mark.parametrize("lang", LANGUAGES)
def test_browser_predictor_matches_flask(tmp_path, lang):
    """GitHub Pages sürümü (predictor.js) Flask API'siyle aynı doğrulama ve sonuçları üretmeli."""
    from scripts.build_static import export_model

    model_path = tmp_path / "model.json"
    model_path.write_text(json.dumps(export_model()), encoding="utf-8")
    output = subprocess.run(
        ["node", str(ROOT / "tests" / "run_predictor.js"), str(model_path)],
        input=json.dumps([{"lang": lang, "payload": p} for p in PARITY_CASES]),
        capture_output=True, text=True, encoding="utf-8", check=True,
    ).stdout
    js_results = json.loads(output)

    c = client()
    for payload, js in zip(PARITY_CASES, js_results, strict=True):
        response = c.post(f"/api/predict?lang={lang}", json=payload)
        py = response.get_json()
        assert js["ok"] == (response.status_code == 200), payload
        if not js["ok"]:
            assert js["data"]["errors"] == py["errors"], payload
            continue
        js_data = js["data"]
        assert js_data["approved"] == py["approved"], payload
        assert abs(js_data["probability"] - py["probability"]) < 1e-9, payload
        assert js_data["factors"] == py["factors"], payload
        assert js_data["warnings"] == py["warnings"], payload


# ---------- Dil desteği ----------

TURKISH_CHARS = re.compile("[çğıöşüÇĞİÖŞÜ]")


def turkish_fragments():
    """Türkçe metinlerin İngilizce sayfada aranacak parçaları (HTML ve {yer tutucular} hariç)."""
    for key, tr in TEXTS["tr"].items():
        if key.startswith("num.") or tr == TEXTS["en"][key]:
            continue
        plain = html.unescape(re.sub(r"<[^>]+>", "", tr))
        for fragment in re.split(r"\{\w+\}", plain):
            fragment = fragment.strip()
            if len(fragment) >= 4:
                yield key, fragment


def find_turkish(content: str) -> list:
    problems = [f"Türkçe harf: ...{content[max(m.start() - 30, 0):m.end() + 30]}..."
                for m in TURKISH_CHARS.finditer(content)]
    problems += [f"Türkçe metin ({key}): {fragment}"
                 for key, fragment in turkish_fragments() if fragment in content]
    return problems


def test_translations_have_same_keys_and_placeholders():
    formatter = string.Formatter()
    assert TEXTS["tr"].keys() == TEXTS["en"].keys()
    for key in TEXTS["tr"]:
        names = [{name for _, name, _, _ in formatter.parse(TEXTS[lang][key]) if name} for lang in LANGUAGES]
        assert names[0] == names[1], key


def test_english_texts_have_no_turkish_characters():
    for key, value in TEXTS["en"].items():
        assert not TURKISH_CHARS.search(value), f"{key}: {value}"


@pytest.mark.parametrize("path, status", [("/en/", 200), ("/en/model", 200), ("/en/olmayan-sayfa", 404)])
def test_english_pages_have_no_turkish(path, status):
    response = client().get(path)
    assert response.status_code == status
    page = response.get_data(as_text=True)
    assert '<html lang="en">' in page

    embedded = json.loads(re.search(r'<script id="kredi-i18n" type="application/json">(.*?)</script>', page).group(1))
    assert embedded == {"lang": "en", **export("en", "js.", "num.")}

    # Türkçe sayfaya giden dil düğmesi (lang="tr") bilerek Türkçe kalır.
    page = re.sub(r'<a [^>]*\blang="tr"[^>]*>.*?</a>', "", page)
    assert find_turkish(html.unescape(page)) == []


@pytest.mark.parametrize("path, status", [("/", 200), ("/model", 200), ("/olmayan-sayfa", 404)])
def test_turkish_pages_are_turkish(path, status):
    response = client().get(path)
    assert response.status_code == status
    page = html.unescape(response.get_data(as_text=True))
    assert '<html lang="tr">' in page
    page = re.sub(r'<a [^>]*\blang="en"[^>]*>.*?</a>', "", page)
    leaks = [key for key, en in TEXTS["en"].items()
             if not key.startswith("num.") and en != TEXTS["tr"][key] and len(en) > 20
             and "{" not in en and "<" not in en and en in page]
    assert leaks == []


def test_language_switch_links():
    tr_page = client().get("/model").get_data(as_text=True)
    en_page = client().get("/en/model").get_data(as_text=True)
    for page, current in ((tr_page, "tr"), (en_page, "en")):
        assert 'href="/model" hreflang="tr"' in page
        assert 'href="/en/model" hreflang="en"' in page
        assert f'hreflang="{current}" lang="{current}" title="{LANGUAGE_NAMES[current]}" aria-label="{LANGUAGE_NAMES[current]}" aria-current="true"' in page


def test_static_files_are_versioned_and_cached():
    c = client()
    page = c.get("/").get_data(as_text=True)
    css = re.search(r'href="(/static/css/style\.css\?v=\w+)"', page).group(1)
    assert "max-age=31536000" in c.get(css).headers["Cache-Control"]
    # Sürümsüz adres önbelleğe uzun süre alınmamalı.
    assert "max-age=31536000" not in c.get("/static/css/style.css").headers.get("Cache-Control", "")


def test_english_api_has_no_turkish():
    c = client()
    for payload in PARITY_CASES:
        data = c.post("/api/predict?lang=en", json=payload).get_json()
        assert find_turkish(json.dumps(data, ensure_ascii=False)) == [], payload
    assert find_turkish(json.dumps(c.get("/api/yok?lang=en").get_json(), ensure_ascii=False)) == []


def test_api_defaults_to_turkish():
    data = client().post("/api/predict", json={**APPROVED, "cibil_score": 1200}).get_json()
    assert data["errors"]["cibil_score"] == TEXTS["tr"]["api.cibil_range"]


def test_javascript_has_no_hardcoded_texts():
    """Kullanıcıya görünen metinler JS dosyalarına yazılmamalı; src/i18n.py'den gelmeli."""
    for name in ("app.js", "theme.js", "predictor.js"):
        source = (ROOT / "static" / "js" / name).read_text(encoding="utf-8")
        source = re.sub(r"/\*.*?\*/|//[^\n]*", "", source, flags=re.S)  # yorumlar hariç
        for lang in LANGUAGES:
            for key, value in TEXTS[lang].items():
                if key.startswith(("js.", "api.", "field.")) and len(value) >= 4:
                    assert value not in source, f"{name}: {key} = {value}"


# ---------- Güvenlik, paylaşım ve erişilebilirlik ----------

def test_large_request_is_rejected():
    response = client().post("/api/predict?lang=en", data="{" + " " * 50_000 + "}", content_type="application/json")
    assert response.status_code == 413
    assert response.get_json()["error"] == TEXTS["en"]["http.413_text"]


@pytest.mark.parametrize("path", ["/", "/en/model"])
def test_open_graph_tags(path):
    page = client().get(path, base_url="https://example.com").get_data(as_text=True)
    for prop in ("og:title", "og:description", "og:image", "og:url"):
        assert f'<meta property="{prop}"' in page, prop
    assert '<meta property="og:image" content="https://example.com/static/img/og-image.png">' in page
    assert (ROOT / "static" / "img" / "og-image.png").is_file()


def test_static_site_open_graph_uses_site_url():
    from scripts.build_static import SITE_URL, render_pages

    pages = render_pages()
    assert f'<meta property="og:image" content="{SITE_URL}/static/img/og-image.png">' in pages["index.html"]
    assert f'<meta property="og:url" content="{SITE_URL}/en/">' in pages["en/index.html"]
    # 404 sayfası her adreste açılabilir; bağlantıları sitenin kök yolundan başlamalı.
    base_path = urlparse(SITE_URL).path
    assert f'href="{base_path}/static/css/style.css?v=' in pages["404.html"]


def test_brand_link_has_accessible_name():
    page = client().get("/").get_data(as_text=True)
    assert 'class="brand" href="/" aria-label="KrediTahmin"' in page


# ---------- Güvenlik ----------

@pytest.mark.parametrize("path", ["/", "/en/model", "/olmayan-sayfa", "/static/css/style.css"])
def test_security_headers(path):
    headers = client().get(path).headers
    assert "script-src 'self'" in headers["Content-Security-Policy"]
    assert "frame-ancestors 'none'" in headers["Content-Security-Policy"]
    assert headers["X-Content-Type-Options"] == "nosniff"
    assert headers["X-Frame-Options"] == "DENY"
    assert headers["Referrer-Policy"] == "strict-origin-when-cross-origin"


def test_api_has_security_headers():
    headers = client().post("/api/predict", json=APPROVED).headers
    assert headers["X-Content-Type-Options"] == "nosniff"
    assert "Content-Security-Policy" in headers


def test_hsts_only_over_https():
    assert "Strict-Transport-Security" not in client().get("/").headers
    assert "Strict-Transport-Security" in client().get("/", base_url="https://example.com").headers


def test_pages_have_no_inline_scripts():
    """CSP satır içi script'e izin vermez; her <script> ya dosya ya da JSON veri olmalı."""
    from scripts.build_static import render_pages

    pages = [client().get(path).get_data(as_text=True) for path in ("/", "/model", "/en/", "/olmayan-sayfa")]
    pages += list(render_pages().values())
    for page in pages:
        assert "<meta http-equiv=\"Content-Security-Policy\"" in page
        for tag in re.findall(r"<script\b[^>]*>", page):
            assert ' src="' in tag or 'type="application/json"' in tag, tag
        assert not re.search(r"\son[a-z]+=\"", page), "satır içi olay işleyicisi (onclick vb.)"


def test_forwarded_host_is_ignored():
    page = client().get("/", headers={"X-Forwarded-Host": "evil.example"}).get_data(as_text=True)
    assert "evil.example" not in page


def test_error_pages_do_not_reflect_input():
    response = client().get("/<script>alert(1)</script>")
    assert response.status_code == 404
    assert "<script>alert(1)</script>" not in response.get_data(as_text=True)


def test_lang_parameter_only_affects_api():
    page = client().get("/?lang=en").get_data(as_text=True)
    assert '<html lang="tr">' in page
