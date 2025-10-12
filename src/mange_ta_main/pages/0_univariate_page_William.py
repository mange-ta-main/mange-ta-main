import numpy as np
import streamlit as st
import pandas as pd
import matplotlib
matplotlib.use('MacOSX')   # backend natif pour macOS
import matplotlib.pyplot as plt




df_recipes = pd.read_pickle("Data/RAW_recipes_local.pkl")
df_interactions = pd.read_pickle("Data/RAW_interactions_local.pkl")


# Essais avec Streamlit
'''
st.title('Visualisation des données')
st.write('vous ne serez pas déçus')

variables = recipes.columns.tolist()
choix = st.selectbox('choisi ta variable pour dessiner l histogramme:',variables,key='choix')
choix_numeriques = ['minutes','n_steps','n_ingredients','id','contributor_id']

if  choix in choix_numeriques:
    plt.hist(recipes[choix],edgecolor = 'black',bins=20)
    plt.title(f"Histogramme de la variable {choix}")
    plt.xlabel(choix)
    plt.ylabel("Fréquence")
    st.pyplot(plt)
else: 
    st.warning('on ne peut pas tracer de graphe pour cette variable')


# Calcul du nombre de données manquantes
Missing_value = st.selectbox('choisi ta variable pour afficher le nombre de données manquantes:',variables,key='missing value')
seuil_data_missing = 10

nb_val_manquante_i = recipes[Missing_value].isna().sum()
if nb_val_manquante_i<seuil_data_missing:
     st.write(f'Nombre de données manquantes: {nb_val_manquante_i}. Peu de données pour la variable **{Missing_value}** ({nb_val_manquante_i})')
     # J'ai un doute sur le nombre de données manquantes et calcul fait. Le nombre me parait faible
else:
     st.write(f'il manque beaucoup de données pour la variable **{Missing_value}** ({nb_val_manquante_i})')
'''

# Cas à étudier :
# - quels sont les contributeurs qui font vivrent la plateforme (et donc ceux qu'il faudra cibler et encourage à améliorer les recettes dans une démarches de santé publique)
# /! Pour cette question, i sera intéressant d'associer les notes aux contributeurs /!
# - cuisine t'on plus vite avec le temps (étude en bivariée) -> cette étude pourra être reprise en troisième partie avec l'évolution de ce temps de préparation par rapport à la qualité


# Quels sont les contributeurs à fidéliser le plus ?

# recipes count per contributor
nb_recipes_contributor = df_recipes['contributor_id'].value_counts()

# Recipes number
total_recipes = df_recipes.shape[0]
print(f'total recipes: ', total_recipes)

# moyenne/min/max recipes per contributors
mean_contribution = nb_recipes_contributor.mean()
max_contribution = nb_recipes_contributor.max()
min_contribution = nb_recipes_contributor.min()

print(f'mean contribution: ', mean_contribution)    # mean : 8 recipes
print(f'max contribution: ',max_contribution)       # max : 3118 recipes
print(f'min contribution: ',min_contribution)       # min: 1 recipes

# repartition histogram
# plt.hist(Nb_recipes_contributor,bins=50)
# plt.show()                                           # La distribution est très étalée: quelques forts contributeurs et très concentrée (1 à 20 recettes par contributeurs)

# Q3 study
Q3 = np.percentile(nb_recipes_contributor,75)
print(f"Seuil du 3ᵉ quartile (Q3) : {Q3:.0f} recettes")

# Top contributor
top_contributors = nb_recipes_contributor[nb_recipes_contributor>=Q3]
print("Nb de contributeurs (Q3+):", top_contributors.size)

# part du total des contributeurs
share_contributors = top_contributors.size / nb_recipes_contributor.size
print(f"Part des contributeurs (Q3+): {share_contributors:.2%}")

# part du total des recettes produites par ces top contributeurs
share_recipes = top_contributors.sum() / nb_recipes_contributor.sum()
print(f"Part des recettes produites par (Q3+): {share_recipes:.2%}")


# On obtient:
# - Nb de contributeurs (Q3+): 8834
# - Part des contributeurs (Q3+): 31.63%
# - Part des recettes produites par (Q3+): 90.14%

# Il faut réduire la taille du nombre de contributeurs avec: P90/P95/P99

# P90
P90 = np.percentile(nb_recipes_contributor,90)
print(f'seuil de P90: {P90:.0f} recettes')
top_P90_contributors = nb_recipes_contributor[nb_recipes_contributor>P90]
print(f'Nbre de contributeurs (P90) :',top_P90_contributors.size)
share_recipes_P90 = top_P90_contributors.sum()/nb_recipes_contributor.sum()
print(f'Part des recettes prooduites par (P90): {share_recipes:.2%}')
# On trouve : 
# - seuil de P90: 11 recettes
# - Nbre de contributeurs (P90) : 2632
# - Part des recettes prooduites par (P90): 90.14%
# diff Q3 & P90
diff_Q3_P90 = nb_recipes_contributor[(nb_recipes_contributor>=Q3)&(nb_recipes_contributor<P90)]
print(f'nombre de contributeurs sur les 15 pourcent entre Q3 et P90:',diff_Q3_P90.size)
share_diff_Q3_P90 = diff_Q3_P90.sum()/nb_recipes_contributor.sum()
print(f'Part des recettes prooduites par diff Q3_P90): {share_diff_Q3_P90:.2%}')

# Conclusion: 
# - les 15% de contributeurs entre Q3 et P90 ne pèsent quasiment pour rien. Ils pèsent pour 13% des recettes produites
# - on resserre l'intervalle avec le percentile P95

# P95
P95 = np.percentile(nb_recipes_contributor,95)
print(f'seuil de P95: {P95:.0f} recettes')
top_P95_contributors = nb_recipes_contributor[nb_recipes_contributor>P95]
print(f'Nbre de contributeurs (P95) :',top_P95_contributors.size)
share_recipes_P95 = top_P95_contributors.sum()/nb_recipes_contributor.sum()
print(f'Part des recettes prooduites par (P95): {share_recipes_P95:.2%}')

# dif P95_P90
diff_P90_P95 = nb_recipes_contributor[(nb_recipes_contributor>=P90)&(nb_recipes_contributor<P95)]
print(f'nombre de contributeurs sur les 15 pourcent entre P90 et P95:',diff_P90_P95.size)
share_diff_P90_P95 = diff_P90_P95.sum()/nb_recipes_contributor.sum()
print(f'Part des recettes prooduites par diff Q3_P90): {share_diff_P90_P95:.2%}')

# P99
P99 = np.percentile(nb_recipes_contributor,99)
print(f'seuil de P99: {P99:.0f} recettes')
top_P99_contributors = nb_recipes_contributor[nb_recipes_contributor>P99]
print(f'Nbre de contributeurs (P99) :',top_P99_contributors.size)
share_recipes_P99 = top_P99_contributors.sum()/nb_recipes_contributor.sum()
print(f'Part des recettes prooduites par (P99): {share_recipes_P95:.2%}')

# Conclusion:
# - 1% des 8834 contributeurs publient les 2/3 des recettes du sites. Donc une poignée d'hyper actif fait vivre la plateforme.
# - On va donc cibler l'étude de santé publique sur ces 1% (277 contributeurs)
# - j'illustre ces résultats avec une courbe de Lorentz

# Tri décroissant
counts_sorted = nb_recipes_contributor.sort_values(ascending=False).values

# Courbe de Lorenz
cum_recipes = np.cumsum(counts_sorted) / np.sum(counts_sorted)
cum_contributors = np.arange(1, len(counts_sorted)+1) / len(counts_sorted)

# Tracé courbe de Lorentz
# ---------------------------------------------------------------------------------------#
# plt.figure(figsize=(7,6))
# plt.plot(cum_contributors, cum_recipes, label="Courbe de Lorenz", color="darkorange")
# plt.plot([0,1],[0,1], linestyle="--", color="gray", label="Égalité parfaite")
# plt.xlabel("Part cumulée des contributeurs")
# plt.ylabel("Part cumulée des recettes")
# plt.title("Courbe de concentration des contributions")
# plt.legend()
# plt.grid(True, alpha=0.3)
# plt.show()
# ---------------------------------------------------------------------------------------#

top_P99_contributors = nb_recipes_contributor[nb_recipes_contributor>P99]
# ---------------------------------------------------------------------------------------#
# plt.hist(top_P99_contributors,bins=20,log=True)
# plt.xlabel("Nombre de recettes par contributeur")
# plt.ylabel("Fréquence (log)")
# plt.title("Distribution des recettes parmi les 277 top contributeurs")
# plt.show()
# ---------------------------------------------------------------------------------------#

# Conclusion complémentaire:
# - en traçant l'histogramme des 277 plus gros contributeurs (percentil 99), on remarque que même entre eux il y a de grandes disparités.

# Comptage du nombre de recettes par contributeur
count = df_recipes['contributor_id'].value_counts()

# Filtrage des "outliers" : contributeurs entre 1250 et 1350 recettes
band = count[(count > 1250) & (count <= 3500)].sort_values(ascending=True)

# Taille et part de ce groupe
n_band = band.size
share_band = band.sum() / count.sum()

print(f"Contributeurs entre 1250 et 3500 recettes : {n_band}")
print(f"Contribution de ces {n_band} contributeurs : {share_band:.2%}")


# ------------------------------------------------------------------------------------------------------------------------#
# ------------------------------------------------- BIVARIE --------------------------------------------------------------#
# ------------------------------------------------------------------------------------------------------------------------#

# Etude des top_277 contributeurs dans le temps
# On fait un clustering des trajectoirres temporelles des contributeurs





# Sélection des deux colonnes 'contributor_id' et 'submitted'
#df_contributions = df_recipes[['contributor_id','submitted']]
