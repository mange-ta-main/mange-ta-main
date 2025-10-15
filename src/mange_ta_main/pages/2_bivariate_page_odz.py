import streamlit as st
from utils.data_loader import load_data
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# =========================================================================
# Retrieve data
# =========================================================================
# Load data
df_recipes = pd.read_csv("Data/RAW_recipes.csv")
#df_interactions = pd.read_pickle("Data/RAW_interactions_local.pkl")        # Not used in the present analysis

# Select feature 1 
feature_1 = "submitted"
df_dates = df_recipes[[feature_1]]

# Converting from strings to datetime
df_dates[feature_1] = pd.to_datetime(df_dates[feature_1])

# Retrieve days
df_dates["day"] = df_dates[feature_1].dt.day_name()

# Retrieve calories
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

feature_2 = "day"
feature_3 = "Calories"

result = pd.concat([df_dates[feature_2],nutrition_split[feature_3]],axis = 1)

# ----------------------------------------
# Figure
# ----------------------------------------
fig_calories = plt.figure()
plt.scatter(result[feature_2], result[feature_3], marker="o", color="skyblue")
plt.xticks(rotation=45)
plt.ylim(-1000, 100000)
plt.grid(True, linestyle='--', alpha=1)
plt.title("Calories of recipies per day of the week")
st.pyplot(fig_calories)
