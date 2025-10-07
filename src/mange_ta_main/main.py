from utils.data_loader import load_data
import streamlit as st
df_recipes, df_interactions = load_data()

# Display basic info
st.header("Data")
st.title("RECIPES:")
st.dataframe(df_recipes.head())
st.title("INTERACTIONS:")
st.dataframe(df_interactions.head())
