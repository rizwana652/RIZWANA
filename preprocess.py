"""
preprocessing.py

Simple, safe preprocessing for application_train.csv (Home Credit dataset).

Functions
- preprocess(df, drop_threshold=0.6, winsor_pct=0.01, verbose=True)
    -> Returns (df_clean, report)

Usage
>>> import pandas as pd
>>> from utils.preprocess import preprocess
>>> df = pd.read_csv("application_train.csv")
>>> df_clean, report = preprocess(df)
"""

import pandas as pd
import numpy as np


def preprocess(df: pd.DataFrame, drop_threshold: float = 0.6, winsor_pct: float = 0.01, verbose: bool = True):
    """Preprocess the Home Credit application_train DataFrame.

    Steps (kept intentionally simple):
    1. Drop columns with > `drop_threshold` fraction missing.
    2. Derive AGE_YEARS and EMPLOYMENT_YEARS (handle 365243 placeholder).
    3. Create ratios: DTI, LOAN_TO_INCOME, ANNUITY_TO_CREDIT (if source cols exist).
    4. Report missingness, then impute: numeric -> median, categorical -> mode.
    5. Merge rare categorical values (<1%) into 'Other'.
    6. Winsorize (clip) top/bottom `winsor_pct` for main numeric features used in charts.
    7. Create INCOME_BRACKET and AGE_RANGE and standardized filter columns.

    Returns
    -------
    df_clean : pd.DataFrame
        Processed DataFrame (copy).
    report : dict
        Dictionary describing drops/imputes/winsorization and key stats.
    """

    df = df.copy()
    report = {}

    # 0. initial snapshot
    report["initial_shape"] = df.shape

    # 1. missingness and drop high-missing columns
    missing_frac = df.isna().mean()
    report["missing_frac_by_col"] = missing_frac.to_dict()

    drop_cols = missing_frac[missing_frac > drop_threshold].index.tolist()
    if drop_cols:
        df = df.drop(columns=drop_cols)
    report["dropped_columns"] = drop_cols

    # 2. derive age and employment years
    if "DAYS_BIRTH" in df.columns:
        df["AGE_YEARS"] = (-df["DAYS_BIRTH"]) / 365.25

    if "DAYS_EMPLOYED" in df.columns:
        # 365243 is a known placeholder in Home Credit dataset -> treat as missing
        df["DAYS_EMPLOYED"] = df["DAYS_EMPLOYED"].replace(365243, np.nan)
        df["EMPLOYMENT_YEARS"] = (-df["DAYS_EMPLOYED"]) / 365.25

    # 3. ratios (safe divisions)
    def safe_div(a, b):
        return (a / b).replace([np.inf, -np.inf], np.nan)

    if {"AMT_ANNUITY", "AMT_INCOME_TOTAL"}.issubset(df.columns):
        df["DTI"] = safe_div(df["AMT_ANNUITY"], df["AMT_INCOME_TOTAL"])

    if {"AMT_CREDIT", "AMT_INCOME_TOTAL"}.issubset(df.columns):
        df["LOAN_TO_INCOME"] = safe_div(df["AMT_CREDIT"], df["AMT_INCOME_TOTAL"])

    if {"AMT_ANNUITY", "AMT_CREDIT"}.issubset(df.columns):
        df["ANNUITY_TO_CREDIT"] = safe_div(df["AMT_ANNUITY"], df["AMT_CREDIT"])

    # 4. imputation: numeric -> median, categorical -> mode
    imputed = {"numeric": {}, "categorical": {}}

    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    for col in numeric_cols:
        if df[col].isna().any():
            med = df[col].median()
            df[col] = df[col].fillna(med)
            imputed["numeric"][col] = float(med) if pd.notna(med) else None

    categorical_cols = df.select_dtypes(include=["object"]).columns.tolist()
    for col in categorical_cols:
        if df[col].isna().any():
            modes = df[col].mode()
            fill = modes.iloc[0] if not modes.empty else "Unknown"
            df[col] = df[col].fillna(fill)
            imputed["categorical"][col] = str(fill)

    report["imputed"] = imputed

    # 5. standardize categories: merge rare categories (<1% share) into 'Other'
    rare_replacements = {}
    for col in categorical_cols:
        freq = df[col].value_counts(normalize=True)
        rare = freq[freq < 0.01].index.tolist()
        if rare:
            df[col] = df[col].replace(rare, "Other")
            rare_replacements[col] = rare
    report["rare_replacements"] = rare_replacements

    # 6. winsorize (clip) top/bottom for commonly-visualized numeric columns
    winsor_targets = [
        c for c in ["AMT_INCOME_TOTAL", "AMT_CREDIT", "AMT_ANNUITY", "AMT_GOODS_PRICE"] if c in df.columns
    ]
    winsor_info = {}
    for col in winsor_targets:
        low = df[col].quantile(winsor_pct)
        high = df[col].quantile(1 - winsor_pct)
        df[col] = df[col].clip(lower=low, upper=high)
        winsor_info[col] = {"lower": float(low), "upper": float(high)}

    report["winsorized"] = winsor_info

    # 7. income brackets (Low: <=Q1, Mid: Q1-Q3, High: >Q3)
    if "AMT_INCOME_TOTAL" in df.columns:
        q1 = df["AMT_INCOME_TOTAL"].quantile(0.25)
        q3 = df["AMT_INCOME_TOTAL"].quantile(0.75)

        def income_bracket(val):
            if val <= q1:
                return "Low"
            if val > q3:
                return "High"
            return "Mid"

        df["INCOME_BRACKET"] = df["AMT_INCOME_TOTAL"].apply(income_bracket)
        report["income_quantiles"] = {"q1": float(q1), "q3": float(q3)}

    # 8. age ranges for consistent filtering
    if "AGE_YEARS" in df.columns:
        bins = [0, 25, 35, 45, 55, 1000]
        labels = ["<25", "25-34", "35-44", "45-54", "55+"]
        df["AGE_RANGE"] = pd.cut(df["AGE_YEARS"], bins=bins, labels=labels, include_lowest=True)

    # 9. standardized filter columns (rename/copy if present)
    if "CODE_GENDER" in df.columns:
        df["GENDER"] = df["CODE_GENDER"].astype(str).str.title().replace({"Xna": "Other"})
    if "NAME_EDUCATION_TYPE" in df.columns:
        df["EDUCATION"] = df["NAME_EDUCATION_TYPE"].astype(str)
    if "NAME_FAMILY_STATUS" in df.columns:
        df["FAMILY_STATUS"] = df["NAME_FAMILY_STATUS"].astype(str)
    if "NAME_HOUSING_TYPE" in df.columns:
        df["HOUSING_TYPE"] = df["NAME_HOUSING_TYPE"].astype(str)

    # final shape and summary
    report["final_shape"] = df.shape
    report["summary"] = {
        "n_rows_before": report["initial_shape"][0],
        "n_rows_after": df.shape[0],
        "n_cols_before": report["initial_shape"][1],
        "n_cols_after": df.shape[1],
    }

    if verbose:
        print("Preprocessing completed.")
        print(f"Dropped columns (> {drop_threshold*100:.0f}% missing): {drop_cols}")
        print(f"Winsorized: {list(winsor_info.keys())}")

    return df, report
