# pages/Page3_Demographics_Household.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

from utils.load_data import load_data
from utils.preprocess import preprocess

st.set_page_config(page_title="Demographics & Household (Page 3)", layout="wide")

@st.cache_data
def get_clean_data():
    df_raw = load_data("application_train.csv")
    df_clean, _ = preprocess(df_raw, verbose=False)
    return df_clean

df = get_clean_data()

st.title("👪 Demographics & Household Profile (Page 3)")
st.markdown("Purpose: Who are the applicants? Household structure and human factors.")

# --------------------------
# Helper funcs
# --------------------------
def safe_mean(series):
    return float(series.mean()) if (series is not None and len(series) > 0 and series.notna().any()) else np.nan

def percent(cond_series, total):
    return (cond_series.sum() / total * 100) if total > 0 else np.nan

n = len(df)

# --------------------------
# KPIs (10)
# --------------------------
# % Male vs Female
pct_female = np.nan
pct_male = np.nan
if "CODE_GENDER" in df.columns:
    gender_norm = df["CODE_GENDER"].astype(str).str.strip()
    vc = (gender_norm.value_counts(normalize=True) * 100).to_dict()
    pct_female = vc.get("F", vc.get("Female", np.nan))
    pct_male = vc.get("M", vc.get("Male", np.nan))

# Avg Age — Defaulters / Non-Defaulters
avg_age_def = safe_mean(df.loc[df["TARGET"] == 1, "AGE_YEARS"]) if {"TARGET", "AGE_YEARS"}.issubset(df.columns) else np.nan
avg_age_nondef = safe_mean(df.loc[df["TARGET"] == 0, "AGE_YEARS"]) if {"TARGET", "AGE_YEARS"}.issubset(df.columns) else np.nan

# % With Children
pct_with_children = np.nan
if "CNT_CHILDREN" in df.columns:
    pct_with_children = (df["CNT_CHILDREN"] > 0).mean() * 100

# Avg Family Size
avg_family_size = df["CNT_FAM_MEMBERS"].mean() if "CNT_FAM_MEMBERS" in df.columns else np.nan

# % Married vs Single
pct_married = np.nan
pct_single = np.nan
if "NAME_FAMILY_STATUS" in df.columns:
    fs = df["NAME_FAMILY_STATUS"].astype(str)
    pct_married = fs.str.contains("Married", case=False, na=False).mean() * 100
    pct_single = fs.str.contains("Single", case=False, na=False).mean() * 100

# % Higher Education (Bachelor+) - interpret as 'Higher education' and 'Academic degree'
pct_higher_edu = np.nan
if "NAME_EDUCATION_TYPE" in df.columns:
    he_mask = df["NAME_EDUCATION_TYPE"].isin(["Higher education", "Academic degree"])
    pct_higher_edu = he_mask.mean() * 100

# % Living With Parents
pct_with_parents = np.nan
if "NAME_HOUSING_TYPE" in df.columns:
    pct_with_parents = (df["NAME_HOUSING_TYPE"] == "With parents").mean() * 100

# % Currently Working (derive from OCCUPATION_TYPE or EMPLOYMENT_YEARS)
pct_currently_working = np.nan
if "OCCUPATION_TYPE" in df.columns:
    occ = df["OCCUPATION_TYPE"].astype(str).str.strip().str.lower()
    non_working_values = {"nan", "none", "unknown", "other", ""}
    working_mask = ~occ.isin(non_working_values)
    pct_currently_working = working_mask.mean() * 100
elif "EMPLOYMENT_YEARS" in df.columns:
    pct_currently_working = (df["EMPLOYMENT_YEARS"] > 0).mean() * 100

# Avg Employment Years
avg_employment_years = df["EMPLOYMENT_YEARS"].mean() if "EMPLOYMENT_YEARS" in df.columns else np.nan

# Display KPIs
r1 = st.columns(5)
r2 = st.columns(5)

r1[0].metric("% Female", f"{pct_female:.1f}%" if not np.isnan(pct_female) else "NA")
r1[1].metric("% Male", f"{pct_male:.1f}%" if not np.isnan(pct_male) else "NA")
r1[2].metric("Avg Age — Defaulters", f"{avg_age_def:.1f}" if not np.isnan(avg_age_def) else "NA")
r1[3].metric("Avg Age — Non-Defaulters", f"{avg_age_nondef:.1f}" if not np.isnan(avg_age_nondef) else "NA")
r1[4].metric("% With Children", f"{pct_with_children:.1f}%" if not np.isnan(pct_with_children) else "NA")

r2[0].metric("Avg Family Size", f"{avg_family_size:.2f}" if not np.isnan(avg_family_size) else "NA")
r2[1].metric("% Married", f"{pct_married:.1f}%" if not np.isnan(pct_married) else "NA")
r2[2].metric("% Single", f"{pct_single:.1f}%" if not np.isnan(pct_single) else "NA")
r2[3].metric("% Higher Education", f"{pct_higher_edu:.1f}%" if not np.isnan(pct_higher_edu) else "NA")
r2[4].metric("% Living With Parents", f"{pct_with_parents:.1f}%" if not np.isnan(pct_with_parents) else "NA")

st.markdown("---")

# --------------------------
# Graphs (10)
# --------------------------
st.subheader("Charts")

# 1. Histogram — Age distribution (all)
if "AGE_YEARS" in df.columns:
    fig1 = px.histogram(df, x="AGE_YEARS", nbins=40, title="Age Distribution (All Applicants)")
    st.plotly_chart(fig1, use_container_width=True)
else:
    st.info("AGE_YEARS missing — cannot show Age distribution.")

# 2. Histogram — Age by Target (overlay)
if {"AGE_YEARS", "TARGET"}.issubset(df.columns):
    fig2 = px.histogram(df, x="AGE_YEARS", color="TARGET", barmode="overlay", nbins=40,
                        title="Age Distribution by Target (overlay)",
                        labels={"TARGET": "Target (0=Repaid,1=Default)"})
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.info("AGE_YEARS or TARGET missing — skipping Age by Target overlay.")

# 3. Bar — Gender distribution
if "CODE_GENDER" in df.columns:
    gender_df = df["CODE_GENDER"].value_counts().reset_index()
    gender_df.columns = ["CODE_GENDER", "Count"]
    fig3 = px.bar(gender_df, x="CODE_GENDER", y="Count", text="Count", title="Gender Distribution")
    st.plotly_chart(fig3, use_container_width=True)
else:
    st.info("CODE_GENDER missing — cannot show Gender distribution.")

# 4. Bar — Family Status distribution
if "NAME_FAMILY_STATUS" in df.columns:
    fam_df = df["NAME_FAMILY_STATUS"].value_counts().reset_index()
    fam_df.columns = ["NAME_FAMILY_STATUS", "Count"]
    fig4 = px.bar(fam_df, x="NAME_FAMILY_STATUS", y="Count", text="Count", title="Family Status Distribution")
    st.plotly_chart(fig4, use_container_width=True)
else:
    st.info("NAME_FAMILY_STATUS missing — cannot show Family Status distribution.")

# 5. Bar — Education distribution
if "NAME_EDUCATION_TYPE" in df.columns:
    edu_df = df["NAME_EDUCATION_TYPE"].value_counts().reset_index()
    edu_df.columns = ["NAME_EDUCATION_TYPE", "Count"]
    fig5 = px.bar(edu_df, x="NAME_EDUCATION_TYPE", y="Count", text="Count", title="Education Distribution")
    st.plotly_chart(fig5, use_container_width=True)
else:
    st.info("NAME_EDUCATION_TYPE missing — cannot show Education distribution.")

# 6. Bar — Occupation distribution (top 10)
if "OCCUPATION_TYPE" in df.columns:
    occ_df = df["OCCUPATION_TYPE"].value_counts().head(10).reset_index()
    occ_df.columns = ["OCCUPATION_TYPE", "Count"]
    fig6 = px.bar(occ_df, x="OCCUPATION_TYPE", y="Count", text="Count", title="Top 10 Occupations")
    st.plotly_chart(fig6, use_container_width=True)
else:
    st.info("OCCUPATION_TYPE missing — cannot show Occupation distribution.")

# 7. Pie — Housing Type distribution
if "NAME_HOUSING_TYPE" in df.columns:
    ht = df["NAME_HOUSING_TYPE"].value_counts().reset_index()
    ht.columns = ["NAME_HOUSING_TYPE", "Count"]
    fig7 = px.pie(ht, values="Count", names="NAME_HOUSING_TYPE", title="Housing Type Distribution")
    st.plotly_chart(fig7, use_container_width=True)
else:
    st.info("NAME_HOUSING_TYPE missing — cannot show Housing Type pie.")

# 8. Countplot — CNT_CHILDREN
if "CNT_CHILDREN" in df.columns:
    children_df = df["CNT_CHILDREN"].value_counts().sort_index().reset_index()
    children_df.columns = ["CNT_CHILDREN", "Count"]
    fig8 = px.bar(children_df, x="CNT_CHILDREN", y="Count", text="Count", title="Count of Children (CNT_CHILDREN)")
    st.plotly_chart(fig8, use_container_width=True)
else:
    st.info("CNT_CHILDREN missing — cannot show children countplot.")

# 9. Boxplot — Age vs Target
if {"AGE_YEARS", "TARGET"}.issubset(df.columns):
    fig9 = px.box(df, x="TARGET", y="AGE_YEARS", points="outliers",
                  title="Age by Target (Boxplot)",
                  labels={"TARGET": "Target (0=Repaid,1=Default)", "AGE_YEARS": "Age (years)"})
    st.plotly_chart(fig9, use_container_width=True)
else:
    st.info("AGE_YEARS or TARGET missing — cannot show Age vs Target boxplot.")

# 10. Heatmap — Corr(Age, Children, Family Size, TARGET)
corr_cols = [c for c in ["AGE_YEARS", "CNT_CHILDREN", "CNT_FAM_MEMBERS", "TARGET"] if c in df.columns]
if len(corr_cols) >= 2:
    corr_df = df[corr_cols].corr(numeric_only=True)
    fig10 = px.imshow(corr_df, text_auto=True, aspect="auto",
                      title="Correlation: Age, Children, Family Size, TARGET")
    st.plotly_chart(fig10, use_container_width=True)
else:
    st.info("Not enough columns for correlation heatmap (need AGE_YEARS, CNT_CHILDREN, CNT_FAM_MEMBERS, TARGET).")

st.markdown("---")
st.subheader("Narrative")
st.markdown("""
- Look for **life-stage patterns**: younger applicants may have different default exposure (e.g., early-career, lower income)
  while older applicants may be more stable but with larger credit sizes.  
- **Children & family size**: larger families increase household obligations — check whether default rates rise with number of children or family members.  
- **Employment tenure** and **occupation** are stability indicators — short employment years often correlate with higher risk.
""")
