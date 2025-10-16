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

# création d'une matrice activité - agrégation par mois de l'activité par auteur
        # chaque ligne = un auteur
        # chaque colonne = un mois
        # chaque cellule = nombre de recettes publiées ce mois-là.

def build_activity_matrix(df, freq="M"):
    """Crée la matrice auteurs x période"""
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
# plt.figure(figsize=(10,4))
# for c in range(4):  # 4 clusters
#     plt.plot(activity.columns[:-1], km.cluster_centers_[c], label=f"Cluster {c}")
# plt.title("Évolution moyenne standardisée de l'activité par cluster")
# plt.xlabel("Mois")
# plt.ylabel("Z-score d'activité")
# plt.legend()
# plt.tight_layout()
# plt.show()
# ---------------------------------------------------------------------------------------#

# étude des cluster 0 et 3
cluster_3 = activity[activity['cluster']==3]
cluster_0 = activity[activity['cluster']==0]
cluster_1 = activity[activity['cluster']==1]
cluster_2 = activity[activity['cluster']==2]

print(f'nombre de contributeurs dans cluster_3:',cluster_3.shape[0])
print(f'nombre de contributeurs dans cluster_1:',cluster_1.shape[0])
print(f'nombre de contributeurs dans cluster_2:',cluster_2.shape[0])
print(f'nombre de contributeurs dans cluster_0:',cluster_0.shape[0])

nb_recettes_cluster_1 = df_recipes[df_recipes['contributor_id'].isin(cluster_1.index)].shape[0]
nb_recettes_cluster_3 = df_recipes[df_recipes['contributor_id'].isin(cluster_3.index)].shape[0]
nb_recettes_cluster_0 = df_recipes[df_recipes['contributor_id'].isin(cluster_0.index)].shape[0]

print(f'nombre de recette de cluster 3: ',nb_recettes_cluster_3)
print(f'nombre de recette de cluster 0: ',nb_recettes_cluster_0)    # beaucoup de recettes ont été publiées à l'ouverture du site et sont historiques
print(f'nombre de recette de cluster 1: ',nb_recettes_cluster_1)


# Etude avec un critère de réescense
START, END = pd.Timestamp('2008-01-01'), pd.Timestamp('2014-12-31')

# Contributeurs des clusters 0 & 3
targets = activity.index[activity['cluster'].isin([0, 3])]

# Dernière publication (toutes périodes)
last_pub = df_recipes.groupby('contributor_id')['submitted'].max()

# Diagnostic : % des cibles (0/3) qui NE sont plus actives en fin de fenêtre
cutoff = pd.Timestamp('2013-01-01')
pct_inactifs = (last_pub.loc[targets] < cutoff).mean()
print(f"% des contributeurs 0/3 inactifs depuis avant 2013 : {pct_inactifs:.1%}")

# Super cœur récent : 0/3 avec dernière publication dans la fenêtre (ou après cutoff)
super_coeur = [cid for cid in targets if last_pub.get(cid, pd.Timestamp.min) >= cutoff]
print("Taille du super cœur (récents) :", len(super_coeur))

# Option régularité: mois actifs entre 2008 et 2014
df_win = df_recipes[(df_recipes['submitted']>=START) & (df_recipes['submitted']<=END)]
df_win = df_win[df_win['contributor_id'].isin(targets)].copy()
df_win['month'] = df_win['submitted'].dt.to_period('M').dt.to_timestamp()

mois_actifs = (df_win.groupby(['contributor_id','month'])['id'].nunique()>0)\
               .groupby('contributor_id').sum()
super_coeur_reg = mois_actifs[mois_actifs >= 6].index.tolist()  # ex. ≥ 6 mois actifs


# extraction du super coeur
df_super_coeur = df_recipes[df_recipes['contributor_id'].isin(super_coeur)]

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
# nombre de contributeurs dans cluster_3: 33
# nombre de contributeurs dans cluster_0: 5
# nombre de recette de cluster 3:  16923
# nombre de recette de cluster 0:  10790
# super coeur participe à 10% du site

# Etude de rescence
# en faisant une étude de rescence selon les critères suivants 
#   - Appartenance à clusters 0 ou 3
#   - Dernière publi ≥ 2013-01-01
#   - (Option) ≥ 6 mois actifs sur 2008–2014
# 
# on obtient:
#   - % des contributeurs 0/3 inactifs depuis avant 2013 : 13.2%
#   - Taille du super cœur (récents) : 33

# combien de recettes pour super_coeur ?
print(super_coeur)
recettes_sp = df[df['contributor_id'].isin(super_coeur)]['id'].shape[0]
print(recettes_sp)
repartition_sp = round(recettes_sp/(df['id'].count())*100,2)
print(repartition_sp)

df_recipes.head()


