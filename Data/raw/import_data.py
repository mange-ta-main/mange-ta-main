# Install dependencies as needed:
# pip install kagglehub[pandas-datasets]
from kagglehub import KaggleDatasetAdapter, load_dataset
import os
import pandas as pd

# Paths
os.makedirs("Data", exist_ok=True)  # crée Data/ si nécessaire
recipes_csv_path = "Data/RAW_recipes_local.csv"
recipes_pkl_path = "Data/RAW_recipes_local.pkl"
interactions_csv_path = "Data/RAW_interactions_local.csv"
interactions_pkl_path = "Data/RAW_interactions_local.pkl"

# Étape 1 : télécharger le CSV des recettes seulement s'il n'existe pas
if not os.path.exists(recipes_csv_path):
    print("CSV non trouvé, téléchargement.")
    file_path = "RAW_recipes.csv"
    df = load_dataset(
        KaggleDatasetAdapter.PANDAS,
        "shuyangli94/food-com-recipes-and-user-interactions",
        file_path,
    )
    df.to_csv(recipes_csv_path, index=False)
    print(f"CSV sauvegardé dans {recipes_csv_path}")
else:
    print("Recipes CSV déjà présent, lecture locale...")
    df = pd.read_csv(recipes_csv_path)


# Étape 2 : créer un pickle pour les interactions seulement s'il n'existe pas
if not os.path.exists(recipes_pkl_path):
    df.to_pickle(recipes_pkl_path)
    print(f"Interactions pickle créé : {recipes_pkl_path}")
else:
    print("Interactions pickle déjà présent.")


# Étape 3 : télécharger le CSV des intercations seulement s'il n'existe pas
if not os.path.exists(interactions_csv_path):
    print("Interactions CSV non trouvé, téléchargement.")
    file_path = "RAW_interactions.csv"
    df = load_dataset(
        KaggleDatasetAdapter.PANDAS,
        "shuyangli94/food-com-recipes-and-user-interactions",
        file_path,
    )
    df.to_csv(interactions_csv_path, index=False)
    print(f"CSV sauvegardé dans {interactions_csv_path}")
else:
    print("Interactions CSV déjà présent, lecture locale...")
    df = pd.read_csv(interactions_csv_path)
    
# Étape 4 : créer un pickle pour les recipes seulement s'il n'existe pas
if not os.path.exists(interactions_pkl_path):
    df.to_pickle(interactions_pkl_path)
    print(f"Interactions pickle créé : {interactions_pkl_path}")
else:
    print("Interactions pickle déjà présent.")

# Aperçu
print("First 5 records:", df.head())
