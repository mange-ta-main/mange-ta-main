import streamlit as st
import pandas as pd
from pathlib import Path

# this can be in a settings file later
DATA_DIR = Path(__file__).parent.parent.parent / "Data"
CSV_FILE = DATA_DIR / "RAW_recipes_local.csv"

# Load the data
@st.cache_data  # Cache the data for better performance
def load_data():
    return pd.read_csv(CSV_FILE.resolve())

df = load_data()
# Display basic info
st.header("Data hajdfdsfsd")
st.write(f"Shape: {df.shape[0]} rows, {df.shape[1]} columns")
st.dataframe(df.head())

# Create histogram
st.header("Histogram")
column = st.selectbox("Select column for histogram:", df.select_dtypes(include='number').columns)

if column:
    fig = df[column].hist(bins=30)
    st.pyplot(fig.get_figure())