import pandas as pd
from pathlib import Path
import streamlit as st

DATA_DIR = Path("Data")
RECIPES_PICKLE_FILE = DATA_DIR / "RAW_recipes_local.pkl"
INTERACTIONS_PICKLE_FILE = DATA_DIR / "RAW_interactions_local.pkl"

@st.cache_data
def load_data() -> tuple[pd.DataFrame | pd.Series, pd.DataFrame | pd.Series]:
    return pd.read_pickle(RECIPES_PICKLE_FILE.resolve()), pd.read_pickle(INTERACTIONS_PICKLE_FILE)
