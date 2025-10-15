import streamlit as st
from utils.data_loader import load_data
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# =========================================================================
# Retrieve data
# =========================================================================
# Load data
df_recipes = pd.read_pickle("Data/RAW_recipes_local.pkl")
#df_interactions = pd.read_pickle("Data/RAW_interactions_local.pkl")        # Not used in the present analysis

# Select feature of interest
df_dates = df_recipes[["date"]]

# Converting from strings to datetime
df_dates["date"] = pd.to_datetime(df_dates["date"])

# Retrieve year, month and day
df_dates["year"] = df_dates["date"].dt.year
#df_dates["month"] = df_dates["date"].dt.month_name()       # Not used for now
#df_dates["day"] = df_dates["date"].dt.day_name()       #Not used for now

# =========================================================================
# Univariate data analysis for feature => date
# =========================================================================

# -------------------------------------------------------------------------
st.subheader('Are people eating more outside, *e.g.* in restaurantns, cafés, or ordering food to their homes instead of cooking?')
# -------------------------------------------------------------------------

intro_answer = '''This might look O.k. but it's **NOT!**'''
st.markdown(intro_answer)

# ----------------------------------------
# Picture
# ----------------------------------------
fig_1 = "src/mange_ta_main/assets/eating_at_restaurant.jpg"
st.image(fig_1, width = 400)
# ----------------------------------------


# ----------------------------------------
# Picture
# ----------------------------------------
fig_2 = "src/mange_ta_main/assets/junk_food.jpg"
st.image(fig_2, width = 400)
# ----------------------------------------

text_2 = ''' When you eat outside or order food to your place, you are not in control of the way food is prepared, nor the type of ingredients nor their quality.'''
st.markdown(text_2)


context_habits = '''In thelast decades it's been observed that thare has been a decline in the amount of submitted recipes. This is telling us something: 
May be ceratin portions of the global population cook less and less at home, therefore they go outside more often, for instance, to restaurants, to cafés or they are ordering food
to be delivered to their homes.'''

st.markdown(context_habits)

# ----------------------------------------
# Histogram | Feature: data
# ----------------------------------------
fig_year = plt.figure()
plt.hist(df_dates['year'],edgecolor='black')
plt.title("Annual frequency of recipes submissions")
plt.grid(True, linestyle='--', alpha=1)
st.pyplot(fig_year)

