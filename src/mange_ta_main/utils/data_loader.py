import pandas as pd
import streamlit as st
from pathlib import Path

DATA_DIR = Path("Data")
RECIPES_PICKLE_FILE = DATA_DIR / "RAW_recipes_local.pkl"
INTERACTIONS_PICKLE_FILE = DATA_DIR / "RAW_interactions_local.pkl"

@st.cache_data
def load_data():
    df_recipes = pd.read_pickle(RECIPES_PICKLE_FILE.resolve())
    # Séparation des données nutritionnelles
    nutrition_split = (
        df_recipes["nutrition"]
        .str.strip("[]")
        .str.replace(" ", "", regex=False)
        .str.split(",", expand=True)
    )
    nutrition_split.columns = [
        "Calories", 
        "Total fat", 
        "Sugar", 
        "Sodium", 
        "Protein", 
        "Saturated fat", 
        "Carbohydrates"
    ]
    nutrition_split = nutrition_split.astype(float)
    # Fusion et nettoyage
    df_recipes = pd.concat([df_recipes, nutrition_split], axis=1)
    df_recipes.drop(columns=["nutrition"], inplace=True)
    
    return df_recipes, pd.read_pickle(INTERACTIONS_PICKLE_FILE)