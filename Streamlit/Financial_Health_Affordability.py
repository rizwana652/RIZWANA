# pages/Page4_Financial_Health.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

from utils.load_data import load_data
from utils.preprocess import preprocess

st.set_page_config(page_title="Financial Health & Affordability (Page 4)", layout="wide")

@st.cache_data
def get_clean_data():
    df_raw = load_data("application_train.csv")
    df_clean, _ = preprocess(df_raw, verbose=False)
    return df_clean

df = get_clean_data()

st.title("💳 Financial Health & Affordability (Page 4)")
st.markdown("Purpose: Ability to repay, affordability indicators, and stress.")

# --- Helper functions ---
def safe_mean(col):
    return float(col.mean()) if col is not None and len(col) > 0 else np.nan

def safe_median(col):
    return float(col.median()) if col is not None and len(col) > 0 else np.nan

def pct(condition_series, total):
    return (condition_series.sum() / total * 100) if total > 0 else np.nan

n = len(df)

# --- KPIs (10) ---
# Required columns may already be created in preprocessing: DTI, LOAN_TO_INCOME
income_col = "AMT_INCOME_TOTAL"
credit_col = "AMT_CREDIT"
annuity_col = "AMT_ANNUITY"
goods_col = "AMT_GOODS_PRICE"
dti_col = "DTI"
lti_col = "LOAN_TO_INCOME"

avg_income = safe_mean(df[income_col]) if income_col in df.columns else np.nan
median_income = safe_median(df[income_col]) if income_col in df.columns else np.nan
avg_credit = safe_mean(df[credit_col]) if credit_col in df.columns else np.nan
avg_annuity = safe_mean(df[annuity_col]) if annuity_col in df.columns else np.nan
avg_goods = safe_mean(df[goods_col]) if goods_col in df.columns else np.nan

# DTI / LTI: if not present, compute safely
if dti_col not in df.columns and {annuity_col, income_col}.issubset(df.columns):
    df[dti_col] = df[annuity_col] / df[income_col]
if lti_col not in df.columns and {credit_col, income_col}.issubset(df.columns):
    df[lti_col] = df[credit_col] / df[income_col]

avg_dti = safe_mean(df[dti_col]) if dti_col in df.columns else np.nan
avg_lti = safe_mean(df[lti_col]) if lti_col in df.columns else np.nan

# Income/Credit gaps (Non-def − Def)
income_gap = np.nan
credit_gap = np.nan
if "TARGET" in df.columns:
    df_def = df[df["TARGET"] == 1]
    df_nondef = df[df["TARGET"] == 0]
    if income_col in df.columns:
        income_gap = safe_mean(df_nondef[income_col]) - safe_mean(df_def[income_col]) if (not df_def.empty and not df_nondef.empty) else np.nan
    if credit_col in df.columns:
        credit_gap = safe_mean(df_nondef[credit_col]) - safe_mean(df_def[credit_col]) if (not df_def.empty and not df_nondef.empty) else np.nan

# % High Credit (> 1,000,000)
pct_high_credit = np.nan
if credit_col in df.columns:
    pct_high_credit = pct(df[credit_col] > 1_000_000, n)

# Display KPIs
c1, c2, c3, c4, c5 = st.columns(5)
c6, c7, c8, c9, c10 = st.columns(5)

c1.metric("Avg Annual Income", f"{avg_income:,.0f}" if not np.isnan(avg_income) else "NA")
c2.metric("Median Annual Income", f"{median_income:,.0f}" if not np.isnan(median_income) else "NA")
c3.metric("Avg Credit Amount", f"{avg_credit:,.0f}" if not np.isnan(avg_credit) else "NA")
c4.metric("Avg Annuity", f"{avg_annuity:,.0f}" if not np.isnan(avg_annuity) else "NA")
c5.metric("Avg Goods Price", f"{avg_goods:,.0f}" if not np.isnan(avg_goods) else "NA")

c6.metric("Avg DTI", f"{avg_dti:.3f}" if not np.isnan(avg_dti) else "NA")
c7.metric("Avg LTI", f"{avg_lti:.3f}" if not np.isnan(avg_lti) else "NA")
c8.metric("Income Gap (Non-def − Def)", f"{income_gap:,.0f}" if not np.isnan(income_gap) else "NA")
c9.metric("Credit Gap (Non-def − Def)", f"{credit_gap:,.0f}" if not np.isnan(credit_gap) else "NA")
c10.metric("% High Credit (>1M)", f"{pct_high_credit:.2f}%" if not np.isnan(pct_high_credit) else "NA")

st.markdown("---")

# --- Graphs (10) ---

# 1. Histogram — Income distribution
if income_col in df.columns:
    fig1 = px.histogram(df, x=income_col, nbins=60, title="Income Distribution", labels={income_col: "Annual Income"})
    st.plotly_chart(fig1, use_container_width=True)
else:
    st.info("AMT_INCOME_TOTAL not present — skipping income histogram.")

# 2. Histogram — Credit distribution
if credit_col in df.columns:
    fig2 = px.histogram(df, x=credit_col, nbins=60, title="Credit Amount Distribution", labels={credit_col: "Credit Amount"})
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.info("AMT_CREDIT not present — skipping credit histogram.")

# 3. Histogram — Annuity distribution
if annuity_col in df.columns:
    fig3 = px.histogram(df, x=annuity_col, nbins=60, title="Annuity Distribution", labels={annuity_col: "Annuity"})
    st.plotly_chart(fig3, use_container_width=True)
else:
    st.info("AMT_ANNUITY not present — skipping annuity histogram.")

# 4. Scatter — Income vs Credit (alpha blending; sample for performance)
if {income_col, credit_col}.issubset(df.columns):
    sample_n = min(len(df), 5000)
    sample_df = df.sample(sample_n, random_state=1)
    fig4 = px.scatter(sample_df, x=income_col, y=credit_col, color="TARGET" if "TARGET" in df.columns else None,
                      opacity=0.6, title="Income vs Credit (sample)", labels={income_col: "Income", credit_col: "Credit"})
    st.plotly_chart(fig4, use_container_width=True)
else:
    st.info("Income or Credit column missing — skipping Income vs Credit scatter.")

# 5. Scatter — Income vs Annuity
if {income_col, annuity_col}.issubset(df.columns):
    sample_n = min(len(df), 5000)
    sample_df = df.sample(sample_n, random_state=2)
    fig5 = px.scatter(sample_df, x=income_col, y=annuity_col, color="TARGET" if "TARGET" in df.columns else None,
                      opacity=0.6, title="Income vs Annuity (sample)", labels={income_col: "Income", annuity_col: "Annuity"})
    st.plotly_chart(fig5, use_container_width=True)
else:
    st.info("Income or Annuity column missing — skipping Income vs Annuity scatter.")

# 6. Boxplot — Credit by Target
if {"TARGET", credit_col}.issubset(df.columns):
    fig6 = px.box(df, x="TARGET", y=credit_col, points="outliers", title="Credit by Target", labels={"TARGET": "Target", credit_col: "Credit"})
    st.plotly_chart(fig6, use_container_width=True)
else:
    st.info("TARGET or AMT_CREDIT missing — skipping Credit by Target boxplot.")

# 7. Boxplot — Income by Target
if {"TARGET", income_col}.issubset(df.columns):
    fig7 = px.box(df, x="TARGET", y=income_col, points="outliers", title="Income by Target", labels={"TARGET": "Target", income_col: "Income"})
    st.plotly_chart(fig7, use_container_width=True)
else:
    st.info("TARGET or AMT_INCOME_TOTAL missing — skipping Income by Target boxplot.")

# 8. KDE / Density — Joint Income–Credit (density heatmap)
if {income_col, credit_col}.issubset(df.columns):
    fig8 = px.density_heatmap(df.sample(n=min(len(df), 20000), random_state=3), x=income_col, y=credit_col,
                              nbinsx=80, nbinsy=80, title="Joint Density: Income vs Credit")
    st.plotly_chart(fig8, use_container_width=True)
else:
    st.info("Income or Credit missing — skipping joint density plot.")

# 9. Bar — Income Brackets vs Default Rate
if "INCOME_BRACKET" in df.columns and "TARGET" in df.columns:
    rate_df = df.groupby("INCOME_BRACKET")["TARGET"].mean().reset_index()
    rate_df["DefaultRatePct"] = rate_df["TARGET"] * 100
    fig9 = px.bar(rate_df, x="INCOME_BRACKET", y="DefaultRatePct", text="DefaultRatePct",
                  title="Income Bracket vs Default Rate", labels={"DefaultRatePct": "Default Rate (%)"})
    fig9.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    st.plotly_chart(fig9, use_container_width=True)
else:
    st.info("INCOME_BRACKET or TARGET missing — skipping Income Bracket vs Default Rate.")

# 10. Heatmap — Financial variable correlations
financial_cols = [c for c in [income_col, credit_col, annuity_col, dti_col, lti_col, goods_col, "TARGET"] if c in df.columns]
if len(financial_cols) >= 2:
    corr = df[financial_cols].corr(numeric_only=True)
    fig10 = px.imshow(corr, text_auto=True, aspect="auto", title="Correlation: Income, Credit, Annuity, DTI, LTI, TARGET")
    st.plotly_chart(fig10, use_container_width=True)
else:
    st.info("Not enough financial columns for correlation heatmap.")

st.markdown("---")

# --- Narrative: Affordability thresholds & validation checks ---
st.subheader("Narrative & Quick Affordability Checks")

# Example thresholds to evaluate
thresholds = {
    "LTI > 6": ("LOAN_TO_INCOME", 6),
    "DTI > 0.35": ("DTI", 0.35)
}

for label, (col, thresh) in thresholds.items():
    if col in df.columns and "TARGET" in df.columns:
        subset = df[df[col].notna()]
        high = subset[subset[col] > thresh]
        if len(high) > 0:
            rate = high["TARGET"].mean() * 100
            st.markdown(f"- **{label}**: Observations = {len(high):,}, Default Rate = **{rate:.2f}%**")
        else:
            st.markdown(f"- **{label}**: No observations above threshold.")
    else:
        st.markdown(f"- **{label}**: Column '{col}' or 'TARGET' not available to evaluate.")

st.markdown("""
**Interpretation guidance:**  
- Look for rising default rates in higher-LTI / higher-DTI groups — these indicate affordability stress.  
- Use the Income Bracket vs Default Rate chart to find practical thresholds (e.g., LTI or DTI levels where default spikes).  
- Consider combining employer/occupation stability and INCOME_BRACKET to refine affordability rules.
""")
