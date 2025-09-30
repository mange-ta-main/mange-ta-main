# Install dependencies as needed:
# pip install kagglehub[pandas-datasets]
import kagglehub
from kagglehub import KaggleDatasetAdapter
import os
import pandas as pd

# Paths
os.makedirs("Data", exist_ok=True)  # crée Data/ si nécessaire
csv_path = "Data/RAW_recipes_local.csv"
pkl_path = "Data/RAW_recipes_local.pkl"

# Étape 1 : télécharger le CSV seulement s'il n'existe pas
if not os.path.exists(csv_path):
    print("CSV non trouvé, téléchargement.")
    file_path = "RAW_recipes.csv"
    df = kagglehub.load_dataset(
        KaggleDatasetAdapter.PANDAS,
        "shuyangli94/food-com-recipes-and-user-interactions",
        file_path,
    )
    df.to_csv(csv_path, index=False)
    print(f"CSV sauvegardé dans {csv_path}")
else:
    print("CSV déjà présent, lecture locale...")
    df = pd.read_csv(csv_path)

# Étape 2 : créer un pickle seulement s'il n'existe pas
if not os.path.exists(pkl_path):
    df.to_pickle(pkl_path)
    print(f"Pickle créé : {pkl_path}")
else:
    print("Pickle déjà présent.")

# Aperçu
print("First 5 records:", df.head())
