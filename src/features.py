"""Eğitim notebook'undaki feature engineering adımının aynısı.

Web uygulaması kullanıcıdan gelen veriyi modelin eğitimde gördüğü
formata çevirmek için bu fonksiyonları kullanır.
"""
import pandas as pd

ASSET_COLUMNS = [
    "residential_assets_value",
    "commercial_assets_value",
    "luxury_assets_value",
    "bank_asset_value",
]

RAW_COLUMNS = [
    "no_of_dependents",
    "education",
    "self_employed",
    "income_annum",
    "loan_amount",
    "loan_term",
    "cibil_score",
    *ASSET_COLUMNS,
]


def add_features(data: pd.DataFrame) -> pd.DataFrame:
    data = data.copy()
    data["total_assets"] = data[ASSET_COLUMNS].sum(axis=1)
    data["loan_to_income"] = data["loan_amount"] / data["income_annum"]
    data["loan_to_assets"] = data["loan_amount"] / data["total_assets"].replace(0, 1)
    data["yearly_payment_to_income"] = (data["loan_amount"] / data["loan_term"]) / data["income_annum"]
    return data


def prepare_input(application: dict, bundle: dict) -> pd.DataFrame:
    """Tek bir başvuruyu (dict) modelin beklediği DataFrame'e çevirir."""
    row = pd.DataFrame([{col: application[col] for col in RAW_COLUMNS}])
    row["education"] = row["education"].map(bundle["education_map"])
    row["self_employed"] = row["self_employed"].map(bundle["self_employed_map"])
    row = add_features(row)
    return row[bundle["feature_columns"]]
