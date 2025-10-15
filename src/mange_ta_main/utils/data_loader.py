import pandas as pd
from pathlib import Path
import streamlit as st

DATA_DIR = Path("Data")
RECIPES_PICKLE_FILE = DATA_DIR / "RAW_recipes_local.pkl"
INTERACTIONS_PICKLE_FILE = DATA_DIR / "RAW_interactions_local.pkl"

@st.cache_data
<<<<<<< HEAD
def load_data() -> tuple[pd.DataFrame | pd.Series, pd.DataFrame | pd.Series]:
    return pd.read_pickle(RECIPES_PICKLE_FILE.resolve()), pd.read_pickle(INTERACTIONS_PICKLE_FILE)


def load_tags() -> pd.DataFrame:
    return pd.read_pickle(DATA_DIR / "tags_coocurence.csv")
=======
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
>>>>>>> 2c66e48 (Added the kaggle link in the sidebar)
