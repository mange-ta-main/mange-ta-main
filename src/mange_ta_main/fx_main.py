##Analyse univariée sur nutrition
import pandas as pd
import os
import matplotlib.pyplot as plt
    
recipes = pd.read_pickle("Data/RAW_recipes_local.pkl")

#Spliting the nutrition datas to perform some analyses
nutrition_split = recipes["nutrition"].str.strip("[]").str.split(",", expand=True)
nutrition_split.columns = [
    "calories", 
    "total fat", 
    "sugar", 
    "sodium", 
    "protein", 
    "saturated fat", 
    "carbohydrates"
]
nutrition_split = nutrition_split.astype(float)
recipes = pd.concat([recipes, nutrition_split], axis=1)

fig, ax = plt.subplots(2, 4, figsize=(20, 8))
ax = ax.flatten()

# I. Data preparation
# 1. How many empty values are there in nutrition scores ?
#Counting the values 
nutrition_sum = nutrition_split.sum(axis=1)
nb_empty = (nutrition_sum==0).sum()
#Plotting the empty values as a barchart
ax[0].bar(["Valeur vides"], [nb_empty])
ax[0].set_title("NB recipes empty nutrition values")

# II. Univariate analysis
# 1. What are the quantiles distribution of each nutrition score ?
cols = [
    "calories",
    "total fat",
    "sugar",
    "sodium",
    "protein",
    "saturated fat",
    "carbohydrates"
]
# Tracer un boxplot pour chaque colonne
for i, col in enumerate(cols, start=1):  # start=1 car ax[0] est déjà utilisé pour les valeurs vides
    col_no_max = recipes[col].drop(recipes[col].idxmax())  # on retire uniquement le max
    ax[i].boxplot(col_no_max)
    ax[i].set_title(f"Boxplot {col}")

#plt.show()

# 2. Get the mean of each nutrition score
dict_mean_values = recipes[cols].mean().round(1).to_dict()
labels = list(dict_mean_values.keys())
values = list(dict_mean_values.values())
print("--------------------------------------------------")
print("--------------------------------------------------")
print("Mean values of nutrition score: ", dict_mean_values)
print("--------------------------------------------------")
print("--------------------------------------------------")
top10_calories = recipes.nlargest(1000, 'calories')
print("Top 1000 fatty recipes:\n", top10_calories[["name", "calories"]])


