from pathlib import Path
import pandas as pd
import streamlit as st

DATA_DIR = Path("Data")
RECIPES_PICKLE_FILE = DATA_DIR / "RAW_recipes_local.pkl"
INTERACTIONS_PICKLE_FILE = DATA_DIR / "RAW_interactions_local.pkl"
TAGS_COOCURENCE = DATA_DIR / "tags_coocurence.pkl"

nutrition_categories = [
    "Calories",
    "Total fat",
    "Sugar",
    "Sodium",
    "Protein",
    "Saturated fat",
    "Carbohydrates",
]


@st.cache_data
def load_interactions() -> pd.DataFrame:
    return pd.read_pickle(INTERACTIONS_PICKLE_FILE)


@st.cache_data
def load_recipes() -> pd.DataFrame:
    recipes = pd.read_pickle(RECIPES_PICKLE_FILE.resolve())
    # Séparation des données nutritionnelles
    nutrition_split = (
        recipes["nutrition"]
        .str.strip("[]")
        .str.replace(" ", "", regex=False)
        .str.split(",", expand=True)
    )
    nutrition_split.columns = nutrition_categories
    nutrition_split = nutrition_split.astype(float)
    # Fusion et nettoyage
    recipes = pd.concat([recipes, nutrition_split], axis=1)
    recipes.drop(columns=["nutrition"], inplace=True)

    return recipes


@st.cache_data
def load_tags() -> pd.DataFrame:
    return pd.read_pickle(DATA_DIR / "tags_coocurence.csv")
