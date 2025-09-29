# pages/Page5_Correlations_Drivers.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

from utils.load_data import load_data
from utils.preprocess import preprocess

st.set_page_config(page_title="Correlations & Drivers (Page 5)", layout="wide")

@st.cache_data
def get_clean_data():
    df_raw = load_data("application_train.csv")
    df_clean, _ = preprocess(df_raw, verbose=False)
    return df_clean

df = get_clean_data()

st.title("🔎 Correlations, Drivers & Interactive Slice-and-Dice (Page 5)")
st.markdown("Purpose: What drives default? Correlation views + interactive filters to build candidate policy rules.")

# -------------------------
# Sidebar filters (interactive slice-and-dice)
# -------------------------
st.sidebar.header("Filters — slice the data")
# Possible filter columns created by preprocessing
filter_gender = st.sidebar.multiselect(
    "Gender", options=sorted(df["CODE_GENDER"].dropna().unique()) if "CODE_GENDER" in df.columns else [],
    default=sorted(df["CODE_GENDER"].dropna().unique()) if "CODE_GENDER" in df.columns else []
)
filter_education = st.sidebar.multiselect(
    "Education", options=sorted(df["NAME_EDUCATION_TYPE"].dropna().unique()) if "NAME_EDUCATION_TYPE" in df.columns else [],
    default=sorted(df["NAME_EDUCATION_TYPE"].dropna().unique()) if "NAME_EDUCATION_TYPE" in df.columns else []
)
filter_family = st.sidebar.multiselect(
    "Family Status", options=sorted(df["NAME_FAMILY_STATUS"].dropna().unique()) if "NAME_FAMILY_STATUS" in df.columns else [],
    default=sorted(df["NAME_FAMILY_STATUS"].dropna().unique()) if "NAME_FAMILY_STATUS" in df.columns else []
)
filter_housing = st.sidebar.multiselect(
    "Housing", options=sorted(df["NAME_HOUSING_TYPE"].dropna().unique()) if "NAME_HOUSING_TYPE" in df.columns else [],
    default=sorted(df["NAME_HOUSING_TYPE"].dropna().unique()) if "NAME_HOUSING_TYPE" in df.columns else []
)
# Age range slider (use AGE_YEARS)
if "AGE_YEARS" in df.columns:
    min_age = int(max(0, np.floor(df["AGE_YEARS"].min())))
    max_age = int(np.ceil(df["AGE_YEARS"].max()))
    age_range = st.sidebar.slider("Age range", min_value=min_age, max_value=max_age,
                                  value=(min_age, max_age))
else:
    age_range = None

# Income bracket filter
if "INCOME_BRACKET" in df.columns:
    income_brackets = sorted(df["INCOME_BRACKET"].dropna().unique(), key=str)
    filter_income_bracket = st.sidebar.multiselect("Income Bracket", options=income_brackets, default=income_brackets)
else:
    filter_income_bracket = []

# Apply filters
df_filtered = df.copy()
if filter_gender:
    if "CODE_GENDER" in df_filtered.columns:
        df_filtered = df_filtered[df_filtered["CODE_GENDER"].isin(filter_gender)]
if filter_education:
    if "NAME_EDUCATION_TYPE" in df_filtered.columns:
        df_filtered = df_filtered[df_filtered["NAME_EDUCATION_TYPE"].isin(filter_education)]
if filter_family:
    if "NAME_FAMILY_STATUS" in df_filtered.columns:
        df_filtered = df_filtered[df_filtered["NAME_FAMILY_STATUS"].isin(filter_family)]
if filter_housing:
    if "NAME_HOUSING_TYPE" in df_filtered.columns:
        df_filtered = df_filtered[df_filtered["NAME_HOUSING_TYPE"].isin(filter_housing)]
if age_range and "AGE_YEARS" in df_filtered.columns:
    df_filtered = df_filtered[(df_filtered["AGE_YEARS"] >= age_range[0]) & (df_filtered["AGE_YEARS"] <= age_range[1])]
if filter_income_bracket and "INCOME_BRACKET" in df_filtered.columns:
    df_filtered = df_filtered[df_filtered["INCOME_BRACKET"].isin(filter_income_bracket)]

st.sidebar.markdown(f"**Filtered rows:** {len(df_filtered):,} (of {len(df):,})")

# -------------------------
# Numeric features selection for correlation
# -------------------------
numeric_cols = df_filtered.select_dtypes(include=[np.number]).columns.tolist()
# remove identifier-like columns if present
for c in ["SK_ID_CURR", "SK_ID_PREV"]:
    if c in numeric_cols:
        numeric_cols.remove(c)

# Ensure TARGET is present
if "TARGET" not in numeric_cols and "TARGET" in df_filtered.columns:
    numeric_cols.append("TARGET")

if len(numeric_cols) < 2:
    st.error("Not enough numeric columns to compute correlations after filtering.")
    st.stop()

# Correlation matrix (filtered)
corr = df_filtered[numeric_cols].corr(numeric_only=True)

# Correlation of each feature with TARGET (exclude TARGET itself)
if "TARGET" in corr.columns:
    corr_with_target = corr["TARGET"].drop("TARGET", errors='ignore')
else:
    st.error("'TARGET' column missing in dataset (required).")
    st.stop()

# Top + / - correlation with TARGET
top_pos = corr_with_target.sort_values(ascending=False).head(5)
top_neg = corr_with_target.sort_values().head(5)

# Most correlated with Income and Credit (by absolute corr)
income_col = "AMT_INCOME_TOTAL"
credit_col = "AMT_CREDIT"

most_corr_with_income = None
most_corr_with_credit = None
corr_income_credit = np.nan

if income_col in corr.columns:
    temp = corr[income_col].drop(income_col, errors='ignore').abs()
    if not temp.empty:
        most_corr_with_income = temp.idxmax()
if credit_col in corr.columns:
    temp2 = corr[credit_col].drop(credit_col, errors='ignore').abs()
    if not temp2.empty:
        most_corr_with_credit = temp2.idxmax()
if income_col in corr.columns and credit_col in corr.columns:
    corr_income_credit = corr.loc[income_col, credit_col]

# Other requested correlations
corr_age_target = corr.loc["AGE_YEARS", "TARGET"] if ("AGE_YEARS" in corr.index and "TARGET" in corr.columns) else np.nan
corr_emp_target = corr.loc["EMPLOYMENT_YEARS", "TARGET"] if ("EMPLOYMENT_YEARS" in corr.index and "TARGET" in corr.columns) else np.nan
corr_family_target = corr.loc["CNT_FAM_MEMBERS", "TARGET"] if ("CNT_FAM_MEMBERS" in corr.index and "TARGET" in corr.columns) else np.nan

# Variance explained proxy via squared correlations
all_r2 = (corr_with_target ** 2).dropna()
top5_r2 = all_r2.abs().sort_values(ascending=False).head(5).sum()
total_r2 = all_r2.sum() if not all_r2.empty else np.nan
variance_explained_proxy = (top5_r2 / total_r2 * 100) if (not np.isnan(total_r2) and total_r2 > 0) else np.nan

# Number of features with |corr| > 0.5
n_high_corr = (corr_with_target.abs() > 0.5).sum()

# -------------------------
# KPIs (10) display
# -------------------------
k1, k2, k3, k4, k5 = st.columns(5)
k6, k7, k8, k9, k10 = st.columns(5)

k1.metric("Top 5 +Corr with TARGET", ", ".join([f"{idx} ({val:.2f})" for idx, val in top_pos.items()]) if not top_pos.empty else "N/A")
k2.metric("Top 5 −Corr with TARGET", ", ".join([f"{idx} ({val:.2f})" for idx, val in top_neg.items()]) if not top_neg.empty else "N/A")
k3.metric("Most correlated with Income", f"{most_corr_with_income}" if most_corr_with_income is not None else "N/A")
k4.metric("Most correlated with Credit", f"{most_corr_with_credit}" if most_corr_with_credit is not None else "N/A")
k5.metric("Corr(Income, Credit)", f"{corr_income_credit:.3f}" if not np.isnan(corr_income_credit) else "N/A")

k6.metric("Corr(Age, TARGET)", f"{corr_age_target:.3f}" if not np.isnan(corr_age_target) else "N/A")
k7.metric("Corr(Employment Years, TARGET)", f"{corr_emp_target:.3f}" if not np.isnan(corr_emp_target) else "N/A")
k8.metric("Corr(Family Size, TARGET)", f"{corr_family_target:.3f}" if not np.isnan(corr_family_target) else "N/A")
k9.metric("Variance explained (proxy) — Top5", f"{variance_explained_proxy:.1f}%" if not np.isnan(variance_explained_proxy) else "N/A")
k10.metric("# Features with |corr| > 0.5", f"{int(n_high_corr)}")

st.markdown("---")

# -------------------------
# Graphs (10)
# -------------------------

# 1. Heatmap — Correlation (selected numerics)
st.subheader("Heatmap — Correlation (selected numerics)")
default_corr_cols = sorted(numeric_cols, key=lambda c: -abs(corr_with_target.get(c, 0)))[:20]
sel_corr_cols = st.multiselect("Select numeric columns for heatmap", options=sorted(numeric_cols), default=default_corr_cols)
if sel_corr_cols:
    corr_sel = df_filtered[sel_corr_cols].corr(numeric_only=True)
    fig_heat = px.imshow(corr_sel, text_auto=True, aspect="auto", title="Correlation heatmap (selected columns)")
    st.plotly_chart(fig_heat, use_container_width=True)
else:
    st.info("No numeric columns selected for heatmap.")

# 2. Bar — |Correlation| of features vs TARGET (top N)
st.subheader("Bar — |Correlation| of features vs TARGET")
top_n = st.slider("Top N features by |corr| to show", min_value=5, max_value=min(50, len(corr_with_target)), value=10)
corr_abs_df = corr_with_target.abs().sort_values(ascending=False).head(top_n).reset_index()
corr_abs_df.columns = ["feature", "abs_corr"]
fig_bar_corr = px.bar(corr_abs_df, x="feature", y="abs_corr", text="abs_corr", title=f"Top {top_n} |Correlation| vs TARGET")
fig_bar_corr.update_traces(texttemplate='%{text:.2f}', textposition='outside')
st.plotly_chart(fig_bar_corr, use_container_width=True)

# 3. Scatter — Age vs Credit (hue=TARGET)
st.subheader("Scatter — Age vs Credit (hue=TARGET)")
if {"AGE_YEARS", "AMT_CREDIT"}.issubset(df_filtered.columns):
    sample_df = df_filtered.sample(n=min(len(df_filtered), 5000), random_state=10)
    fig_sc1 = px.scatter(sample_df, x="AGE_YEARS", y="AMT_CREDIT", color="TARGET",
                         opacity=0.6, title="Age vs Credit (sampled)")
    st.plotly_chart(fig_sc1, use_container_width=True)
else:
    st.info("AGE_YEARS or AMT_CREDIT not available for Age vs Credit scatter.")

# 4. Scatter — Age vs Income (hue=TARGET)
st.subheader("Scatter — Age vs Income (hue=TARGET)")
if {"AGE_YEARS", "AMT_INCOME_TOTAL"}.issubset(df_filtered.columns):
    sample_df = df_filtered.sample(n=min(len(df_filtered), 5000), random_state=11)
    fig_sc2 = px.scatter(sample_df, x="AGE_YEARS", y="AMT_INCOME_TOTAL", color="TARGET",
                         opacity=0.6, title="Age vs Income (sampled)")
    st.plotly_chart(fig_sc2, use_container_width=True)
else:
    st.info("AGE_YEARS or AMT_INCOME_TOTAL not available for Age vs Income scatter.")

# 5. Scatter — Employment Years vs TARGET (jitter)
st.subheader("Scatter — Employment Years vs TARGET (jitter)")
if "EMPLOYMENT_YEARS" in df_filtered.columns and "TARGET" in df_filtered.columns:
    samp = df_filtered.sample(n=min(len(df_filtered), 5000), random_state=12).copy()
    # jitter y-value slightly so points separate for target 0/1
    samp["_TARGET_JITTER"] = samp["TARGET"] + np.random.uniform(-0.03, 0.03, len(samp))
    fig_sc3 = px.scatter(samp, x="EMPLOYMENT_YEARS", y="_TARGET_JITTER", color="TARGET",
                         labels={"_TARGET_JITTER": "TARGET (jittered)"}, title="Employment Years vs TARGET (jittered)")
    st.plotly_chart(fig_sc3, use_container_width=True)
else:
    st.info("EMPLOYMENT_YEARS or TARGET not present — skipping Employment vs TARGET scatter.")

# 6. Boxplot — Credit by Education
st.subheader("Boxplot — Credit by Education")
if "NAME_EDUCATION_TYPE" in df_filtered.columns and "AMT_CREDIT" in df_filtered.columns:
    fig_box_edu = px.box(df_filtered, x="NAME_EDUCATION_TYPE", y="AMT_CREDIT", points="outliers",
                         title="Credit by Education")
    st.plotly_chart(fig_box_edu, use_container_width=True)
else:
    st.info("NAME_EDUCATION_TYPE or AMT_CREDIT missing — skipping boxplot.")

# 7. Boxplot — Income by Family Status
st.subheader("Boxplot — Income by Family Status")
if "NAME_FAMILY_STATUS" in df_filtered.columns and "AMT_INCOME_TOTAL" in df_filtered.columns:
    fig_box_fam = px.box(df_filtered, x="NAME_FAMILY_STATUS", y="AMT_INCOME_TOTAL", points="outliers",
                         title="Income by Family Status")
    st.plotly_chart(fig_box_fam, use_container_width=True)
else:
    st.info("NAME_FAMILY_STATUS or AMT_INCOME_TOTAL missing — skipping boxplot.")

# 8. Pair Plot — Income, Credit, Annuity, TARGET
st.subheader("Pair Plot — Income, Credit, Annuity, TARGET (sampled)")
pair_cols = [c for c in ["AMT_INCOME_TOTAL", "AMT_CREDIT", "AMT_ANNUITY", "TARGET"] if c in df_filtered.columns]
if len(pair_cols) >= 2:
    sample_pair = df_filtered[pair_cols].sample(n=min(len(df_filtered), 2000), random_state=13)
    fig_pair = px.scatter_matrix(sample_pair, dimensions=[c for c in pair_cols if c != "TARGET"],
                                color="TARGET" if "TARGET" in pair_cols else None,
                                title="Pair plot (Income, Credit, Annuity, TARGET)")
    st.plotly_chart(fig_pair, use_container_width=True)
else:
    st.info("Not enough columns for pair plot (need Income/Credit/Annuity/TARGET).")

# 9. Filtered Bar — Default Rate by Gender (responsive to sidebar filters)
st.subheader("Filtered Bar — Default Rate by Gender (responsive)")
if "CODE_GENDER" in df_filtered.columns and "TARGET" in df_filtered.columns:
    gr = df_filtered.groupby("CODE_GENDER")["TARGET"].mean().reset_index()
    gr["DefaultRatePct"] = gr["TARGET"] * 100
    fig_fg = px.bar(gr, x="CODE_GENDER", y="DefaultRatePct", text="DefaultRatePct", title="Default Rate by Gender (filtered)")
    fig_fg.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    st.plotly_chart(fig_fg, use_container_width=True)
else:
    st.info("CODE_GENDER or TARGET not available — skipping filtered Default Rate by Gender.")

# 10. Filtered Bar — Default Rate by Education (responsive)
st.subheader("Filtered Bar — Default Rate by Education (responsive)")
if "NAME_EDUCATION_TYPE" in df_filtered.columns and "TARGET" in df_filtered.columns:
    gr2 = df_filtered.groupby("NAME_EDUCATION_TYPE")["TARGET"].mean().reset_index()
    gr2["DefaultRatePct"] = gr2["TARGET"] * 100
    fig_fe = px.bar(gr2, x="NAME_EDUCATION_TYPE", y="DefaultRatePct", text="DefaultRatePct", title="Default Rate by Education (filtered)")
    fig_fe.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    st.plotly_chart(fig_fe, use_container_width=True)
else:
    st.info("NAME_EDUCATION_TYPE or TARGET not available — skipping filtered Default Rate by Education.")

st.markdown("---")

# -------------------------
# Narrative & suggested policy rules
# -------------------------
st.subheader("Narrative: Translating correlations into candidate policy rules")

st.markdown(
    "- Use the top positively correlated features to **prioritize risk reviews** (e.g., if `LOAN_TO_INCOME` or `DTI` is among top correlated features, consider LTI caps or DTI thresholds).\n"
    "- Use negatively correlated features (protective factors) to design **fast-track approvals** (e.g., long `EMPLOYMENT_YEARS`, high income).\n"
    "- Proxy for \"variance explained\" here is the sum of squared correlations (r²) for top-5 features — treat this as a quick indicator of how concentrated risk is in a few features.\n"
    "- Candidate operational rules to evaluate (example):\n"
    "  - If `LOAN_TO_INCOME` > 6 and `DTI` > 0.35 then require additional affordability checks.\n"
    "  - Minimum income floors for certain contract types or age groups based on the Default Rate by Income Bracket chart.\n"
)
st.markdown("**Next steps:** cross-validate candidate rules on holdout data and measure expected reduction in default (lift) vs acceptance change.")
