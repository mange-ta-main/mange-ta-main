import matplotlib
import streamlit as st
from utils.data_loader import load_data
import pandas as pd
import matplotlib.pyplot as plt
matplotlib.use("Agg")  # backend non graphique compatible Streamlit
import seaborn as sns
from utils.sidebar import kaggle_link

kaggle_link()

# Configuration de la page
st.set_page_config(page_title="Analyse qualitative des recettes")

# Chargement et préparation des données
df_recipes, df_interactions = load_data()

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

st.dataframe(df_recipes[["Calories", "Sugar", "Sodium"]].head(10))

st.dataframe(
    df_recipes[nutriments]
        .describe()
        .loc[["mean", "std", "min", "max"]]
        .round(2)
)

# Visualisation
st.subheader("Analyse détaillée par nutriment")

selected_nutriment = st.radio(
    "Choisissez un nutriment :",
    nutriments,
    horizontal=False
)

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