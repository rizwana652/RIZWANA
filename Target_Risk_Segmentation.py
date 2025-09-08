# pages/Page2_Target_Risk_Segmentation.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

from utils.load_data import load_data
from utils.preprocess import preprocess

st.set_page_config(page_title="Default Risk Segmentation", layout="wide")

@st.cache_data
def get_clean_data():
    df_raw = load_data("application_train.csv")
    df_clean, _ = preprocess(df_raw, verbose=False)
    return df_clean

df = get_clean_data()

st.title("⚠️ Default Risk Segmentation (Page 2)")
st.markdown("Purpose: Understand how default varies across key segments.")

# Ensure TARGET exists
if "TARGET" not in df.columns:
    st.error("Column 'TARGET' not found in dataset after preprocessing.")
    st.stop()

# ---------- Helper to format top-n items of a series ----------
def top_n_str(series: pd.Series, n: int = 3):
    if series is None or series.empty:
        return "N/A"
    top = series.sort_values(ascending=False).head(n)
    return ", ".join([f"{str(idx)}: {val:.1f}%" for idx, val in top.items()])

# ---------- KPIs (10) ----------
total_defaults = int(df["TARGET"].sum())
default_rate = float(df["TARGET"].mean() * 100)

# Default rates by groups (if column exists)
def_rate_gender = df.groupby("CODE_GENDER")["TARGET"].mean() * 100 if "CODE_GENDER" in df.columns else pd.Series(dtype=float)
def_rate_edu = df.groupby("NAME_EDUCATION_TYPE")["TARGET"].mean() * 100 if "NAME_EDUCATION_TYPE" in df.columns else pd.Series(dtype=float)
def_rate_fam = df.groupby("NAME_FAMILY_STATUS")["TARGET"].mean() * 100 if "NAME_FAMILY_STATUS" in df.columns else pd.Series(dtype=float)
def_rate_housing = df.groupby("NAME_HOUSING_TYPE")["TARGET"].mean() * 100 if "NAME_HOUSING_TYPE" in df.columns else pd.Series(dtype=float)

# Averages among defaulters
df_def = df[df["TARGET"] == 1]
avg_income_def = float(df_def["AMT_INCOME_TOTAL"].mean()) if "AMT_INCOME_TOTAL" in df.columns and not df_def.empty else np.nan
avg_credit_def = float(df_def["AMT_CREDIT"].mean()) if "AMT_CREDIT" in df.columns and not df_def.empty else np.nan
avg_annuity_def = float(df_def["AMT_ANNUITY"].mean()) if "AMT_ANNUITY" in df.columns and not df_def.empty else np.nan
avg_emp_def = float(df_def["EMPLOYMENT_YEARS"].mean()) if "EMPLOYMENT_YEARS" in df.columns and not df_def.empty else np.nan

# Layout KPIs
k1, k2, k3, k4, k5 = st.columns(5)
k6, k7, k8, k9, k10 = st.columns(5)

k1.metric("Total Defaults", f"{total_defaults:,}")
k2.metric("Default Rate", f"{default_rate:.2f}%")
k3.metric("Default Rate by Gender (top)", top_n_str(def_rate_gender, 2))
k4.metric("Default Rate by Education (top)", top_n_str(def_rate_edu, 2))
k5.metric("Default Rate by Family (top)", top_n_str(def_rate_fam, 2))

k6.metric("Avg Income — Defaulters", f"{avg_income_def:,.0f}" if not np.isnan(avg_income_def) else "NA")
k7.metric("Avg Credit — Defaulters", f"{avg_credit_def:,.0f}" if not np.isnan(avg_credit_def) else "NA")
k8.metric("Avg Annuity — Defaulters", f"{avg_annuity_def:,.0f}" if not np.isnan(avg_annuity_def) else "NA")
k9.metric("Avg Employment (Years) — Defaulters", f"{avg_emp_def:.1f}" if not np.isnan(avg_emp_def) else "NA")
k10.metric("Default Rate by Housing (top)", top_n_str(def_rate_housing, 2))

st.markdown("---")

# ---------- GRAPHS (10) ----------

# 1. Bar — Counts: Default vs Repaid
fig1 = px.histogram(df, x="TARGET", text_auto=True,
                    labels={"TARGET": "Target (0=Repaid, 1=Default)"},
                    title="Counts: Default (1) vs Repaid (0)")
st.plotly_chart(fig1, use_container_width=True)

# Helper: if series exists convert to df for plotting default % charts
def series_to_df_for_rate(series: pd.Series, col_name: str, y_name: str = "DefaultRate"):
    if series is None or series.empty:
        return None
    d = series.reset_index()
    d.columns = [col_name, y_name]
    d[y_name] = d[y_name].astype(float)
    return d

# 2. Bar — Default % by Gender
df_gender_rate = series_to_df_for_rate(def_rate_gender, "CODE_GENDER")
if df_gender_rate is not None:
    fig2 = px.bar(df_gender_rate, x="CODE_GENDER", y="DefaultRate", text="DefaultRate",
                  labels={"DefaultRate": "Default Rate (%)"}, title="Default % by Gender")
    fig2.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.info("CODE_GENDER not present — skipping default % by gender chart.")

# 3. Bar — Default % by Education
df_edu_rate = series_to_df_for_rate(def_rate_edu, "NAME_EDUCATION_TYPE")
if df_edu_rate is not None:
    fig3 = px.bar(df_edu_rate, x="NAME_EDUCATION_TYPE", y="DefaultRate", text="DefaultRate",
                  labels={"DefaultRate": "Default Rate (%)"}, title="Default % by Education")
    fig3.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    st.plotly_chart(fig3, use_container_width=True)
else:
    st.info("NAME_EDUCATION_TYPE not present — skipping default % by education chart.")

# 4. Bar — Default % by Family Status
df_fam_rate = series_to_df_for_rate(def_rate_fam, "NAME_FAMILY_STATUS")
if df_fam_rate is not None:
    fig4 = px.bar(df_fam_rate, x="NAME_FAMILY_STATUS", y="DefaultRate", text="DefaultRate",
                  labels={"DefaultRate": "Default Rate (%)"}, title="Default % by Family Status")
    fig4.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    st.plotly_chart(fig4, use_container_width=True)
else:
    st.info("NAME_FAMILY_STATUS not present — skipping default % by family chart.")

# 5. Bar — Default % by Housing Type
df_housing_rate = series_to_df_for_rate(def_rate_housing, "NAME_HOUSING_TYPE")
if df_housing_rate is not None:
    fig5 = px.bar(df_housing_rate, x="NAME_HOUSING_TYPE", y="DefaultRate", text="DefaultRate",
                  labels={"DefaultRate": "Default Rate (%)"}, title="Default % by Housing Type")
    fig5.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    st.plotly_chart(fig5, use_container_width=True)
else:
    st.info("NAME_HOUSING_TYPE not present — skipping default % by housing chart.")

# 6. Boxplot — Income by Target
if "AMT_INCOME_TOTAL" in df.columns:
    fig6 = px.box(df, x="TARGET", y="AMT_INCOME_TOTAL",
                  labels={"TARGET": "Target", "AMT_INCOME_TOTAL": "Income"},
                  title="Boxplot — Income by Target", points="outliers")
    st.plotly_chart(fig6, use_container_width=True)
else:
    st.info("AMT_INCOME_TOTAL not present — skipping income by target boxplot.")

# 7. Boxplot — Credit by Target
if "AMT_CREDIT" in df.columns:
    fig7 = px.box(df, x="TARGET", y="AMT_CREDIT",
                  labels={"TARGET": "Target", "AMT_CREDIT": "Credit Amount"},
                  title="Boxplot — Credit by Target", points="outliers")
    st.plotly_chart(fig7, use_container_width=True)
else:
    st.info("AMT_CREDIT not present — skipping credit by target boxplot.")

# 8. Violin — Age vs Target
if "AGE_YEARS" in df.columns:
    fig8 = px.violin(df, x="TARGET", y="AGE_YEARS", box=True, points="outliers",
                     labels={"TARGET": "Target", "AGE_YEARS": "Age (years)"},
                     title="Violin — Age Distribution by Target")
    st.plotly_chart(fig8, use_container_width=True)
else:
    st.info("AGE_YEARS not present — skipping age vs target violin plot.")

# 9. Histogram (stacked) — EMPLOYMENT_YEARS by Target
if "EMPLOYMENT_YEARS" in df.columns:
    fig9 = px.histogram(df, x="EMPLOYMENT_YEARS", color="TARGET", barmode="stack",
                        nbins=40, labels={"TARGET": "Target"},
                        title="Histogram (stacked) — Employment Years by Target")
    st.plotly_chart(fig9, use_container_width=True)
else:
    st.info("EMPLOYMENT_YEARS not present — skipping employment years histogram.")

# 10. Stacked Bar — NAME_CONTRACT_TYPE vs Target
if "NAME_CONTRACT_TYPE" in df.columns:
    fig10 = px.histogram(df, x="NAME_CONTRACT_TYPE", color="TARGET", barmode="stack",
                         text_auto=True, title="Stacked Bar — Contract Type vs Target",
                         labels={"TARGET": "Target"})
    st.plotly_chart(fig10, use_container_width=True)
else:
    st.info("NAME_CONTRACT_TYPE not present — skipping contract type vs target chart.")

st.markdown("---")

# ---------- Narrative: highlight top/bottom segments ----------
st.subheader("Narrative Insights — top / bottom segments")

# Education top/bottom
edu_text = "Education data N/A"
if not def_rate_edu.empty:
    edu_sorted = def_rate_edu.sort_values(ascending=False)
    top_edu = edu_sorted.head(3)
    bot_edu = edu_sorted.tail(3)
    edu_text = f"Highest default by education: {', '.join([f'{i}: {v:.1f}%' for i, v in top_edu.items()])}. " \
               f"Lowest default by education: {', '.join([f'{i}: {v:.1f}%' for i, v in bot_edu.items()])}."

# Housing top/bottom
housing_text = "Housing data N/A"
if not def_rate_housing.empty:
    h_sorted = def_rate_housing.sort_values(ascending=False)
    top_h = h_sorted.head(2)
    bot_h = h_sorted.tail(2)
    housing_text = f"Highest default by housing: {', '.join([f'{i}: {v:.1f}%' for i, v in top_h.items()])}. " \
                   f"Lowest default by housing: {', '.join([f'{i}: {v:.1f}%' for i, v in bot_h.items()])}."

# Gender summary
gender_text = "Gender data N/A"
if not def_rate_gender.empty:
    gender_text = f"Default Rate by Gender — {', '.join([f'{i}: {v:.1f}%' for i, v in def_rate_gender.items()])}."

st.markdown(f"- **Education:** {edu_text}")
st.markdown(f"- **Housing:** {housing_text}")
st.markdown(f"- **Gender:** {gender_text}")

st.markdown("""
**Hypotheses:**  
- Segments with **high default** often show *lower income* and *higher loan-to-income ratios* — affordability stress.  
- **Short employment tenure** and **rented housing** can be proxies for unstable income and therefore higher risk.  
- Further analysis: cross-tabulate `INCOME_BRACKET` and `LOAN_TO_INCOME` with `TARGET` to validate hypotheses.
""")
