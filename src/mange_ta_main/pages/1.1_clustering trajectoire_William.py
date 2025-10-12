import numpy as np
import streamlit as st
import pandas as pd
import matplotlib
matplotlib.use('MacOSX')   # backend natif pour macOS
import matplotlib.pyplot as plt

from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

# ------------------------------------------------------------------------------------------------------------------------#
# ------------------------------------------------- BIVARIE --------------------------------------------------------------#
# ------------------------------------------------------------------------------------------------------------------------#

df_recipes = pd.read_pickle("Data/RAW_recipes_local.pkl")
df_interactions = pd.read_pickle("Data/RAW_interactions_local.pkl")

# conversion du champ de dates
df_recipes['submitted']=pd.to_datetime(df_recipes['submitted'],errors='coerce') # transforme submitted en une date lisible par panda (format datetime64)
df = df_recipes[['submitted','contributor_id','id']]                    # garder que les données intéressantes
df = df.sort_values('submitted')                                        # tri par date de soumission
#df['contributor_id']=df['contributor_id'].astype(int).astype(str)       # on force contributor id en texte pour éviter les problème en cas de merge sur la colonne par exemple
print(df.head(5))

# création d'une matrice activité - agrégation par mois de l'activité par auteur
        # chaque ligne = un auteur
        # chaque colonne = un mois
        # chaque cellule = nombre de recettes publiées ce mois-là.

def build_activity_matrix(df, freq="M"):
    """Crée la matrice auteurs × période"""
    df["month"] = df["submitted"].dt.to_period(freq).dt.to_timestamp()
    activity = (
        df.groupby(["contributor_id", "month"])["id"]
          .nunique()
          .unstack(fill_value=0)
          .sort_index(axis=1)
    )
    return activity

# filtrer les 277 top contributeurs
def filter_top_contributors(df, top_n=277):
    contrib_counts = df.groupby("contributor_id")["id"].nunique().sort_values(ascending=False)
    top_authors = contrib_counts.head(top_n).index
    return df[df["contributor_id"].isin(top_authors)]


def prepare_for_clustering(df):
    """Pipeline complet avant clustering"""
    df_top = filter_top_contributors(df, 277)
    activity = build_activity_matrix(df_top)
    return activity


# Construction de la matrice d'activité
activity = prepare_for_clustering(df)

# Standardisation + clustering
scaler = StandardScaler()
X = scaler.fit_transform(activity.rolling(window=3, axis=1, min_periods=1).mean())

k = 4
km = KMeans(n_clusters=k, random_state=42)      # Le modèle KMeans regroupe les trajectoires similaires ensemble
labels = km.fit_predict(X)

activity["cluster"] = labels

n_clusters_found = len(set(labels))
print("Nombre de clusters créés :", n_clusters_found)
# ---------------------------------------------------------------------------------------#
plt.figure(figsize=(10,4))
for c in range(4):  # 4 clusters
    plt.plot(activity.columns[:-1], km.cluster_centers_[c], label=f"Cluster {c}")
plt.title("Évolution moyenne standardisée de l'activité par cluster")
plt.xlabel("Mois")
plt.ylabel("Z-score d'activité")
plt.legend()
plt.tight_layout()
plt.show()
# ---------------------------------------------------------------------------------------#


cluster_3 = activity[activity['cluster']==3]
contributor_cluster_3 = cluster_3.index.tolist()
print(f'nombre de contributeurs dans cluster_3:',len(contributor_cluster_3)) # le cluster 3 ne contient qu'une seule personne
id_super_star = contributor_cluster_3[0]
nb_recettes = df_recipes[df_recipes['contributor_id']==id_super_star].shape[0]
print(f'nombre de recette de la super stare: ',nb_recettes)

print(type(id_super_star))
print(df_recipes['contributor_id'].dtype)

# Analyse univariée:
# - l'analyse univariée de contributor_id a montré qu'il y avait un top_contributor(277) correspondant au percentil 99;
# - il y avait également au sein de ce P99 une hétérogénéité des contribution (6 personnes contribuaient à 5% des publications)
# - je reste néanmoins sur une sélction de P99 dans sa globalité qui contribuent à 66% des recettes
# - la courbe de Lorentz permet de mettre en avant le phénomène d'une loi Pareto - avec une surconcentration des contrinutions sur une minorité de contributeurs

# Analyse bivariée
# - l'étude univariée est prolongée avec l'étude dans le temps de P99;
# - on distingue 3 clusters: 
#       - cluster 0:	Contributeurs réguliers sur le long terme
#       - cluster 1:	Contributeurs marginaux / peu actifs
#       - cluster 2:	Pionniers historiques (2000–2006)
#       - cluster 3:	Nouvelle vague (2008–2015)
# L'étude s'arrête en 2018 mais on remarque que la plateforme n'est plus entretenue dès 2014. Donc un choix peut être de considérer 
# une étude de 2000 à 2014.

# Dans le cadre de la fidélisation des conributeurs, il faudrait récompenser les contributeurs des clusters 0 et 3 (réguliers et nouvelle vague)



