from utils.data_loader import load_data
import streamlit as st

df_main = load_data()

# Display basic info
st.header("Data")
st.dataframe(df_main.head())