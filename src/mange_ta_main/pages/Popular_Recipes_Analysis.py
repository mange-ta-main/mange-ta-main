from pathlib import Path
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from utils.data_loader import load_data, nutrition_categories
from utils.sidebar import kaggle_link
from assets import CAMENBEAR

from utils.navbar import hide_page_navbar
from utils.navbar import nav


st.set_page_config(page_title="Populat Nutritional Score", layout="wide")

# =========================================================================
# Customed navigation bar
# =========================================================================
# Hide navigation bar based on pages file names
hide_page_navbar()
#Generate customed navigation bar
nav('Popular Recipes Analysis')

kaggle_link()
st.sidebar.image(CAMENBEAR, width="stretch")


# To draw histograms
def histogram(dataset, selected_column, title, bin_nb):
    # Histogram
    st.subheader("Histogram")
    # fig, ax = plt.subplots(figsize=(3, 2))
    # ax.hist(dataset[selected_column].dropna(), align='mid', bins=bin_nb, color='teal') #, edgecolor='black')
    # ax.set_title(title)
    # ax.set_xlabel(selected_column)
    # ax.set_ylabel("Frequence")
    fig = px.histogram(
        dataset,
        x=selected_column,
        nbins=bin_nb,
        labels={'x': selected_column, 'y': "Frequence"},
        title=title)

    st.plotly_chart(fig)

# Load data files
recipes, interaction_data = load_data()

st.title("Popular Recipes Analysis")

# Set subject of the page
st.write("Following the request from the Health Ministry Agency, we need to know if the most popular recipes have a nutritional score at the recommended level")

# Set Part I (Interaction dataset analysis)
st.header("A. Interaction dataset analysis")
st.subheader("A.1 Interactions Dataset")
# Interaction dataset description
st.markdown("""
         In this dataset, there are five attributs
         - user_id attribut : a unique ID for each contributor. The same ID is used in the Recipe dataset to indicate who posted the recipe
         - recipe_id attribut : ID of the evaluated recipe
         - date attribut : date of the recipe evaluation
         - rating attribut : level of the evaluation from 1 to 5. 5 is the best evaluation
         - review attribut : comment of the evaluation""")

st.write("Example for the 5 fist lines")
st.dataframe(interaction_data.head())

# Determination of the number of evaluated recipes# Change data extension to catch csv files and not pickle ones

# copy from utils file and change pickle to csv to keep the load_data() function
nb_recette_notees = interaction_data["recipe_id"].nunique()
nb_recette_recipe = recipes["id"].count()
st.markdown(f"""The number of evaluated recipes : {nb_recette_notees} is identical to the number of recipes in the recipes dataset : {nb_recette_recipe}.
        With others words, all recipes are evaluated at least one time.
        We will see later, for the recipe with only one evaluation, it is a self evaluation""")

# Analysis of the attribut : Rating to determine the popularity
st.subheader("A.2 Rating of recipes")
st.write("With each evaluation, a rating from 1 to 5 is done. We built an histogram of the ratings to determine their distribution.")
# Histogram of recipe ratings
histogram(interaction_data, "rating", "Number per rating", 5)
# comment of recipe ratings
st.write("We can see that the majority of the ratings are at level 5. This criterion is not a discriminating criterion for determining the popularity of a recipe.")

# Analysis of the number of evaluation to determine the popularity
st.subheader("A.3 Number of evaluation per recipe")
st.write("In the next, we will determine the popularity by the number of evaluations per recipe."
         "\n We will focus on the recipes that received more than 10 evaluations.")
# Built of a dataset with the number of evalution by recipe
evaluated_recipes = interaction_data["recipe_id"].value_counts().reset_index()
evaluated_recipes.columns = ["recipe_id", "n_evaluated"]

evaluated_recipes_sup_10 = evaluated_recipes[evaluated_recipes["n_evaluated"] > 10]
histogram(evaluated_recipes_sup_10, "n_evaluated", "Distribution for the recipes with more than 10 evaluations", 30)
st.write(f"The median of the number of evaluations is at {evaluated_recipes_sup_10["n_evaluated"].median()}"
         f"\n for the {evaluated_recipes["n_evaluated"].count()} recipes with more than 10 evaluations.")

st.subheader("A.4 Number of evaluation per recipe")
nb_most_popular = 200
popular_recipes = evaluated_recipes.nlargest(nb_most_popular, "n_evaluated")
histogram(popular_recipes, "n_evaluated", f"Distribution of evaluations for the {nb_most_popular} most popular recipes", 30)
st.write(f"For this study, we selected {nb_most_popular} the number of the most popular recipes."
         f" The number of evaluations for the {nb_most_popular}th most popular recipe is {popular_recipes["n_evaluated"].min()} evaluations.")

st.header("B. Relationship between popularity and nutritional values")
st.write("Select the nutritional parameter on the left"
         "\nMove cursors to zoom")

popular_recipes_merged = pd.merge(recipes, popular_recipes, left_on="id", right_on="recipe_id")

# Merge of the both full dataset
recipes_evaluation_merged = pd.merge(recipes, evaluated_recipes, left_on="id", right_on="recipe_id")
# Dataset with only the number of evaluations higher than 10
evaluated_recipes_sup_10 = recipes_evaluation_merged[recipes_evaluation_merged["n_evaluated"] > 10]
# Cleaning recipes with a number of calories higher than 10000
recipes_evaluation_merged_cleaned = evaluated_recipes_sup_10.drop(evaluated_recipes_sup_10[evaluated_recipes_sup_10["Calories"] > 10000].index)
# List of nutritional parameters
# Define limits for the x cursors
min_val = int(recipes_evaluation_merged_cleaned["n_evaluated"].min())
max_val = int(recipes_evaluation_merged_cleaned["n_evaluated"].max())
dot_size = 10
col1, col2 = st.columns([1, 5])
with col1:
    selected_column = st.radio("Choice one nutrition parameter", nutrition_categories)
    # Cursors for x axis
    selected_x = st.slider("Number of evaluations :", min_value=min_val, max_value=max_val, value=(min_val, max_val))
    
with col2:
    # Define limits for the y cursor
    max_val = int(recipes_evaluation_merged_cleaned[selected_column].max())
    # Cursor for y axis
    y_max_value = st.slider(selected_column, 0, max_val, value=max_val)

    # Plot nutritional parameter versus nb of evaluations
    fig5 = go.Figure()
    # Plot all recipes evaluations
    fig5.add_trace(go.Scatter(
        x=recipes_evaluation_merged_cleaned["n_evaluated"],
        y=recipes_evaluation_merged_cleaned[selected_column],
        mode='markers',
        marker=dict(color='orange', size=dot_size, opacity=0.3),
        name=selected_column
    ))
    # Plot the most popular recipes
    fig5.add_trace(go.Scatter(
        x=popular_recipes_merged["n_evaluated"],
        y=popular_recipes_merged[selected_column],
        mode='markers',
        marker=dict(color='teal', size=dot_size),
        name='most popular'
    ))
    #graph update
    fig5.update_layout(
        title=f"Relationship between number of evaluations and {selected_column} for the all recipes",
        xaxis_title="Number of evaluations",
        yaxis_title=selected_column,
        xaxis=dict(range=selected_x, showgrid=True),
        yaxis=dict(range=[0, y_max_value], showgrid=True),
        legend_title="Legend"
    )
    st.plotly_chart(fig5)    
    
    
st.header("C. Conclusion")
st.write("In conclusion, all the most popular recipes have a good nutritional quality."
         "\nIt seems that the number of evaluations can be a parameter to find a good recipe.")