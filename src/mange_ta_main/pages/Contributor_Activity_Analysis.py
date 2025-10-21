# ==========================================================
#               📊 CONTRIBUTOR ANALYSIS
# ==========================================================
import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler


# ==========================================================
#             DATA LOADING
# ==========================================================
@st.cache_data
def load_data():
    """Load local data from the Data/ folder"""
    return pd.read_pickle("Data/RAW_recipes_local.pkl")

df_recipes = load_data()


# ==========================================================
#                    PAGE CONFIGURATION
# ==========================================================
st.set_page_config(
    page_title="Contributor Analysis",
    page_icon="📊",
    layout="wide",
)

st.title("📊 Summary: Contributor Behavior and Temporal Analysis")
st.markdown("""
This page presents a **temporal and behavioral analysis** of contributors:
- Identification of *top contributors* (P99)
- Grouping of temporal trajectories via **clustering**
- Detection of the **super core** of highly active contributors

The goal is to determine the **small fraction of contributors** who drive most of the platform’s activity, 
allowing targeted interventions for maximum impact in a public health context.
""")


# ==========================================================
#                 PART 1: LORENZ CURVE
# ==========================================================
st.subheader("1️⃣ Contribution Concentration — Lorenz Curve")

nb_recipes_contributor = df_recipes['contributor_id'].value_counts()
total_recipes = nb_recipes_contributor.sum()
total_contributors = nb_recipes_contributor.size

k_top = max(1, int(np.floor(0.10 * total_contributors)))
share_top10 = nb_recipes_contributor.sort_values(ascending=False).head(k_top).sum() / total_recipes

# Lorenz curve
counts_sorted = np.sort(nb_recipes_contributor.values)
cum_recipes = np.cumsum(counts_sorted) / counts_sorted.sum()
cum_contributors = np.arange(1, len(counts_sorted) + 1) / len(counts_sorted)
lorenz_x = np.insert(cum_contributors, 0, 0)
lorenz_y = np.insert(cum_recipes, 0, 0)

col1, col2, col3 = st.columns(3)
col1.metric("Number of contributors", f"{total_contributors:,}".replace(",", " "))
col2.metric("Number of recipes", f"{total_recipes:,}".replace(",", " "))
col3.metric("Share of recipes (Top 10%)", f"{share_top10*100:.1f}%")

fig, ax = plt.subplots(figsize=(7, 5))
ax.plot(lorenz_x, lorenz_y, linewidth=2)
ax.plot([0, 1], [0, 1], linestyle="--")
ax.set_xlabel("Cumulative share of contributors")
ax.set_ylabel("Cumulative share of recipes")
ax.set_title("Lorenz Curve — Contribution Inequality")
ax.grid(True, alpha=0.3)
st.pyplot(fig)

st.markdown(f"""
**Analysis:**
- The blue curve shows the **actual distribution of contributions**, while the diagonal line represents **perfect equality**.  
- The further the Lorenz curve deviates from the diagonal, the stronger the concentration.  
- Here, **10% of contributors produce about 70% of the recipes**.  
  This highly active subset forms the focus of the next analysis.
""")


# ==========================================================
#                 PART 2: CLUSTERING & SUPER CORE
# ==========================================================

def build_activity_matrix(df, freq="M"):
    df = df.copy()
    df["submitted"] = pd.to_datetime(df["submitted"], errors="coerce")
    df["month"] = df["submitted"].dt.to_period(freq).dt.to_timestamp()
    return (
        df.groupby(["contributor_id", "month"])["id"]
          .nunique()
          .unstack(fill_value=0)
          .sort_index(axis=1)
    )


def filter_top_contributors(df, top_n=277):
    top_authors = (
        df.groupby("contributor_id")["id"]
          .nunique()
          .sort_values(ascending=False)
          .head(top_n)
          .index
    )
    return df[df["contributor_id"].isin(top_authors)]


def prepare_activity_data(df, top_n=277):
    df_top = filter_top_contributors(df, top_n)
    return build_activity_matrix(df_top)


def perform_activity_clustering(activity, n_clusters=3, window=3, random_state=42):
    smoothed = activity.rolling(window=window, axis=1, min_periods=1).mean()
    X = MinMaxScaler().fit_transform(smoothed)

    km = KMeans(n_clusters=n_clusters, random_state=random_state)
    labels = km.fit_predict(X)

    activity_clustered = activity.copy()
    activity_clustered["cluster"] = labels
    return activity_clustered, km, len(set(labels))


def compute_super_core_metrics(activity, cutoff="2013-01-01", active_window=("2008-01-01", "2014-12-31")):
    START, END = pd.Timestamp(active_window[0]), pd.Timestamp(active_window[1])
    CUTOFF = pd.Timestamp(cutoff)

    total_recipes = activity.sum(axis=1)
    active_months = activity.loc[:, (activity.columns >= START) & (activity.columns <= END)].gt(0).sum(axis=1)

    last_pub = activity.apply(lambda row: row[row > 0].index.max() if (row > 0).any() else pd.NaT, axis=1)
    late_cols = [c for c in activity.columns if c >= CUTOFF]
    late_share = activity[late_cols].sum(axis=1) / total_recipes.replace(0, np.nan)

    return pd.DataFrame({
        "total_recipes": total_recipes,
        "active_months": active_months,
        "last_pub": last_pub,
        "late_share": late_share.fillna(0)
    })


def identify_super_core(df_recipes,
                        activity_clustered,
                        activity_matrix=None,
                        cutoff="2013-01-01",
                        active_window=("2008-01-01", "2014-12-31"),
                        min_active_months=6,
                        percentile_min_recipes=0.90,
                        min_late_share=0.30):
    if activity_matrix is None:
        activity_matrix = activity_clustered.drop(columns=["cluster"])

    metrics = compute_super_core_metrics(activity_matrix, cutoff, active_window)
    min_recipes = np.nanpercentile(metrics["total_recipes"], percentile_min_recipes * 100)

    mask = (
        (metrics["last_pub"] >= pd.Timestamp(cutoff))
        & (metrics["active_months"] >= min_active_months)
        & (metrics["total_recipes"] >= min_recipes)
        & (metrics["late_share"] >= min_late_share)
    )

    super_core = metrics.index[mask].tolist()
    super_core_reg = metrics.index[mask & (metrics["active_months"] >= 12)].tolist()
    pct_inactive = float((metrics["last_pub"] < pd.Timestamp(cutoff)).mean())

    df_super = df_recipes[df_recipes["contributor_id"].isin(super_core)]

    return {
        "super_core": super_core,
        "super_core_reg": super_core_reg,
        "pct_inactive": pct_inactive,
        "df_super_core": df_super,
        "metrics": metrics,
        "thresholds": {
            "min_recipes": int(min_recipes),
            "min_active_months": min_active_months,
            "min_late_share": min_late_share
        }
    }


def summarize_temporal_clustering(df_recipes, top_n=277, n_clusters=3):
    df = df_recipes.copy()
    df["submitted"] = pd.to_datetime(df["submitted"], errors="coerce")
    df = df.sort_values("submitted")

    activity = prepare_activity_data(df, top_n)
    activity_clustered, model, n_clusters_found = perform_activity_clustering(activity, n_clusters)
    super_core_info = identify_super_core(df, activity_clustered, activity_matrix=activity)

    n_recipes_sc = df[df["contributor_id"].isin(super_core_info["super_core"])].shape[0]
    share_sc = n_recipes_sc / df.shape[0] if df.shape[0] > 0 else 0

    return {
        "activity_matrix": activity,
        "activity_clustered": activity_clustered,
        "cluster_model": model,
        "n_clusters": n_clusters_found,
        "super_core_info": super_core_info,
        "super_core_recipe_share": share_sc
    }


# ==========================================================
#               PIPELINE EXECUTION
# ==========================================================
with st.spinner("Computing activity clusters..."):
    results = summarize_temporal_clustering(df_recipes)

activity = results["activity_clustered"]
model = results["cluster_model"]
super_core_info = results["super_core_info"]
super_core_share = results["super_core_recipe_share"]

# ==========================================================
#               CLUSTER VISUALIZATION
# ==========================================================
st.subheader("2️⃣ Average Normalized Activity Over Time")

activity_cols = activity.columns[:-1]  # exclude cluster column
fig, ax = plt.subplots(figsize=(10, 5))
for c in range(results["n_clusters"]):
    ax.plot(activity_cols, model.cluster_centers_[c], label=f"Cluster {c}")
ax.set_title("Average Normalized Activity Evolution (per cluster)")
ax.set_xlabel("Month")
ax.set_ylabel("Normalized Activity Index (0–1)")
ax.legend()
ax.grid(alpha=0.3)
st.pyplot(fig)


# ==========================================================
#               SUPER CORE ANALYSIS
# ==========================================================
st.header("Super Core Contributor Analysis")

"""
The normalized activity index represents each contributor’s relative participation dynamics — 
it indicates how much their activity at a given time deviates from their usual average.

For example, a score of +1 means a contributor is publishing roughly one standard deviation 
above their normal level — a significant increase in output. Conversely, −1 indicates lower-than-average activity.

By linking this index to actual recipe counts, each variation can be interpreted 
as a tangible change in contributions (e.g., from 5 to 8 recipes per month for +1.5).

Thus, these activity curves are not abstract measures: 
they reflect real shifts in platform participation.

Cluster selection: an initial 4-cluster test showed one inactive cluster, so we kept 3.  
Temporal analysis reveals that the platform’s peak occurred between 2002–2015, 
with two dominant groups of contributors: early (2002–2008) and later (2008–2015).
"""
