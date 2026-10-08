"""GitHub Pages için sitenin statik sürümünü docs/ klasörüne üretir.

Flask uygulaması tahmini sunucuda yapar. GitHub Pages ise sadece statik
dosya barındırabildiği için bu script:
  1. loan_model.pkl içindeki Gradient Boosting ağaçlarını docs/model.json'a aktarır,
  2. sayfaları Flask şablonlarından HTML olarak üretir,
  3. CSS / JS / font dosyalarını kopyalar.
Tarayıcıda static/js/predictor.js modeli model.json'dan okuyup çalıştırır.

Kullanım:  python scripts/build_static.py
"""
import json
import os
import posixpath
import re
import shutil
import sys
from pathlib import Path
from urllib.parse import urlparse

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import BUNDLE, MODEL_INFO, app  # noqa: E402
from src.i18n import LANGUAGES, export  # noqa: E402

DOCS = ROOT / "docs"


def export_model():
    model = BUNDLE["model"]
    columns = BUNDLE["feature_columns"]
    init = float(model._raw_predict_init(np.zeros((1, len(columns))))[0, 0])

    trees = []
    for estimator in model.estimators_[:, 0]:
        tree = estimator.tree_
        trees.append({
            "feature": tree.feature.tolist(),
            "threshold": [float(t) for t in tree.threshold],
            "left": tree.children_left.tolist(),
            "right": tree.children_right.tolist(),
            "value": [float(v) for v in tree.value[:, 0, 0]],
        })

    return {
        "model_name": BUNDLE.get("model_name", type(model).__name__),
        "features": columns,
        "init": init,
        "learning_rate": float(model.learning_rate),
        "trees": trees,
        "education_map": BUNDLE["education_map"],
        "self_employed_map": BUNDLE["self_employed_map"],
        "feature_ranges": MODEL_INFO.get("feature_ranges", {}),
        "messages": {lang: export(lang, "api.", "field.", "num.") for lang in LANGUAGES},
    }


# GitHub Pages adresi; paylaşım önizlemesindeki (Open Graph) tam adresler ve 404 sayfası için.
# Repo başka bir kullanıcı/isimle yayınlanıyorsa: SITE_URL=https://<kullanici>.github.io/<repo>
SITE_URL = os.environ.get("SITE_URL", "https://generalbusa.github.io/kreditahmin").rstrip("/")

# Flask adresi -> docs/ içindeki dosya.
PAGES = {
    "/": "index.html",
    "/model": "model.html",
    "/en/": "en/index.html",
    "/en/model": "en/model.html",
}
# GitHub Pages, bulunamayan her adreste docs/404.html dosyasını gösterir.
NOT_FOUND = ("/olmayan-sayfa", "404.html")
LINK_PATTERN = re.compile(r'(href|src|content)="(/[^"#]*)(#[^"]*)?"')


def relative_links(html: str, page: str, base_path: str | None = None) -> str:
    """Kök-göreli bağlantıları (/static/..., /en/model) statik sitede çalışır hâle getirir.

    Normalde sayfanın konumuna göre göreli yapar. base_path verilirse (404 sayfası
    her adreste açılabildiği için) sitenin kök yolundan başlayan mutlak yol kullanır.
    """
    page_dir = posixpath.dirname(page) or "."

    def replace(match):
        attr, path, fragment = match.group(1), match.group(2), match.group(3) or ""
        if path in PAGES:
            target = PAGES[path]
        elif path.startswith("/static/") or path == "/model.json":
            target = path.lstrip("/")
        else:
            raise ValueError(f"Statik sitede karşılığı olmayan bağlantı: {path} ({page})")
        link = f"{base_path}/{target}" if base_path is not None else posixpath.relpath(target, page_dir)
        return f'{attr}="{link}{fragment}"'

    return LINK_PATTERN.sub(replace, html)


def render_pages():
    """Sayfaları statik site için HTML olarak üretir: {dosya yolu: html}."""
    app.config["STATIC_SITE"] = True
    previous_site_url = app.config["SITE_URL"]
    app.config["SITE_URL"] = SITE_URL
    try:
        client = app.test_client()
        pages = {}
        for route, page in PAGES.items():
            response = client.get(route)
            if response.status_code != 200:
                raise RuntimeError(f"{route} sayfası üretilemedi (HTTP {response.status_code}).")
            pages[page] = relative_links(response.get_data(as_text=True), page)

        route, page = NOT_FOUND
        response = client.get(route)
        if response.status_code != 404:
            raise RuntimeError(f"404 sayfası üretilemedi (HTTP {response.status_code}).")
        pages[page] = relative_links(response.get_data(as_text=True), page, urlparse(SITE_URL).path)
        return pages
    finally:
        app.config["STATIC_SITE"] = False
        app.config["SITE_URL"] = previous_site_url


def main():
    if DOCS.exists():
        shutil.rmtree(DOCS)
    DOCS.mkdir()

    with open(DOCS / "model.json", "w", encoding="utf-8") as f:
        json.dump(export_model(), f, separators=(",", ":"))

    for page, html in render_pages().items():
        (DOCS / page).parent.mkdir(parents=True, exist_ok=True)
        (DOCS / page).write_text(html, encoding="utf-8")

    shutil.copytree(ROOT / "static", DOCS / "static")
    (DOCS / ".nojekyll").write_text("")
    print(f"Statik site üretildi: {DOCS}")


if __name__ == "__main__":
    main()
