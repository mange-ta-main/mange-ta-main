import streamlit as st
from utils.data_loader import load_data
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import calendar


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
df_dates["month_num"] = df_dates["date"].dt.month
df_dates["day_num"] = df_dates["date"].dt.dayofweek
#df_dates["month"] = df_dates["date"].dt.month_name()       # Not used for now
#df_dates["day"] = df_dates["date"].dt.day_name()       #Not used for now

# Retrieve years data as series (not as a dataframe) while removing missing values
years = df_dates["year"].dropna()
months = df_dates["month_num"].dropna()
days = df_dates["day_num"].dropna()

# =========================================================================
# Univariate data analysis for feature => date
# =========================================================================

st.subheader('Are people eating more outside, *e.g.* in restaurantns, cafés, or ordering food to their homes instead of cooking?')
st.subheader('''This might look O.k. but it's **NOT!**''')
st.subheader('''When is this happening?''')

# st.columns() creates horizontal containers (columns) that divide your app’s page side by side
col1, col2, col3 = st.columns([1, 2, 1])

# ----------------------------------------
# Picture
# ----------------------------------------
fig_1 = "src/mange_ta_main/assets/eating_at_restaurant.jpg"
# Centered image
with col2:
    st.image(fig_1, width = 400)
# ----------------------------------------


# ----------------------------------------
# Picture
# ----------------------------------------
fig_2 = "src/mange_ta_main/assets/junk_food.jpg"
with col2:
    st.image(fig_2, width=400)
# ----------------------------------------

text_2 = ''' When you eat outside or order food to your place, you are not in control of the way food is prepared, nor the type of ingredients nor their quality.'''
st.markdown(text_2)

context_habits = '''In thelast decades it's been observed that thare has been a decline in the amount of submitted recipes. This is telling us something: 
May be ceratin portions of the global population cook less and less at home, therefore they go outside more often, for instance, to restaurants, to cafés or they are ordering food
to be delivered to their homes.'''
st.markdown(context_habits)

# ----------------------------------------
# Histogram | Years
# ----------------------------------------
# Compute bins so each bin belongs to a year
bins = range(int(years.min()), int(years.max()) + 2)

# Generate histogram
fig_year = plt.figure(figsize=(7,3))
plt.hist(years, bins=bins, align="left",color="paleturquoise", edgecolor="black", rwidth=0.9)

# Each horizontal axis matches a separate year
plt.xticks(range(int(years.min()), int(years.max()) + 1))
plt.tick_params(axis='x', labelrotation=70)

plt.title("Annual frequencies of recipes publications")
plt.ylabel("Frequency")
plt.xlabel("Years")
plt.grid(True, linestyle='--', alpha=1)
st.pyplot(fig_year)
# ----------------------------------------

# ----------------------------------------
# Histogram | Months
# ----------------------------------------
# Compute bins so each bin belongs to a year
bins = range(int(months.min()), int(months.max()) + 2)    # Compute bins so each bin belongs to a year

# Generate histogram
fig_month = plt.figure(figsize=(7,3))
plt.hist(months, bins=bins, align="left",color="paleturquoise", edgecolor="black", rwidth=0.9)

# Each horizontal axis matches a separate month
plt.xticks(range(int(months.min()), int(months.max()) + 1))
plt.xticks(range(1, 13), calendar.month_name[1:], rotation=90)

plt.title("Monthly frequencies of recipes publications")
plt.ylabel("Frequency")
plt.xlabel("Mothn")
plt.grid(True, linestyle='--', alpha=1)
st.pyplot(fig_month)
# ----------------------------------------


# ----------------------------------------
# Histogram | Days of the week
# ----------------------------------------
# Compute bins so each bin belongs to a year
bins = range(0,8)    # Compute bins so each bin belongs to a year

# Generate histogram
fig_days = plt.figure(figsize=(7,3))
plt.hist(days, bins=bins, align="left",color="paleturquoise", edgecolor="black", rwidth=0.9)

# Each horizontal axis matches a separate month
plt.xticks(range(0,7 + 1))
plt.xticks(range(0, 7), calendar.day_name, rotation=45)

plt.title("Daily frequencies of recipes publications 2001 - 2018")
plt.ylabel("Frequency")
plt.xlabel("Day of the week")
plt.grid(True, linestyle='--', alpha=1)
st.pyplot(fig_days)
# ----------------------------------------