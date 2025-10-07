import pandas as pd
from pathlib import Path
import streamlit as st

DATA_DIR = Path("Data")
CSV_FILE = DATA_DIR / "RAW_recipes_local.csv"
PICKLE_FILE = DATA_DIR / "RAW_recipes_local.pkl"

@st.cache_data
def load_data():
    return pd.read_pickle(PICKLE_FILE.resolve())