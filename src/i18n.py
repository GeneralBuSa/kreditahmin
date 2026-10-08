"""Sitenin Türkçe ve İngilizce metinleri.

Tüm kullanıcıya görünen metinler burada durur:
  page.*   HTML şablonları (Jinja). HTML etiketi içerebilir.
  js.*     static/js/app.js ve theme.js (sayfaya JSON olarak gömülür).
  api.*    /api/predict hata mesajları, gerekçeler ve uyarılar.
  field.*  Alan ve değişken adları.
  num.*    Sayı biçimi.
  http.*   Hata sayfaları.
api.*, field.* ve num.* anahtarları GitHub Pages sürümü için docs/model.json'a da
aktarılır; böylece tarayıcıdaki predictor.js aynı metinleri kullanır.

Yeni metin eklerken iki dile de ekleyin; tests/test_app.py anahtarların ve
{yer tutucuların} iki dilde aynı olduğunu kontrol eder.
"""

LANGUAGES = ("tr", "en")
DEFAULT_LANG = "tr"
LANGUAGE_NAMES = {"tr": "Türkçe", "en": "English"}

KAGGLE_URL = "https://www.kaggle.com/datasets/architsharma01/loan-approval-prediction-dataset"

TEXTS = {
    "tr": {
        # ---------- Sayı biçimi ----------
        "num.locale": "tr-TR",
        "num.thousands": ".",
        "num.decimal": ",",
        "num.percent": "%{value}",

        # ---------- Genel sayfa ----------
        "page.meta_description": "Kredi başvurusunun onaylanıp onaylanmayacağını tahmin eden makine öğrenmesi uygulaması.",
        "page.og_image_alt": "KrediTahmin: Kredi başvurunuz onaylanır mı? %99,77 test doğruluğu.",
        "page.skip": "İçeriğe geç",
        "page.nav_label": "Ana menü",
        "page.nav_apply": "Başvuru",
        "page.nav_model_long": "Model nasıl çalışıyor?",
        "page.nav_model_short": "Model",
        "page.lang_label": "Dil",
        "page.theme_label": "Tema",
        "page.theme_light": "Aydınlık tema",
        "page.theme_dark": "Karanlık tema",
        "page.footer_disclaimer": f"Bu uygulama bir eğitim projesidir ve gerçek bir kredi kararı vermez. Model, Kaggle'daki <a href=\"{KAGGLE_URL}\">Loan Approval Prediction</a> veri setiyle eğitildi.",
        "page.footer_course": "Veri Bilimi ve Makine Öğrenmesi 2026: 100 Günlük Kamp kapanış projesi",
        "page.footer_source": "Kaynak kod GitHub'da",

        # ---------- Başvuru sayfası ----------
        "page.index_title": "KrediTahmin: Kredi başvurunuz onaylanır mı?",
        "page.hero_title": "Kredi başvurunuz onaylanır mı?",
        "page.hero_lede": "Başvuru bilgilerini girin. {count} kredi başvurusuyla eğitilmiş model, kararını ve gerekçesini birkaç saniyede göstersin.",
        "page.examples_label": "Örnek başvurular",
        "page.example_approved": "Onaylanan örneği dene",
        "page.example_rejected": "Reddedilen örneği dene",
        "page.score_title": "Kredi skoru",
        "page.score_help": "Modelin kararında en belirleyici bilgi. Bu, Hindistan'daki <strong>CIBIL</strong> skorudur (300–900). Türkiye'deki Findeks notuyla (1–1900) aynı ölçekte değildir; Findeks notunuzu buraya doğrudan girmeyin.",
        "page.score_threshold": "550 eşiği",
        "page.loan_title": "Kredi talebi",
        "page.loan_amount": "Kredi tutarı",
        "page.loan_term": "Vade",
        "page.years_suffix": "yıl",
        "page.term_help": "Eğitim verisinde 2 ile 20 yıl arası.",
        "page.income_title": "Gelir ve kişisel bilgiler",
        "page.income_short": "Gelir bilgileri",
        "page.steps_label": "Başvuru adımları",
        "page.income": "Yıllık gelir",
        "page.dependents": "Bakmakla yükümlü olunan kişi",
        "page.decrease": "Bir azalt",
        "page.increase": "Bir artır",
        "page.education": "Eğitim durumu",
        "page.graduate": "Üniversite mezunu",
        "page.not_graduate": "Mezun değil",
        "page.employment": "Çalışma şekli",
        "page.salaried": "Maaşlı",
        "page.self_employed": "Kendi işi",
        "page.assets_title": "Varlıklar",
        "page.assets_help": "Sahip olmadığınız varlık türü için 0 girin.",
        "page.asset_residential": "Konut",
        "page.asset_commercial": "Ticari",
        "page.asset_luxury": "Lüks (araç, mücevher vb.)",
        "page.asset_bank": "Banka hesapları",
        "page.slip_title": "Değerlendirme",
        "page.ratio_payment": "Yıllık taksit / gelir",
        "page.ratio_income": "Kredi / yıllık gelir",
        "page.ratio_assets": "Toplam varlık",
        "page.result_empty": "Formu doldurup <strong>Başvuruyu değerlendir</strong>'e bastığınızda modelin kararı burada görünecek.",
        "page.probability": "Onay olasılığı",

        # ---------- Model sayfası ----------
        "page.about_lede": "KrediTahmin'in arkasında bir <strong>{model}</strong> modeli var. Modeli eğitirken 10 farklı sınıflandırma algoritmasını karşılaştırdım; en büyük farkı ise algoritma seçimi değil, veriden türettiğim yeni değişkenler yarattı.",
        "page.toc_label": "Bu sayfada",
        "page.test_title": "Test sonucu",
        "page.test_text": "Model, eğitimde hiç görmediği {total} başvurudan <strong>{correct}</strong> tanesini doğru tahmin etti.",
        "page.accuracy": "Doğruluk (accuracy)",
        "page.baseline": "Sadece \"skor ≥ 550 ise onayla\" kuralı",
        "page.matrix_label": "Karışıklık matrisi",
        "page.matrix_caption": "Test setinde tahminler ve gerçek sonuçlar",
        "page.matrix_pred_reject": "Model: reddet",
        "page.matrix_pred_approve": "Model: onayla",
        "page.matrix_true_reject": "Gerçekte reddedildi",
        "page.matrix_true_approve": "Gerçekte onaylandı",
        "page.fe_title": "Feature engineering etkisi",
        "page.fe_text": "Bankalar ham tutarlardan çok oranlara bakar. Ham sütunlardan dört oran türettim: toplam varlık, kredi / gelir, kredi / varlık ve en önemlisi <strong>yıllık taksit / yıllık gelir</strong>. Grafikte her modelin bu değişkenler eklenmeden ve eklendikten sonraki 5-fold cross validation doğruluğu var.",
        "page.legend_before": "Yeni değişkenler olmadan",
        "page.legend_after": "Yeni değişkenlerle",
        "page.dumbbell_label": "{model}: önce {before}, sonra {after}",
        "page.dumbbell_before": "Önce: {value}",
        "page.dumbbell_after": "Sonra: {value}",
        "page.fe_note": "Ağaç tabanlı modellerin hepsi %99'un üzerine çıktı. Naive Bayes ise düştü: değişkenlerin birbirinden bağımsız olduğunu varsayıyor, türetilen oranlar ise mevcut sütunlarla güçlü bir şekilde ilişkili.",
        "page.importance_title": "Model neye bakıyor?",
        "page.importance_text": "Final modelin değişken önem dereceleri. Kararın büyük kısmını kredi skoru, kalanını yıllık taksit / gelir oranı belirliyor; gelir, varlıklar, eğitim ve meslek bilgisinin etkisi neredeyse yok.",
        "page.process_title": "Geliştirme süreci",
        "page.step_1": "<strong>Veri temizliği.</strong> Sütun adlarındaki ve değerlerdeki boşluklar temizlendi; 28 negatif konut varlığı 0 olarak düzeltildi. Eksik veya tekrar eden kayıt yoktu.",
        "page.step_2": "<strong>Keşifsel analiz.</strong> Kredi skorunda 550'de keskin bir eşik bulundu. Eğitim durumu, meslek ve aile büyüklüğünün onay oranına etkisi yok.",
        "page.step_3": "<strong>Feature engineering.</strong> Dört oran türetildi. En iyi modelin hatası yaklaşık 20 kat azaldı.",
        "page.step_4": "<strong>Model karşılaştırma.</strong> Logistic Regression, SVM, Naive Bayes, KNN, Decision Tree, Random Forest, AdaBoost, Gradient Boosting, XGBoost ve LightGBM denendi.",
        "page.step_5": "<strong>Transformation.</strong> Yeo-Johnson denendi; lineer modeli iyileştirmediği için kullanılmadı.",
        "page.step_6": "<strong>Hyperparameter tuning.</strong> En iyi 6 model RandomizedSearchCV ile ayarlandı; cross validation skoru en yüksek olan {model} seçildi.",
        "page.step_7": "<strong>Yayına alma.</strong> Model <code>pickle</code> ile kaydedildi ve bu Flask uygulamasına bağlandı.",
        "page.caveats_title": "Bilmeniz gerekenler",
        "page.caveat_1": "Veri setindeki tutarlar Hint Rupisi (₹) cinsinden. Kredi skoru, Hindistan'daki CIBIL sistemine (300–900) göre; Türkiye'deki Findeks notuyla (1–1900) aynı ölçekte değildir.",
        "page.caveat_2": "Verideki kurallar gerçek banka verisinde görülemeyecek kadar keskin; büyük ihtimalle sentetik bir veri. %99,8'lik başarı bu veri setine özgü.",
        "page.caveat_3": "Düşük kredi skorlu başvurularda model, yüksek taksit / gelir oranını onayla ilişkilendiriyor. Bu desen veriden geliyor; gerçek bankacılık mantığını yansıtmıyor.",
        "page.caveat_4": "Eğitim verisindeki aralığın dışında kalan değerler girildiğinde uygulama uyarı gösterir; o bölgedeki tahminler güvenilir değildir.",

        # ---------- Hata sayfaları ----------
        "http.code": "Hata {code}",
        "http.back": "Başvuru sayfasına dön",
        "http.404_title": "Sayfa bulunamadı",
        "http.404_text": "Aradığınız sayfa yok ya da taşınmış olabilir.",
        "http.413_title": "İstek çok büyük",
        "http.413_text": "Gönderilen veri izin verilen boyutu aşıyor.",
        "http.500_title": "Bir şeyler ters gitti",
        "http.500_text": "Sunucuda beklenmeyen bir hata oluştu. Biraz sonra tekrar deneyin.",
        "http.other_title": "Bir hata oluştu",
        "http.other_text": "İsteğiniz işlenemedi.",

        # ---------- JavaScript ----------
        "js.submit": "Başvuruyu değerlendir",
        "js.submitting": "Değerlendiriliyor…",
        "js.score_above": "Eşiğin üzerinde",
        "js.score_below": "Eşiğin altında",
        "js.years": "{value} yıl",
        "js.badge_waiting": "Bekleniyor",
        "js.badge_stale": "Bilgiler değişti",
        "js.badge_approve": "Onaylanır",
        "js.badge_reject": "Reddedilir",
        "js.stamp_approve": "ONAY",
        "js.stamp_reject": "RET",
        "js.verdict_approve": "Model bu başvurunun onaylanacağını tahmin ediyor.",
        "js.verdict_reject": "Model bu başvurunun reddedileceğini tahmin ediyor.",
        "js.form_invalid": "Bazı alanlar eksik veya hatalı. İşaretli alanları düzeltin.",
        "js.generic_error": "Bir hata oluştu. Biraz sonra tekrar deneyin.",
        "js.network_error": "Sunucuya ulaşılamadı. Uygulamanın çalıştığından emin olup tekrar deneyin.",

        # ---------- API: doğrulama ----------
        "api.required": "Bu alanı doldurun.",
        "api.choice": "Listeden bir seçenek seçin.",
        "api.number": "Sayı girin.",
        "api.negative": "Negatif olamaz.",
        "api.too_large": "Değer çok büyük.",
        "api.cibil_range": "Kredi skoru 300 ile 900 arasında olmalı.",
        "api.income_min": "Yıllık gelir en az 1 olmalı.",
        "api.loan_min": "Kredi tutarı 0'dan büyük olmalı.",
        "api.term_min": "Vade en az 1 yıl olmalı.",
        "api.integer": "Tam sayı girin.",

        # ---------- API: gerekçeler ve uyarılar ----------
        "api.score_above_title": "Kredi skoru {score}, 550 eşiğinin üzerinde",
        "api.score_above_text": "Modelin en çok baktığı değişken bu. Eğitim verisinde skoru 550 ve üzeri olan başvuruların %99'u onaylanmış.",
        "api.score_below_title": "Kredi skoru {score}, 550 eşiğinin altında",
        "api.score_below_text": "Eğitim verisinde bu gruptaki başvuruların yalnızca %10 kadarı onaylanmış. Bu grupta karar büyük ölçüde yıllık taksit / gelir oranına göre veriliyor.",
        "api.payment_title": "Yıllık taksit gelirin %{pct} kadarı",
        "api.payment_text": "Kredi tutarı {term} yıla bölündüğünde yıllık ödeme, yıllık gelirin %{pct} kadarı ediyor. Model için ikinci en önemli değişken.",
        "api.loan_income_title": "Kredi, {ratio} yıllık gelire eşit",
        "api.assets_text": "Toplam varlıklar kredi tutarının {ratio} katı.",
        "api.no_assets_text": "Varlık bilgisi girilmedi (hepsi 0).",
        "api.uncertain_title": "Model bu başvuruda kararsız",
        "api.uncertain_text": "Onay olasılığı %35 ile %65 arasında. Bu başvuru, eğitim verisindeki sınır vakalara benziyor.",
        "api.range_warning": "{label} eğitim verisindeki aralığın ({low} – {high}) dışında. Model bu bölgeyi hiç görmediği için tahmin güvenilir olmayabilir.",

        # ---------- Alan ve değişken adları ----------
        "field.no_of_dependents": "Bakmakla yükümlü olunan kişi sayısı",
        "field.education": "Eğitim durumu",
        "field.self_employed": "Çalışma şekli",
        "field.income_annum": "Yıllık gelir",
        "field.loan_amount": "Kredi tutarı",
        "field.loan_term": "Vade",
        "field.cibil_score": "Kredi skoru",
        "field.residential_assets_value": "Konut varlıkları",
        "field.commercial_assets_value": "Ticari varlıklar",
        "field.luxury_assets_value": "Lüks varlıklar",
        "field.bank_asset_value": "Banka varlıkları",
        "field.total_assets": "Toplam varlık",
        "field.loan_to_income": "Kredi / yıllık gelir",
        "field.loan_to_assets": "Kredi / toplam varlık",
        "field.yearly_payment_to_income": "Yıllık taksit / yıllık gelir",
    },

    "en": {
        # ---------- Number format ----------
        "num.locale": "en-US",
        "num.thousands": ",",
        "num.decimal": ".",
        "num.percent": "{value}%",

        # ---------- General ----------
        "page.meta_description": "A machine learning app that predicts whether a loan application will be approved.",
        "page.og_image_alt": "KrediTahmin: Will your loan application be approved? 99.77% test accuracy.",
        "page.skip": "Skip to content",
        "page.nav_label": "Main menu",
        "page.nav_apply": "Application",
        "page.nav_model_long": "How does the model work?",
        "page.nav_model_short": "Model",
        "page.lang_label": "Language",
        "page.theme_label": "Theme",
        "page.theme_light": "Light theme",
        "page.theme_dark": "Dark theme",
        "page.footer_disclaimer": f"This app is an educational project and does not make real lending decisions. The model was trained on the <a href=\"{KAGGLE_URL}\">Loan Approval Prediction</a> dataset from Kaggle.",
        "page.footer_course": "Capstone project of the Data Science and Machine Learning 2026: 100-Day Bootcamp",
        "page.footer_source": "Source code on GitHub",

        # ---------- Application page ----------
        "page.index_title": "KrediTahmin: Will your loan be approved?",
        "page.hero_title": "Will your loan application be approved?",
        "page.hero_lede": "Enter the application details. A model trained on {count} loan applications shows its decision and the reasoning behind it in seconds.",
        "page.examples_label": "Example applications",
        "page.example_approved": "Try an approved example",
        "page.example_rejected": "Try a rejected example",
        "page.score_title": "Credit score",
        "page.score_help": "The most decisive input for the model. This is India's <strong>CIBIL</strong> score (300–900). It is not on the same scale as other credit scores such as Turkey's Findeks (1–1900), so don't enter those here directly.",
        "page.score_threshold": "550 threshold",
        "page.loan_title": "Loan request",
        "page.loan_amount": "Loan amount",
        "page.loan_term": "Loan term",
        "page.years_suffix": "yrs",
        "page.term_help": "Between 2 and 20 years in the training data.",
        "page.income_title": "Income and personal details",
        "page.income_short": "Income",
        "page.steps_label": "Application steps",
        "page.income": "Annual income",
        "page.dependents": "Dependents",
        "page.decrease": "Decrease",
        "page.increase": "Increase",
        "page.education": "Education",
        "page.graduate": "Graduate",
        "page.not_graduate": "Not a graduate",
        "page.employment": "Employment",
        "page.salaried": "Salaried",
        "page.self_employed": "Self-employed",
        "page.assets_title": "Assets",
        "page.assets_help": "Enter 0 for any asset type you don't have.",
        "page.asset_residential": "Residential",
        "page.asset_commercial": "Commercial",
        "page.asset_luxury": "Luxury (cars, jewellery, etc.)",
        "page.asset_bank": "Bank accounts",
        "page.slip_title": "Assessment",
        "page.ratio_payment": "Annual payment / income",
        "page.ratio_income": "Loan / annual income",
        "page.ratio_assets": "Total assets",
        "page.result_empty": "Fill in the form and press <strong>Evaluate application</strong> to see the model's decision here.",
        "page.probability": "Approval probability",

        # ---------- Model page ----------
        "page.about_lede": "KrediTahmin runs on a <strong>{model}</strong> model. While training it I compared 10 classification algorithms; the biggest gain came not from the choice of algorithm but from new variables I derived from the data.",
        "page.toc_label": "On this page",
        "page.test_title": "Test results",
        "page.test_text": "Out of {total} applications it never saw during training, the model predicted <strong>{correct}</strong> correctly.",
        "page.accuracy": "Accuracy",
        "page.baseline": "The rule \"approve if score ≥ 550\" alone",
        "page.matrix_label": "Confusion matrix",
        "page.matrix_caption": "Predictions vs. actual outcomes on the test set",
        "page.matrix_pred_reject": "Model: reject",
        "page.matrix_pred_approve": "Model: approve",
        "page.matrix_true_reject": "Actually rejected",
        "page.matrix_true_approve": "Actually approved",
        "page.fe_title": "Impact of feature engineering",
        "page.fe_text": "Banks look at ratios more than raw amounts. I derived four ratios from the raw columns: total assets, loan / income, loan / assets and, most importantly, <strong>annual payment / annual income</strong>. The chart shows each model's 5-fold cross-validation accuracy without and with these variables.",
        "page.legend_before": "Without new variables",
        "page.legend_after": "With new variables",
        "page.dumbbell_label": "{model}: before {before}, after {after}",
        "page.dumbbell_before": "Before: {value}",
        "page.dumbbell_after": "After: {value}",
        "page.fe_note": "Every tree-based model rose above 99%. Naive Bayes dropped instead: it assumes the variables are independent of each other, while the derived ratios are strongly correlated with the existing columns.",
        "page.importance_title": "What does the model look at?",
        "page.importance_text": "Feature importances of the final model. The credit score drives most of the decision and the annual payment / income ratio most of the rest; income, assets, education and employment have almost no effect.",
        "page.process_title": "How it was built",
        "page.step_1": "<strong>Data cleaning.</strong> Whitespace in column names and values was removed; 28 negative residential asset values were set to 0. There were no missing or duplicate records.",
        "page.step_2": "<strong>Exploratory analysis.</strong> A sharp threshold at a credit score of 550 was found. Education, employment and family size have no effect on the approval rate.",
        "page.step_3": "<strong>Feature engineering.</strong> Four ratios were derived. The best model's error dropped about 20-fold.",
        "page.step_4": "<strong>Model comparison.</strong> Logistic Regression, SVM, Naive Bayes, KNN, Decision Tree, Random Forest, AdaBoost, Gradient Boosting, XGBoost and LightGBM were tried.",
        "page.step_5": "<strong>Transformation.</strong> Yeo-Johnson was tried; it was not used because it didn't improve the linear model.",
        "page.step_6": "<strong>Hyperparameter tuning.</strong> The top 6 models were tuned with RandomizedSearchCV; {model}, with the highest cross-validation score, was chosen.",
        "page.step_7": "<strong>Deployment.</strong> The model was saved with <code>pickle</code> and connected to this Flask app.",
        "page.caveats_title": "Good to know",
        "page.caveat_1": "Amounts in the dataset are in Indian rupees (₹). The credit score follows India's CIBIL system (300–900), a different scale from other credit scores such as Turkey's Findeks (1–1900).",
        "page.caveat_2": "The rules in the data are too sharp to occur in real bank data; it is most likely synthetic. The 99.8% accuracy is specific to this dataset.",
        "page.caveat_3": "For applications with a low credit score, the model associates a high payment / income ratio with approval. This pattern comes from the data and does not reflect real banking logic.",
        "page.caveat_4": "The app shows a warning when a value falls outside the range of the training data; predictions in that region are not reliable.",

        # ---------- Error pages ----------
        "http.code": "Error {code}",
        "http.back": "Back to the application",
        "http.404_title": "Page not found",
        "http.404_text": "The page you're looking for doesn't exist or may have moved.",
        "http.413_title": "Request too large",
        "http.413_text": "The data sent exceeds the allowed size.",
        "http.500_title": "Something went wrong",
        "http.500_text": "An unexpected error occurred on the server. Please try again shortly.",
        "http.other_title": "An error occurred",
        "http.other_text": "Your request could not be processed.",

        # ---------- JavaScript ----------
        "js.submit": "Evaluate application",
        "js.submitting": "Evaluating…",
        "js.score_above": "Above threshold",
        "js.score_below": "Below threshold",
        "js.years": "{value} years",
        "js.badge_waiting": "Waiting",
        "js.badge_stale": "Inputs changed",
        "js.badge_approve": "Approved",
        "js.badge_reject": "Rejected",
        "js.stamp_approve": "YES",
        "js.stamp_reject": "NO",
        "js.verdict_approve": "The model predicts this application will be approved.",
        "js.verdict_reject": "The model predicts this application will be rejected.",
        "js.form_invalid": "Some fields are missing or invalid. Please fix the highlighted fields.",
        "js.generic_error": "Something went wrong. Please try again shortly.",
        "js.network_error": "Couldn't reach the server. Make sure the app is running and try again.",

        # ---------- API: validation ----------
        "api.required": "Please fill in this field.",
        "api.choice": "Please choose one of the options.",
        "api.number": "Please enter a number.",
        "api.negative": "Cannot be negative.",
        "api.too_large": "The value is too large.",
        "api.cibil_range": "Credit score must be between 300 and 900.",
        "api.income_min": "Annual income must be at least 1.",
        "api.loan_min": "Loan amount must be greater than 0.",
        "api.term_min": "Loan term must be at least 1 year.",
        "api.integer": "Please enter a whole number.",

        # ---------- API: reasons and warnings ----------
        "api.score_above_title": "Credit score {score} is above the 550 threshold",
        "api.score_above_text": "This is the variable the model relies on most. In the training data, 99% of applications with a score of 550 or higher were approved.",
        "api.score_below_title": "Credit score {score} is below the 550 threshold",
        "api.score_below_text": "In the training data, only about 10% of applications in this group were approved. Within this group the decision depends mostly on the annual payment / income ratio.",
        "api.payment_title": "Annual payment is {pct}% of income",
        "api.payment_text": "Over the {term}-year term, the annual payment comes to {pct}% of annual income. This is the second most important variable for the model.",
        "api.loan_income_title": "The loan equals {ratio} years of income",
        "api.assets_text": "Total assets are {ratio} times the loan amount.",
        "api.no_assets_text": "No assets were entered (all 0).",
        "api.uncertain_title": "The model is undecided on this application",
        "api.uncertain_text": "The approval probability is between 35% and 65%. This application resembles the borderline cases in the training data.",
        "api.range_warning": "{label} is outside the range of the training data ({low} – {high}). The model has never seen this region, so the prediction may be unreliable.",

        # ---------- Field and feature names ----------
        "field.no_of_dependents": "Number of dependents",
        "field.education": "Education",
        "field.self_employed": "Employment",
        "field.income_annum": "Annual income",
        "field.loan_amount": "Loan amount",
        "field.loan_term": "Loan term",
        "field.cibil_score": "Credit score",
        "field.residential_assets_value": "Residential assets",
        "field.commercial_assets_value": "Commercial assets",
        "field.luxury_assets_value": "Luxury assets",
        "field.bank_asset_value": "Bank assets",
        "field.total_assets": "Total assets",
        "field.loan_to_income": "Loan / annual income",
        "field.loan_to_assets": "Loan / total assets",
        "field.yearly_payment_to_income": "Annual payment / annual income",
    },
}


def text(lang: str, key: str, **values) -> str:
    template = TEXTS[lang][key]
    return template.format(**values) if values else template


def fmt_int(number: float, lang: str) -> str:
    """1234567 -> '1.234.567' (tr) / '1,234,567' (en)."""
    return f"{number:,.0f}".replace(",", TEXTS[lang]["num.thousands"])


def fmt_dec(number: float, lang: str, digits: int = 1) -> str:
    """3.14 -> '3,1' (tr) / '3.1' (en)."""
    return f"{number:.{digits}f}".replace(".", TEXTS[lang]["num.decimal"])


def fmt_pct(fraction: float, lang: str, digits: int = 1) -> str:
    """0.998 -> '%99,8' (tr) / '99.8%' (en)."""
    return text(lang, "num.percent", value=fmt_dec(fraction * 100, lang, digits))


def export(lang: str, *prefixes: str) -> dict:
    """Belirtilen önekle başlayan metinler (JavaScript'e aktarmak için)."""
    return {key: value for key, value in TEXTS[lang].items() if key.startswith(prefixes)}
