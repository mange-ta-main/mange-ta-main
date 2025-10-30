import streamlit as st
from streamlit_option_menu import option_menu

from utils.sidebar import kaggle_link
from utils.data_loader import load_recipes, load_interactions
from utils.navbar import hide_page_navbar
from utils.navbar import nav


# -------------------------------------------------
# Customed navigation bar
# -------------------------------------------------
# Hide navigation bar based on pages file names
hide_page_navbar()
# Generate customed navigation bar
nav("Data")

kaggle_link()

df_recipes = load_recipes()
df_interactions = load_interactions()

# Display basic info
st.header("Data")
st.title("RECIPES:")
st.dataframe(df_recipes.head())
st.title("INTERACTIONS:")
st.dataframe(df_interactions.head())
