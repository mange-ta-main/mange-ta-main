import streamlit as st
from utils.data_loader import load_data
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Configuration de la page
st.set_page_config(page_title="Analyse qualitative des recettes")

# Chargement et préparation des données
df_recipes, df_interactions = load_data()

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

# Répartition des apports nutritionnels
st.title("Quelle est la répartition des apports nutritionnels par recette ?")

nutriments = [
    "Calories", 
    "Total fat", 
    "Sugar", 
    "Sodium", 
    "Protein", 
    "Saturated fat", 
    "Carbohydrates"
]

st.dataframe(df_recipes[nutriments].describe().round(2))

# Visualisation
st.subheader("Analyse détaillée par nutriment")

selected_nutriment = st.selectbox("Choisissez un nutriment :", nutriments, index=0)

# Statistiques du nutriment sélectionné
st.write(f"**Statistiques descriptives — {selected_nutriment}**")
st.dataframe(df_recipes[selected_nutriment].describe().to_frame().T)

# Histogramme interactif
fig, ax = plt.subplots(figsize=(7, 4))
sns.histplot(df_recipes[selected_nutriment], kde=True, ax=ax, color="skyblue", edgecolor="white")
ax.set_title(f"Distribution de {selected_nutriment}", fontsize=13)
ax.set_xlabel(selected_nutriment)
ax.set_ylabel("Nombre de recettes")
st.pyplot(fig)


#st.title("Le temps de réalisation des recettes a-t-il un impact sur la qualité des apports nutritionnels ?")