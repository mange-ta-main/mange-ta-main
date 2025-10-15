from utils.data_loader import load_data
import streamlit as st
<<<<<<< HEAD
=======
from utils.sidebar import kaggle_link

kaggle_link()

>>>>>>> 2c66e48 (Added the kaggle link in the sidebar)
df_recipes, df_interactions = load_data()

# Display basic info
st.header("Data")
st.title("RECIPES:")
st.dataframe(df_recipes.head())
st.title("INTERACTIONS:")
st.dataframe(df_interactions.head())
