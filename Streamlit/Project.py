# preview_cleaned Data
import streamlit as st
import pandas as pd
from utils.load_data import load_data
from utils.preprocess import preprocess
st.set_page_config(page_title="Home Credit  Dashboard", page_icon="🛍️", layout="wide")

st.title("Home Credit Default Risk Dashboard")

st.markdown("""
Welcome to the **Home Credit Dashboard** built with **Streamlit**.  
Use the sidebar to navigate between different analysis modules:
* Overview & Data Quality  
* Target & Risk Segmentation 
* Demographics & Household Profile 
* Financial Health & Affordability
* Correlations, Drivers & Interactive Slice-and-Dice
""")


#Preview Cleaned Dataset

df_raw = load_data("application_train.csv")
df_clean, _ = preprocess(df_raw, verbose=False)

st.write("Shape of cleaned dataset:", df_clean.shape)
st.write("columns in cleaned dataset : ",df_clean.columns)
st.dataframe(df_clean.head(20))
