import calendar
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import streamlit as st
from utils.data_loader import load_data
from utils.logger import logger
from assets import EATING_AT_RESTAURANT, JUNK_FOOD

st.set_page_config(page_title="Weekday frequencies", layout="wide")


# =========================================================================
# Retrieve and prepare data
# =========================================================================

df_recipes, _ = load_data()
# logger.info(f'sdfdsf {df_recipes.columns}')

# Retrieve targeted feature
feat_name = 'submitted'
df = df_recipes[[feat_name]]
df_dates = df.copy()

# Converting from strings to datetime format
df_dates["date"] = pd.to_datetime(df_dates[feat_name], errors="coerce")
df_dates = df_dates.dropna(subset=["date"])

df_dates["year"] = df_dates["date"].dt.year
years = df_dates["year"]

# Remove empty data
df_dates = df_dates.dropna()

st.subheader('''To Cook or NOT to Cook?''')
st.subheader('Are people eating more outside, *e.g.* in restaurantns, cafés, or ordering food to their homes instead of cooking?')
st.subheader('''This might look O.k. but it's **NOT!**''')
st.subheader('''When is this happening?''')

# st.columns() creates horizontal containers (columns) that divide your app’s page side by side
col1, col2, col3 = st.columns([1, 2, 1])

# ----------------------------------------
# Picture
# ----------------------------------------
# Centered image
with col2:
    st.image(EATING_AT_RESTAURANT, width = 400)
# ----------------------------------------


# ----------------------------------------
# Picture
# ----------------------------------------
with col2:
    st.image(JUNK_FOOD, width=400)
# ----------------------------------------


text_2 = ''' When you eat outside or order food to your place, you are not in control of the way food is prepared, nor the type of ingredients nor their quality.'''
st.markdown(text_2)

context_habits = '''In the last decades it's been observed that there has been a decline in the amount of submitted recipes. This is telling us something: 
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


st.subheader('''Let's find out what happend in the last years for each day of the week?''')

text_3 = ''' Thanks to the interface below you will be able to compare the frequencies for up to 3 days of the week for any year interval between [2001,2018].
Come along and dive deep into the users behaviours, help us identify at what moment would be intereseing to advertise people to eat more at home.'''
st.markdown(text_2)

st.text(" ")
st.text(" ")

# =========================================================================
# Create interactive plot
# BEGIN
# =========================================================================

all_years = sorted(df_dates["date"].dt.year.unique())
min_y, max_y = int(min(all_years)), int(max(all_years))

col1, col2 = st.columns([1, 2])
with col1:
    sel_days = st.multiselect(
        "Pick up to 3 weekdays",
        list(calendar.day_name),
        default=["Monday", "Friday"],
        max_selections=3,
        help="You can choose at most three."
    )
with col2:
    year_start, year_end = st.select_slider(
        "Year interval",
        options=list(range(min_y, max_y + 1)),
        value=(min_y, max_y),
        help="Slide to choose the start and end year."
    )



if not sel_days:
    st.info("Select at least one weekday to plot.")
    st.stop()

# --- Filter to year interval once ---
mask_years = df_dates["date"].dt.year.between(year_start, year_end)
df_window = df_dates.loc[mask_years, ["date"]].copy()

# Build a complete monthly index for the time window (to fill missing months with 0)
full_month_index = pd.date_range(f"{year_start}-01-01", f"{year_end}-12-01", freq="MS")

# --- Plot ---
fig, ax = plt.subplots(figsize=(11, 5))


for day in sel_days:
    # Filter this weekday
    m = df_window["date"].dt.day_name() == day
    d = df_window.loc[m, "date"].copy()

    
    # Build monthly counts per weekday using Period → Timestamp
    mc = (
        d.dt.to_period("M").value_counts().sort_index()
        .rename_axis("ym").reset_index(name="count")
    )
    mc["date_label"] = mc["ym"].dt.to_timestamp()

    # Keep only the needed columns to avoid Period dtype during reindex
    mc = (
    mc[["date_label", "count"]]
      .set_index("date_label")
      .reindex(full_month_index, fill_value=0)
      .reset_index()
      .rename(columns={"index": "date_label"})
    )
    
    # Reindex on full monthly index to ensure continuous line with zeros for gaps
    mc = mc.set_index("date_label").reindex(full_month_index, fill_value=0).reset_index()
    mc = mc.rename(columns={"index": "date_label"})

    ax.plot(mc["date_label"], mc["count"], linewidth=2, label=day, marker=".")


tick_step = st.selectbox(
    "Horizontal labels by a specific number of months",
    options=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
    index=2,
    help="Select how many months between x-axis labels."
)

# Formatting
ax.set_title(f"Weekday frequencies per month ({year_start}–{year_end})")
ax.set_xlabel("Time (Year–Month)")
ax.set_ylabel("Frequency")
ax.grid(True, linestyle="--", alpha=0.6)

# Nice date ticks (every 3 months, e.g. 'Jan 2003')
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=tick_step))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
for label in ax.get_xticklabels():
    label.set_rotation(45)
    label.set_horizontalalignment("right")

ax.legend(title="Weekday")

st.pyplot(fig)

# =========================================================================
# Create interactive plot
# END
# =========================================================================
