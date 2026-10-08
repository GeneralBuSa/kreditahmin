# KrediTahmin

[Türkçe](README.md) | **English**

[![Tests](https://github.com/GeneralBuSa/kreditahmin/actions/workflows/test.yml/badge.svg)](https://github.com/GeneralBuSa/kreditahmin/actions/workflows/test.yml)

A machine learning web app that predicts whether a loan application will be approved. The user enters the application details; the model shows its decision, the approval probability and the reasoning behind it.

**Live site:** [generalbusa.github.io/kreditahmin/en](https://generalbusa.github.io/kreditahmin/en/) · [Türkçe](https://generalbusa.github.io/kreditahmin/)

Capstone project of the **Data Science and Machine Learning 2026: 100-Day Bootcamp**. *KrediTahmin* is Turkish for "loan prediction".

![KrediTahmin, English version](screenshots/ingilizce.png)

## Features

- **Prediction with reasoning:** the approval decision, the approval probability and an explanation of the variables that drove the decision.
- **Section menus (scrollspy):** a step bar above the form on the home page (Credit score, Loan request, Income, Assets) and a table of contents on the "How does the model work?" page; the section you're on is highlighted as you scroll.
- **Warnings:** when a value falls outside the range of the training data, the app says the prediction may be unreliable.
- **Turkish and English:** Turkish pages live at `/` and `/model`, English pages at `/en/` and `/en/model`. Switch languages with the **TR | EN** toggle in the top right.
- **Light and dark theme:** follows the operating system setting on first visit; can be changed with the toggle in the top right, and the choice is remembered in the browser.
- **Serverless version:** on GitHub Pages the model runs in the browser, with results identical to scikit-learn.
- **Mobile friendly**, usable with a keyboard and screen reader, and respects the "reduce motion" setting.

## Results

| | |
|---|---|
| Final model | Gradient Boosting |
| Test accuracy | **99.77%** (852 of 854 applications correct) |
| ROC AUC | 0.998 |
| Baseline (rule: "approve if credit score ≥ 550") | 95.8% |

Ten classification algorithms were compared. The biggest gain came not from the choice of model but from **feature engineering**: the derived *annual payment / annual income* ratio cut the best model's error roughly 20-fold.

| Model | Before feature engineering | After |
|---|---|---|
| Gradient Boosting | 97.8% | **99.9%** |
| Decision Tree | 97.2% | 99.9% |
| LightGBM | 98.4% | 99.9% |
| AdaBoost | 96.6% | 99.9% |
| Random Forest | 97.8% | 99.8% |
| XGBoost | 98.2% | 99.8% |
| SVM | 93.9% | 95.4% |
| Logistic Regression | 91.7% | 93.6% |
| KNN | 88.6% | 89.2% |
| Naive Bayes | 76.3% | 62.7% |

*(5-fold cross-validation accuracy on the training data)*

## Project steps

1. **Data cleaning:** whitespace in column names and values was removed; 28 negative residential asset values were set to 0.
2. **EDA:** a sharp threshold at a credit score of 550 was found. Education, employment and family size have no effect on approval.
3. **Feature engineering:** total assets, loan / income, loan / assets and annual payment / income ratios were derived.
4. **Model comparison:** Logistic Regression, SVM, Naive Bayes, KNN, Decision Tree, Random Forest, AdaBoost, Gradient Boosting, XGBoost, LightGBM.
5. **Transformation:** Yeo-Johnson was tried; it was not used because it didn't improve the linear model.
6. **Hyperparameter tuning:** 6 models were tuned with RandomizedSearchCV.
7. **Deployment:** the model was saved with `pickle` and connected to a Flask app.

The full analysis is in [`notebooks/loan_approval_training.ipynb`](notebooks/loan_approval_training.ipynb) (written in Turkish).

## Screenshots

The screenshots below show the Turkish interface; the English version looks the same.

| Dark theme: approved application | Light theme: rejected application |
|---|---|
| ![Dark theme, approved application](screenshots/karanlik_onay.png) | ![Light theme, rejected application](screenshots/acik_ret.png) |

| Light theme: home page | Mobile view |
|---|---|
| ![Light theme, home page](screenshots/acik_tema.png) | ![Mobile view](screenshots/mobil.png) |

<details>
<summary>"How does the model work?" page (full page)</summary>

![Model page](screenshots/karanlik_model.png)

</details>

## Installation and running

Requires Python 3.12 or newer (`numpy` 2.5 does not support Python 3.11). The recommended version is 3.13, as set in `.python-version`.

```bash
git clone https://github.com/GeneralBuSa/kreditahmin.git
cd kreditahmin
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS / Linux: source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000` in your browser (English: `http://127.0.0.1:5000/en/`). On Windows, use `127.0.0.1` rather than `localhost`: `localhost` tries the IPv6 address first, adding a ~0.2 second delay to every request.

While developing, turn on debug mode so the server restarts when the code changes and shows error details:

```bash
FLASK_DEBUG=1 python app.py
```

In Windows PowerShell: `$env:FLASK_DEBUG=1; python app.py`. Debug mode is off by default for security; never turn it on on a server.

**In PyCharm:** open the project → create a new virtualenv under *Settings → Python Interpreter* → run `pip install -r requirements.txt` in the terminal → right-click `app.py` and choose *Run 'app'*.

### Settings (environment variables)

| Variable | Purpose | Default |
|---|---|---|
| `FLASK_DEBUG` | Turns on debug mode when set to `1` (when running with `python app.py`) | off |
| `SITE_URL` | The site's address, used for the full URLs in link previews (Open Graph) and for the GitHub Pages 404 page | Flask: the request's address · Static site: `https://generalbusa.github.io/kreditahmin` |

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```

The tests check:

- **Prediction:** that the API predicts correctly and rejects missing fields, values like `nan` / `inf`, and very large numbers with a 400 error.
- **GitHub Pages version:** that the `docs/` folder is up to date (if this fails, run `python scripts/build_static.py`), and that `predictor.js`, which runs in the browser, applies the same validation rules and produces the same results as the Flask API in both languages. This test needs [Node.js](https://nodejs.org); it is skipped if Node isn't installed.
- **Language support:** that no Turkish text is left on the English pages, in API responses or in the JavaScript files, and that both languages have the same text keys.
- **Security:** the security headers, that pages contain no inline scripts, that large requests are rejected, and that error pages don't reflect user input.

Tests run automatically on GitHub Actions on every push (`.github/workflows/test.yml`).

## Deployment

The project has two versions of the site.

### 1. GitHub Pages (recommended, no extra account needed)

The `docs/` folder is the static version of the site. The model is read from `docs/model.json` and predictions run **in the browser**: no server is needed and the site never goes to sleep.

1. Open **Settings → Pages** in the repository (the repository must be **public**).
2. Under *Source*, choose **Deploy from a branch**; *Branch*: `main`, folder: `/docs` → **Save**.
3. Within 1–2 minutes the site is live at [generalbusa.github.io/kreditahmin](https://generalbusa.github.io/kreditahmin/).

Rebuild the static version whenever the model, templates, texts, CSS or JavaScript change:

```bash
python scripts/build_static.py
```

If the repository is published under a different user name or repository name, pass the address at build time: `SITE_URL=https://user.github.io/repo python scripts/build_static.py`.

### 2. Render (the Flask app itself)

The repository already includes `render.yaml` and `.python-version`.

1. Sign in to [render.com](https://render.com) with your GitHub account.
2. Choose **New → Blueprint** and connect this repository; Render reads `render.yaml` and sets up the service.
3. When the setup finishes, the site is available at an address like `https://kreditahmin.onrender.com`.

On the free plan the service sleeps after 15 minutes of inactivity; the next first visit takes about a minute.

## API

```bash
curl -X POST "http://127.0.0.1:5000/api/predict?lang=en" \
  -H "Content-Type: application/json" \
  -d '{"cibil_score": 778, "loan_amount": 29900000, "loan_term": 12, "income_annum": 9600000,
       "no_of_dependents": 2, "education": "Graduate", "self_employed": "No",
       "residential_assets_value": 2400000, "commercial_assets_value": 17600000,
       "luxury_assets_value": 22700000, "bank_asset_value": 8000000}'
```

A successful response contains `approved`, `probability`, the computed ratios (`ratios`), the reasons for the decision (`factors`) and warnings for values outside the training range (`warnings`).

- `?lang=en` returns the messages in English; the default language is Turkish.
- Invalid input returns **400** with a message per field: `{"errors": {"cibil_score": "..."}}`.
- Requests larger than 16 KB are rejected with **413**. Other errors return `{"error": "..."}`.

## Security

- **Content Security Policy (CSP):** scripts, styles, fonts and images can only load from the site itself; pages contain no inline scripts. It is sent as a header by the Flask version and as a `<meta>` tag on GitHub Pages.
- **Security headers:** `X-Content-Type-Options`, `X-Frame-Options` (stops other sites from embedding the page in a frame), `Referrer-Policy`, `Permissions-Policy`; `Strict-Transport-Security` over HTTPS.
- **Input validation:** every field is checked for type and range; non-numeric, infinite or excessively large values are rejected. User data is always written to the page as plain text.
- **Debug mode** is off by default; error pages don't reveal internal details.
- The app uses no accounts, sessions, cookies or database; the information entered is not stored.
- Dependencies were scanned with [`pip-audit`](https://pypi.org/project/pip-audit/); no known vulnerabilities were found.

## Project structure

```
kreditahmin/
├── app.py                  Flask app (pages, /api/predict, security headers)
├── requirements.txt        App dependencies (installed by Render)
├── requirements-dev.txt    + test dependencies
├── render.yaml             Render settings
├── .github/workflows/      GitHub Actions: runs the tests on every push
├── docs/                   Static version for GitHub Pages (generated by scripts/build_static.py)
├── scripts/build_static.py Exports the model to model.json and builds the static site
├── src/
│   ├── features.py         Feature engineering (same as in the notebook)
│   └── i18n.py             All Turkish and English texts on the site
├── model/
│   ├── loan_model.pkl      Trained model + category mappings + column order
│   └── model_info.json     Metrics shown on the "How does the model work?" page
├── notebooks/
│   └── loan_approval_training.ipynb   Data analysis and model training
├── templates/              HTML templates (Jinja): application, model and error pages
├── static/
│   ├── css/style.css       Design (light and dark theme)
│   ├── js/                 boot.js (theme, texts), app.js (form), theme.js (toggles), scrollspy.js,
│   │                       predictor.js (model running in the browser on GitHub Pages)
│   ├── img/                Guilloche patterns and link preview image (og-image.png)
│   └── fonts/              Archivo typeface
├── tests/
│   ├── test_app.py         Tests
│   └── run_predictor.js    Runs predictor.js in Node (for the comparison test)
└── screenshots/
```

## Adding new text

Every user-facing text lives in [`src/i18n.py`](src/i18n.py); no text is written directly into the templates or JavaScript files. When you add a text, add it in both languages and then run `python scripts/build_static.py`. The tests catch a text missing in one language, or Turkish leaking into the English pages.

## Retraining the model

The notebook is written to run on Kaggle. Open a new Kaggle notebook, import this file, add the [Loan Approval Prediction Dataset](https://www.kaggle.com/datasets/architsharma01/loan-approval-prediction-dataset) with **Add Input**, and run it. Put the resulting `loan_model.pkl` and `model_info.json` into the `model/` folder, then run `python scripts/build_static.py`.

> A pickle file must be loaded with the same scikit-learn version it was saved with. If you retrain the model on Kaggle, set the `scikit-learn` version in `requirements.txt` to match Kaggle's (it is recorded in the `sklearn_version` field of `model_info.json`). Pickle files can contain executable code; only load model files you produced yourself.

## Good to know

- This is an educational project and does not make real lending decisions.
- Amounts are in Indian rupees (₹). The credit score follows India's CIBIL system (300–900). Turkey's Findeks score (1–1900) is a different scale and there is no official conversion between the two, so don't enter a Findeks score into this form directly.
- The rules in the data are too sharp to occur in real bank data; the data is most likely synthetic. The 99.8% accuracy is specific to this dataset.
- The app shows a warning when a value falls outside the range of the training data.

## Technologies

Python, pandas, scikit-learn, XGBoost, LightGBM (model comparison), Flask, HTML/CSS/JavaScript (no external libraries). The guilloche patterns on the page were generated with Python, inspired by the security printing on banknotes and certificates. Typeface: [Archivo](https://github.com/Omnibus-Type/Archivo) (SIL Open Font License).

## License

[MIT](LICENSE)
