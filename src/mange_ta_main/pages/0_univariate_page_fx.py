import streamlit as st
from utils.data_loader import load_data
import pandas as pd

#Get datas
df_temp = load_data()
nutrition_split = df_temp["nutrition"].str.strip("[]").str.split(",", expand=True)
nutrition_split.columns = [
    "calories", 
    "total fat", 
    "sugar", 
    "sodium", 
    "protein", 
    "saturated fat", 
    "carbohydrates"
]
nutrition_split = nutrition_split.astype(float)
df = pd.concat([df_temp, nutrition_split], axis=1)

#Set streamlit parametres for this page
st.set_page_config(page_title="Univariate FX")
st.title("Univariate FX")
st.write("Ceci est la première page.")


st.subheader("Résumé statistique")
st.dataframe(df.describe())

