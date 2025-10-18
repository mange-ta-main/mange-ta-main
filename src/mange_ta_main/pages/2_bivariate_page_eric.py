import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
# Remove access to utils library due to echec to generate Pickle files with import_data.py
#from mange_ta_main.utils.data_loader import load_data

# Change data extension to catch csv files and not pickle ones
DATA_DIR = "Data"
RECIPES_PICKLE_FILE = DATA_DIR + "\RAW_recipes_local.csv"
INTERACTIONS_PICKLE_FILE = DATA_DIR + "\RAW_interactions_local.csv"

# copy from utils file and change pickle to csv to keep the load_data() function
@st.cache_data
def load_data():
    recipes, interaction_data = pd.read_csv(RECIPES_PICKLE_FILE), pd.read_csv(INTERACTIONS_PICKLE_FILE)
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
    return recipes, interaction_data

# To draw histograms
def histogram(dataset, selected_column, title, bin_nb):
    # Histogram
    st.subheader("Histogram")
    fig, ax = plt.subplots()
    ax.hist(dataset[selected_column].dropna(), align='mid', bins=bin_nb, color='blue', edgecolor='black')
    ax.set_title(title)
    ax.set_xlabel(selected_column)
    ax.set_ylabel("Frequence")
    st.pyplot(fig)

# Load data files
recipes, interaction_data = load_data()

# Page title
st.set_page_config(page_title="Bivariate Eric")
st.title("Popular Recipe Analysis")
# Set subject of the page
st.write("Following the request from the Health Ministry Agency, we need to know if the most popular recipes have a nutritional score at the recommended level")

# Set Part I (Interaction dataset analysis)
st.header("Part I")
st.subheader("1 Dataset analysis")
st.subheader("1.1 Interactions Dataset")
# Interaction dataset description
st.write("In this dataset, there are five attributs "
         "\n- user_id attribut : a unique ID for each contributor. The same ID is used in the Recipe dataset to indicate who posted the recipe"
         "\n- recipe_id attribut : ID of the evaluated recipe"
         "\n- date attribut : date of the recipe evaluation"
         "\n- rating attribut : level of the evaluation from 1 to 5. 5 is the best evaluation"
         "\n- review attribut : comment of the evaluation")
st.write("Example for the 5 fist lines")
st.dataframe(interaction_data.head())

# Determination of the number of evaluated recipes
nb_recette_notees = interaction_data["recipe_id"].nunique()
nb_recette_recipe = recipes["id"].count()
st.write(f"The number of evaluated recipes : {nb_recette_notees} is identical to the number of recipes in the recipes dataset : {nb_recette_recipe}."
         "\n With others words, all recipes are evaluated at least one time."
         " We will see later, for the recipe with only one evaluation, it is a self evaluation")

# Analysis of the attribut : Rating to determine the popularity
st.subheader("1.2 Rating of recipes")
st.write("With each evaluation, a rating from 1 to 5 is done. We built an histogram of the ratings to determine their distribution.")
# Histogram of recipe ratings
histogram(interaction_data, "rating", "Number per rating", 5)
# comment of recipe ratings
st.write("We can see that the majority of the ratings are at level 5. This criterion is not a discriminating criterion for determining the popularity of a recipe.")

# Analysis of the number of evaluation to determine the popularity
st.subheader("1.3 Number of evaluation per recipe")
st.write("In the next, we will determine the popularity by the number of evaluations per recipe."
         "\n We will focus on the recipes that received more than 10 evaluations.")
# Built of a dataset with the number of evalution by recipe
evaluated_recipes = interaction_data["recipe_id"].value_counts().reset_index()
evaluated_recipes.columns = ["recipe_id", "n_evaluated"]

evaluated_recipes_sup_10 = evaluated_recipes[evaluated_recipes["n_evaluated"] > 10]
#st.dataframe(evaluated_recipes.describe())
histogram(evaluated_recipes_sup_10, "n_evaluated", "Distribution for the recipes with more than 10 evaluations", 30)
st.write(f"The median of the number of evaluations is at {evaluated_recipes_sup_10["n_evaluated"].median()}"
         f"\n for the {evaluated_recipes["n_evaluated"].count()} recipes with more than 10 evaluations.")
#st.dataframe(evaluated_recipes_sup_10.describe())

#st.dataframe(evaluated_recipes.nlargest(10, "n_evaluated"))

#nb_notation_threshold = 200
#nb_high_scoring = (evaluated_recipes["n_evaluated"] > nb_notation_threshold).sum()

#st.write(f"Nombre de recettes notées plus de {nb_notation_threshold} fois : {nb_high_scoring}")

nb_most_popular = 200
#popular_recipes = evaluated_recipes[evaluated_recipes["n_evaluated"] > nb_notation_threshold]
popular_recipes = evaluated_recipes.nlargest(nb_most_popular, "n_evaluated")

histogram(popular_recipes, "n_evaluated", f"Distribution of evaluations for the {nb_most_popular} most popular recipes", 30)

#evaluated_recipes_sup_1 = evaluated_recipes[evaluated_recipes["n_evaluated"] > 1]
evaluated_recipes_equal_1 = evaluated_recipes[evaluated_recipes["n_evaluated"] == 1]
#st.write(f"Number of recipes having more than one evaluation : {len(evaluated_recipes_sup_10)}")
#st.write(f"Number of recipes having only one evaluation : {len(evaluated_recipes_equal_1)}")
#histogram(evaluated_recipes_sup_10, "n_evaluated", "Distribution of evaluations", 30)

popular_recipes_merged = pd.merge(recipes, popular_recipes, left_on="id", right_on="recipe_id")
#st.dataframe(popular_recipes_merged.describe())
#st.dataframe(popular_recipes_merged.head())


# Les 2 bases complètes mergées
recipes_evaluation_merged = pd.merge(recipes, evaluated_recipes, left_on="id", right_on="recipe_id")

evaluated_recipes_sup_10 = recipes_evaluation_merged[recipes_evaluation_merged["n_evaluated"] > 10]
#evaluated_recipes_equal_1 = recipes_evaluation_merged[recipes_evaluation_merged["n_evaluated"] == 1]
#st.write(f"Number of recipes having more than one evaluation : {len(evaluated_recipes_sup_1)}")
#st.write(f"Number of recipes having only one evaluation : {len(evaluated_recipes_equal_1)}")
#histogram(evaluated_recipes_sup_1, "n_evaluated", "Distribution of evaluations", 30)
#st.dataframe(evaluated_recipes_sup_1.describe())
#st.dataframe(evaluated_recipes_sup_1.head())
#diff = evaluated_recipes_equal_1[evaluated_recipes_equal_1["contributor_id"] != evaluated_recipes_equal_1["user_id"]]
#st.write(f"Number of recipes having a different user evaluation : {len(diff)}")

# Créer le scatter plot
plt.figure(figsize=(8, 5))

fig, ax = plt.subplots()
ax.scatter(evaluated_recipes_sup_10["n_evaluated"], evaluated_recipes_sup_10["calories"], color="grey")
ax.scatter(evaluated_recipes_sup_10["n_evaluated"], evaluated_recipes_sup_10["calories"], color="teal")
ax.set_xlabel("Number of evaluations")
ax.set_ylabel("Calories")
ax.set_title("Relationship between number of evaluations and calories")
ax.grid(True)
#st.pyplot(fig)

#Sans les x recettes les plus calorifiques

#recipes_evaluation_merged_cleaned = recipes_evaluation_merged.drop(recipes_evaluation_merged.nlargest(100, "calories").index)
recipes_evaluation_merged_cleaned = evaluated_recipes_sup_10.drop(evaluated_recipes_sup_10[evaluated_recipes_sup_10["calories"] > 3000].index)

#plt.figure(figsize=(8, 5))
fig2, ax2 = plt.subplots()
ax2.scatter(recipes_evaluation_merged_cleaned["n_evaluated"], recipes_evaluation_merged_cleaned["calories"], color="grey", label="most popular")
ax2.scatter(popular_recipes_merged["n_evaluated"], popular_recipes_merged["calories"], color="teal", label="all")
ax2.set_xlabel("Number of evaluations")
ax2.set_ylabel("Calories")
ax2.set_title("Relationship between number of evaluations and calories")
ax2.grid(True)
st.pyplot(fig2)

plt.figure(figsize=(12, 8))
dot_size = 10
fig3, ax3 = plt.subplots()
#ax3.scatter(recipes_evaluation_merged_cleaned["n_evaluated"], recipes_evaluation_merged_cleaned["calories"], s=dot_size, color="teal", label="Calories")
ax3.scatter(popular_recipes_merged["n_evaluated"], popular_recipes_merged["sugar"], s=dot_size, color="red", alpha=0.7, label="Sugar")
ax3.scatter(popular_recipes_merged["n_evaluated"], popular_recipes_merged["total fat"], s=dot_size, alpha=0.5, label="Fat")
ax3.scatter(popular_recipes_merged["n_evaluated"], popular_recipes_merged["saturated fat"], s=dot_size, alpha=0.3, label="Saturated Fat")
ax3.set_xlabel("Number of evaluations")
ax3.set_ylabel("in grams")
ax3.set_title(f"Relationship between number of evaluations and sugar, fat for the {nb_most_popular} most popular recipes")
ax3.grid(True)
ax3.legend()
st.pyplot(fig3)

#plt.figure(figsize=(8, 5))
fig4, ax4 = plt.subplots()
#ax4.scatter(recipes_evaluation_merged_cleaned["n_evaluated"], recipes_evaluation_merged_cleaned["calories"], s=dot_size, color="teal", label="Calories")
ax4.scatter(recipes_evaluation_merged_cleaned["n_evaluated"], recipes_evaluation_merged_cleaned["sugar"], s=dot_size, color="red", alpha=0.7, label="Sugar")
ax4.scatter(recipes_evaluation_merged_cleaned["n_evaluated"], recipes_evaluation_merged_cleaned["total fat"], s=dot_size, alpha=0.5, label="Fat")
ax4.scatter(recipes_evaluation_merged_cleaned["n_evaluated"], recipes_evaluation_merged_cleaned["saturated fat"], s=dot_size, alpha=0.3, label="Saturated Fat")
ax4.set_xlabel("Number of evaluations")
ax4.set_ylabel("in grams")
ax4.set_title(f"Relationship between number of evaluations and sugar, fat for the all recipes")
ax4.grid(True)
ax4.legend()
st.pyplot(fig4)
