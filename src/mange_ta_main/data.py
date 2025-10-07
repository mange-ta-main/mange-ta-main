from pathlib import Path
import pandas as pd
import streamlit as st

CSV_FILE = Path("Data") / "RAW_recipes_local.csv"

@st.cache_data  # Cache the data for better performance
def load_data():
    return pd.read_csv(CSV_FILE.resolve())

