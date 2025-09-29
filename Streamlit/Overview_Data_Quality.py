import streamlit as st
import pandas as pd
import plotly.express as px

from utils.load_data import load_data
from utils.preprocess import preprocess

# ----------------------------
# Load + Preprocess
# ----------------------------
@st.cache_data
def get_clean_data():
    df = load_data("application_train.csv")
    df_clean, _ = preprocess(df, verbose=False)
    return df_clean

df = get_clean_data()

st.title("Overview And Data Quality (Page 1)")

st.markdown("""
This page introduces the Home Credit Application dataset, 
evaluates overall data quality, and provides a high-level risk snapshot.
""")

# ----------------------------
# KPIs
# ----------------------------
total_apps = len(df)
default_rate = df["TARGET"].mean() * 100
avg_income = df["AMT_INCOME_TOTAL"].mean()
avg_credit = df["AMT_CREDIT"].mean()
avg_age = df["AGE_YEARS"].mean()

col1, col2, col3 = st.columns(3)
col4, col5 = st.columns(2)

col1.metric("Total Applications", f"{total_apps:,}")
col2.metric("Default Rate", f"{default_rate:.2f}%")
col3.metric("Avg Income", f"{avg_income:,.0f}")
col4.metric("Avg Credit", f"{avg_credit:,.0f}")
col5.metric("Avg Age (Years)", f"{avg_age:.1f}")

st.markdown("---")

# ----------------------------
# Charts
# ----------------------------

# 1. Target distribution
fig1 = px.histogram(df, x="TARGET", text_auto=True,
                    labels={"TARGET": "Default Flag"},
                    title="Distribution of Target (Default vs Non-Default)")
st.plotly_chart(fig1, use_container_width=True)

# 2. Gender distribution
gender_counts = df["CODE_GENDER"].value_counts().reset_index()
gender_counts.columns = ["CODE_GENDER", "Count"]
fig2 = px.bar(gender_counts, x="CODE_GENDER", y="Count",
              text="Count", title="Gender Distribution")
st.plotly_chart(fig2, use_container_width=True)

# 3. Family status distribution
fam_counts = df["NAME_FAMILY_STATUS"].value_counts().reset_index()
fam_counts.columns = ["NAME_FAMILY_STATUS", "Count"]
fig3 = px.bar(fam_counts, x="NAME_FAMILY_STATUS", y="Count",
              text="Count", title="Family Status Distribution")
st.plotly_chart(fig3, use_container_width=True)

# 4. Age distribution
fig4 = px.histogram(df, x="AGE_YEARS", nbins=30,
                    title="Age Distribution (Years)")
st.plotly_chart(fig4, use_container_width=True)

# 5. Income brackets
if "INCOME_BRACKET" in df.columns:
    fig5 = px.histogram(df, x="INCOME_BRACKET",
                        title="Income Bracket Distribution")
    st.plotly_chart(fig5, use_container_width=True)

# 6. Credit amount distribution
fig6 = px.histogram(df, x="AMT_CREDIT", nbins=40,
                    title="Credit Amount Distribution")
st.plotly_chart(fig6, use_container_width=True)

# 7. Employment years
fig7 = px.histogram(df, x="EMPLOYMENT_YEARS", nbins=30,
                    title="Employment Tenure (Years)")
st.plotly_chart(fig7, use_container_width=True)

# 8. Debt-to-Income (DTI) ratio
fig8 = px.histogram(df, x="DTI", nbins=40,
                    title="Debt-to-Income (DTI) Distribution")
st.plotly_chart(fig8, use_container_width=True)

# 9. Loan-to-Income ratio
fig9 = px.histogram(df, x="LOAN_TO_INCOME", nbins=40,
                    title="Loan-to-Income Ratio Distribution")
st.plotly_chart(fig9, use_container_width=True)

# 10. Annuity-to-Credit ratio
fig10 = px.histogram(df, x="ANNUITY_TO_CREDIT", nbins=40,
                     title="Annuity-to-Credit Ratio Distribution")
st.plotly_chart(fig10, use_container_width=True)

st.markdown("---")
st.markdown("✅ Page 1 built using **cleaned dataset** with KPIs + 10 charts.")
