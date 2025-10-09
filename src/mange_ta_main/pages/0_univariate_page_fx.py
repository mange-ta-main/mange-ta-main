import streamlit as st
from utils.data_loader import load_data
import pandas as pd

#Get datas
df_temp = load_data()
st.set_page_config(page_title="Contributor_id")
st.title("Qui fait vivre la plateforme ?")

st.subheader("Résumé statistique")
st.dataframe(df_temp.describe())

