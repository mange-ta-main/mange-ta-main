from collections import Counter

import streamlit as st
import pandas as pd
import matplotlib
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import plotly.express as px

from utils.sidebar import kaggle_link
from utils.data_loader import load_data
from utils.logger import logger
from assets import CAMENBEAR

from utils.navbar import hide_page_navbar
from utils.navbar import nav

# -------------------------------------------------
# Customed navigation bar
# -------------------------------------------------
# Hide navigation bar based on pages file names
hide_page_navbar()
# Generate customed navigation bar
nav('Healthyness')



matplotlib.use("Agg")

# Page configuration
st.set_page_config(page_title="Healthyness")

# Sidebar customization
kaggle_link()
st.sidebar.image(CAMENBEAR, width="stretch")

logger.info("Starting healthiness analysis page...")


@st.cache_data
def preprocess_data() -> pd.DataFrame:
    """Load and preprocess recipe data with outlier removal."""
    logger.info("Preprocessing nutritional data...")
    df_recipes, df_interactions = load_data()
    df_recipes["Calories"] = (df_recipes["Calories"] / 2000) * 100

    numeric_cols = df_recipes.select_dtypes(include=["number"]).columns
    for col in numeric_cols:
        lower = df_recipes[col].quantile(0.01)
        upper = df_recipes[col].quantile(0.99)
        df_recipes = df_recipes[
            (df_recipes[col] >= lower) & (df_recipes[col] <= upper)
        ]
    return df_recipes


df_recipes = preprocess_data()
THRESHOLD = 33

st.title("Are the meals proposed by the platform healthy?")

st.markdown("""
We visualize the distribution of each nutritional variable to identify how many recipes
fall above or below 33% of the recommended daily intake, assuming three meals per day.

**Color coding:** Dark blue indicates recipes providing less than 33% of the daily value,
while light blue represents those providing more than 33%.

**Data processing:** The original data was converted into seven numerical features and
outliers (below 1st percentile and above 99th percentile) were removed.
""")
st.markdown("<br>", unsafe_allow_html=True)
NUTRIENTS = [
    "Calories",
    "Total fat",
    "Sugar",
    "Sodium",
    "Protein",
    "Saturated fat",
    "Carbohydrates",
]

summary = {
    n: {
        "≤ 33% of PDV": (df_recipes[n] <= THRESHOLD).sum(),
        "> 33% of PDV": (df_recipes[n] > THRESHOLD).sum(),
    }
    for n in NUTRIENTS
}

st.markdown("### Distribution of recipes by nutrient category")
df_summary = pd.DataFrame(summary).T

df_melt = df_summary.reset_index().melt(
    id_vars="index",
    var_name="Category",
    value_name="Count"
)

df_melt["Proportion"] = df_melt.groupby("index")["Count"].transform(
    lambda x: x / x.sum() * 100
)

fig = px.bar(
    df_melt,
    x="index",
    y="Proportion",
    color="Category",
    color_discrete_map={
        "≤ 33% of PDV": "#0B4F6C",
        "> 33% of PDV": "#A7C7E7",
    },
    title="Share of recipes above and below 33% of daily value per nutrient",
    labels={"index": "Nutrient", "Proportion": "Share of recipes (%)"},
)

fig.add_hline(
    y=50,
    line_dash="solid",
    line_color="red",
    annotation_text="50%",
    annotation_position="top left"
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("""
**Observation:** Most recipes appear healthy with nutrient intakes under 33%.

**Problem:** The data includes beverages and snacks that are typically sweet or salty,
biasing the healthiness analysis. We need to focus on main dishes.

**Solution:** We identify main dishes using k-means clustering (k=5) based on nutritional
composition, then visualize clusters using PCA for dimensionality reduction.
""")

st.markdown("<br>", unsafe_allow_html=True)

@st.cache_data
def run_clustering():
    """Perform k-means clustering on nutritional features and reduce to 2D with PCA."""
    features = [
        "Calories",
        "Total fat",
        "Sugar",
        "Sodium",
        "Protein",
        "Saturated fat",
        "Carbohydrates",
    ]

    def clean_tags(tag_str):
        """Extract and filter relevant tags from tag string."""
        if pd.isna(tag_str):
            return []
        tags = (tag_str.strip("[]")
                .replace("'", "")
                .replace('"', "")
                .replace(' ', '')
                .split(','))
        ignore = {
            "equipment", "30-minutes-or-less", "15-minutes-or-less",
            "60-minutes-or-less", "3-steps-or-less", "4-hours-or-less",
            "cuisine", "occasion", "low-in-something", "dietary",
            "time-to-make", "course", "main-ingredient", "preparation",
            "easy", "number-of-servings",
        }
        return [t for t in tags if t not in ignore]

    df_recipes["clean_tags"] = df_recipes["tags"].apply(clean_tags)
    X = df_recipes[features].fillna(0)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    kmeans = KMeans(n_clusters=5, random_state=42)
    df_recipes["cluster"] = kmeans.fit_predict(X_scaled)

    cluster_profiles = df_recipes.groupby("cluster")[features].mean().round(1)
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X_scaled)
    df_recipes["PC1"] = X_pca[:, 0]
    df_recipes["PC2"] = X_pca[:, 1]

    return df_recipes, cluster_profiles


@st.cache_data
def compute_tag_summary(df, top_n=3):
    """Compute most common tags and centroid coordinates for each cluster."""
    summaries = []
    for cluster_id, group in df.groupby("cluster"):
        tags_flat = [t for tags in group["clean_tags"].dropna() for t in tags]
        common_tags = [t for t, _ in Counter(tags_flat).most_common(top_n)]
        summaries.append({
            "cluster": cluster_id,
            "tags": ", ".join(common_tags),
            "x": group["PC1"].mean(),
            "y": group["PC2"].mean(),
        })
    return pd.DataFrame(summaries)


df_recipes = preprocess_data()
df_recipes, cluster_profiles = run_clustering()
tag_summary = compute_tag_summary(df_recipes, top_n=3)
fig = px.scatter(
    df_recipes,
    x="PC1",
    y="PC2",
    color=df_recipes["cluster"].astype(str),
    opacity=0.6,
    title="Clustering of recipes based on nutritional profiles",
    color_discrete_sequence=px.colors.qualitative.Plotly
)

offsets = [(40, -40), (-60, 40), (60, -20), (80, 50), (60, -20)]
for i, row in enumerate(tag_summary.iterrows()):
    _, r = row
    ax_offset, ay_offset = offsets[i % len(offsets)]
    fig.add_annotation(
        x=r["x"],
        y=r["y"],
        text=r["tags"],
        showarrow=True,
        arrowhead=2,
        ax=ax_offset,
        ay=ay_offset,
        font=dict(color="black", size=13, family="Arial"),
        bgcolor="rgba(255,255,255,0.9)",
        bordercolor="rgba(0,0,0,0.3)",
        borderwidth=0.5,
        borderpad=4
    )

fig.update_traces(marker=dict(size=5))
fig.update_layout(
    width=700,
    height=600,
    margin=dict(l=80, r=80, t=80, b=80),
    title_font=dict(size=22)
)

st.plotly_chart(fig, use_container_width=False)

st.markdown("### Cluster summary")

st.markdown("""
Each cluster groups recipes with similar nutritional patterns. By analyzing their most
frequent tags and nutritional values, we categorize them as main meals, desserts, drinks,
snacks, or sauces. This helps filter out non-main dishes for more relevant analysis.
""")

cluster_summary = cluster_profiles.copy()
cluster_summary["top_tags"] = tag_summary.set_index("cluster")["tags"]
cluster_summary = cluster_summary.reset_index()
cluster_palette = sns.color_palette(
    "tab10",
    n_colors=len(df_recipes["cluster"].unique())
)
palette_dict = {i: cluster_palette[i] for i in range(len(cluster_palette))}


def categorize_cluster(tags):
    """Categorize cluster based on tag keywords."""
    t = tags.lower()
    if any(k in t for k in ["drink", "beverage", "smoothie", "juice"]):
        return "Drink / Beverage"
    elif any(k in t for k in ["dessert", "cake", "cookie", "sweet", "fruit"]):
        return "Dessert / Sweet"
    elif any(k in t for k in ["sauce", "dip", "dressing"]):
        return "Sauce / Dressing"
    elif any(k in t for k in ["salad", "snack", "side"]):
        return "Snack / Side"
    elif any(k in t for k in ["main", "meat", "pasta", "rice", "chicken"]):
        return "Main meal / Entrée"
    else:
        return "Other"


def cluster_color(cluster_id):
    """Generate background color for cluster cell."""
    rgb = tuple(int(255 * c) for c in palette_dict[cluster_id])
    return f"background-color: rgb({rgb[0]}, {rgb[1]}, {rgb[2]}); color: white;"


cluster_summary["category"] = cluster_summary["top_tags"].apply(categorize_cluster)
cols = ["cluster", "category", "top_tags"] + [
    c for c in cluster_profiles.columns if c != "cluster"
]

st.dataframe(
    cluster_summary[cols].style.apply(
        lambda s: [cluster_color(v) if s.name == "cluster" else "" for v in s],
        axis=0
    )
)

main_dish_cols = [
    "id", "Calories", "Total fat", "Sugar", "Sodium",
    "Protein", "Saturated fat", "Carbohydrates"
]
df_main_dishes = df_recipes[
    (df_recipes["cluster"] == 1) | (df_recipes["cluster"] == 3)
][main_dish_cols]

summary = {
    n: {
        "≤ 33% of PDV": (df_main_dishes[n] <= THRESHOLD).sum(),
        "> 33% of PDV": (df_main_dishes[n] > THRESHOLD).sum(),
    }
    for n in NUTRIENTS
}

df_summary = pd.DataFrame(summary).T

df_melt = df_summary.reset_index().melt(
    id_vars="index",
    var_name="Category",
    value_name="Count"
)

df_melt["Proportion"] = df_melt.groupby("index")["Count"].transform(
    lambda x: x / x.sum() * 100
)

fig = px.bar(
    df_melt,
    x="index",
    y="Proportion",
    color="Category",
    color_discrete_map={
        "≤ 33% of PDV": "#0B4F6C",
        "> 33% of PDV": "#A7C7E7",
    },
    title="Share of main dishes above and below 33% of daily value per nutrient",
    labels={"index": "Nutrient", "Proportion": "Share of recipes (%)"},
)

fig.add_hline(
    y=50,
    line_dash="solid",
    line_color="red",
    annotation_text="50%",
    annotation_position="top left"
)

st.plotly_chart(fig)

st.markdown("### Conclusion")

st.markdown("""
The initial analysis suggested that most recipes on the platform are healthy, with all
nutrients below the 33% threshold. However, after filtering for main dishes using
clustering, the results reveal a different picture:

**Key findings:**
- **Total fat, Protein, and Saturated fat** exceed 33% PDV in most main dishes
- This indicates that main meals on the platform tend to be rich in fats and proteins
- The initial dataset was skewed by beverages, snacks, and desserts that are typically
  lower in these nutrients

**Interpretation:** While the platform offers diverse recipe types, main dishes tend to
provide substantial portions of daily fat and protein intake. Users should be mindful of
these nutritional profiles when planning balanced meals.
""")
