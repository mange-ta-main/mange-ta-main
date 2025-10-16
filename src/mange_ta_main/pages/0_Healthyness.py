import streamlit as st
from utils.data_loader import load_data
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use("Agg")
import seaborn as sns
from utils.sidebar import kaggle_link
import os
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from collections import Counter
from adjustText import adjust_text

# Page configuration
st.set_page_config(page_title="Qualitative analysis of recipes")

# Sidebar customization
kaggle_link()
image_path = os.path.join(os.path.dirname(__file__), "..", "assets", "camembear.png")
st.sidebar.image(image_path, width="stretch")

@st.cache_data
def preprocess_data():
    df_recipes, df_interactions = load_data()
    df_recipes["Calories_pdv"] = (df_recipes["Calories"] / 2000) * 100  # convert absolute value to PDV

    numeric_cols = df_recipes.select_dtypes(include=["number"]).columns
    for col in numeric_cols:
        lower = df_recipes[col].quantile(0.01)
        upper = df_recipes[col].quantile(0.99)
        df_recipes = df_recipes[
            (df_recipes[col] >= lower) &
            (df_recipes[col] <= upper)
        ]
    return df_recipes

df_recipes = preprocess_data()
# --- Main analysis question ---
st.title("Are the dishes proposed by the platform healthy?")

# --- First approach ---
st.markdown("""
To get an initial overview, let's visualize the distribution of each nutritional variable.  
For each one, we display a histogram of its **Percent Daily Value (PDV)**, meaning how much a single portion contributes to daily intake.

A red dashed line indicates the **recommended PDV for a meal**.  
If most recipes exceed this threshold, they likely contain excessive amounts of that nutrient.
""")

nutriments = [
    "Calories_pdv", 
    "Total fat", 
    "Sugar", 
    "Sodium", 
    "Protein", 
    "Saturated fat", 
    "Carbohydrates"
]

recommended_values = {
    "Calories_pdv": 33,
    "Total fat": 33,
    "Saturated fat": 33,
    "Sugar": 25,
    "Sodium": 25,
    "Protein": 33,
    "Carbohydrates": 33
}

selected_nutriment = st.radio(
    label="", 
    options=nutriments, 
    horizontal=True, 
    label_visibility="collapsed"
)

fig, ax = plt.subplots(figsize=(7, 4))
sns.histplot(
    df_recipes[selected_nutriment],
    bins=20,
    kde=True,
    ax=ax,
    color="skyblue",
    edgecolor="white"
)

rec_value = recommended_values[selected_nutriment]
ax.axvline(
        rec_value,
        color="red",
        linestyle="--",
        linewidth=2,
        label=f"Recommended ({rec_value} PDV)"
    )
ax.legend()
ax.set_title(f"Distribution of {selected_nutriment} (PDV per portion)", fontsize=13)
ax.set_xlabel(f"{selected_nutriment} — % Daily Value")
ax.set_ylabel("Number of recipes")
st.pyplot(fig)

# --- Clustering explanation ---
st.markdown("""
#### Problem: beverages and snacks are treated as main dishes
When analyzing the dataset globally, drinks, sauces, and snacks are mixed together with full meals.  
This biases the results since their nutritional scales are not comparable.

#### Solution: identify main dishes based on nutritional profiles
To solve this, we use the **nutritional composition** of each recipe instead of the unreliable `tags` column.  
This information, initially stored as a list of strings, was cleaned and split into seven numerical features:  
**Calories_pdv**, **Total fat**, **Sugar**, **Sodium**, **Protein**, **Saturated fat**, and **Carbohydrates**.

Each of these features expresses the **Percent Daily Value (PDV)** for one portion.  
Using these seven indicators, we apply a **K-Means clustering algorithm** to automatically group similar recipes.

Finally, we project these groups into two dimensions using **Principal Component Analysis (PCA)**,  
which maximizes variance and allows for a clear visualization of the clusters.
""")
@st.cache_data
def run_clustering(df_recipes):
    features = [
        "Calories_pdv", 
        "Total fat", 
        "Sugar", 
        "Sodium", 
        "Protein", 
        "Saturated fat", 
        "Carbohydrates"
    ]

    def clean_tags(tag_str):
        if pd.isna(tag_str):
            return []
        tag_str = tag_str.strip("[]").replace("'", "").replace('"', "")
        tags = [t.strip().lower() for t in tag_str.split(",") if t.strip()]
        ignore = {"equipment", "30-minutes-or-less", "60-minutes-or-less", "cuisine", "occasion", "low-in-something", "dietary", "time-to-make", "course", "main-ingredient", "preparation", "easy", "number-of-servings"}
        tags = [t for t in tags if t not in ignore]
        return tags

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
    summaries = []
    for cluster_id, group in df.groupby("cluster"):
        tags_flat = []
        for tags in group["clean_tags"].dropna():
            for t in tags:
                tags_flat.append(t)
        common_tags = [t for t, _ in Counter(tags_flat).most_common(top_n)]
        mean_x = group["PC1"].mean()
        mean_y = group["PC2"].mean()
        summaries.append({
            "cluster": cluster_id,
            "tags": ", ".join(common_tags),
            "x": mean_x,
            "y": mean_y
        })
    return pd.DataFrame(summaries)

# --- Load and process data ---
df_recipes = preprocess_data()
df_recipes, cluster_profiles = run_clustering(df_recipes)
tag_summary = compute_tag_summary(df_recipes, top_n=3)

# --- PCA visualization ---
fig, ax = plt.subplots(figsize=(8, 6))
sns.scatterplot(
    data=df_recipes,
    x="PC1", y="PC2",
    hue="cluster",
    palette="tab10",
    alpha=0.7
)
texts = []
for _, row in tag_summary.iterrows():
    texts.append(ax.text(
        row["x"], row["y"],
        f"{row['tags']}",
        fontsize=9,
        ha="center", va="center",
        bbox=dict(facecolor="white", alpha=0.6, edgecolor="none", boxstyle="round,pad=0.3")
    ))
adjust_text(
    texts,  
    only_move={'points': 'y', 'text': 'xy'},
    expand_points=(1.2, 1.4),
    expand_text=(1.2, 1.4),
    arrowprops=dict(arrowstyle="->", color="gray", lw=0.7)
)
ax.set_title("Clustering of recipes based on nutritional profiles")

st.pyplot(fig)
# --- Consistent palette for PCA and summary table ---
cluster_palette = sns.color_palette("tab10", n_colors=len(df_recipes["cluster"].unique()))
palette_dict = {i: cluster_palette[i] for i in range(len(cluster_palette))}

# --- Automatic cluster summary ---
st.markdown("### Cluster summary — Interpreting the recipe categories")

st.markdown("""
Each cluster gathers recipes with similar nutritional patterns.  
By analyzing their most frequent tags and average nutrition values, we can interpret each cluster as a general recipe category:
main meals, desserts, drinks, snacks, or sauces.

This step helps filter out recipes that are not actual main dishes, making the following analyses more relevant.
""")

cluster_summary = cluster_profiles.copy()
cluster_summary["top_tags"] = tag_summary.set_index("cluster")["tags"]
cluster_summary = cluster_summary.reset_index()

def categorize_cluster(tags):
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

cluster_summary["category"] = cluster_summary["top_tags"].apply(categorize_cluster)
cols = ["cluster", "category", "top_tags"] + [c for c in cluster_profiles.columns if c != "cluster"]

def cluster_color(cluster_id):
    rgb = tuple(int(255 * c) for c in palette_dict[cluster_id])
    return f"background-color: rgb({rgb[0]}, {rgb[1]}, {rgb[2]}); color: white;"

st.dataframe(
    cluster_summary[cols]
        .style
        .apply(lambda s: [cluster_color(v) if s.name == "cluster" else "" for v in s], axis=0)
)
