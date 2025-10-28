# ==========================================================
#          CONTRIBUTOR ANALYSIS (Simplified Interactive)
# ==========================================================
import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

from utils.data_loader import load_data
from utils.logger import logger
from utils.navbar import hide_page_navbar
from utils.navbar import nav

# -------------------------------------------------
# Customed navigation bar
# -------------------------------------------------
# Hide navigation bar based on pages file names
hide_page_navbar()
# Generate customed navigation bar
nav('Contributor Activity Analysis')



# ==========================================================
#             DATA LOADING
# ==========================================================

df_recipes, _ = load_data()


# ==========================================================
#                    PAGE CONFIGURATION
# ==========================================================
st.set_page_config(
    page_title="Contributor Analysis",
    layout="wide",
)

st.title("Summary: Contributor Behavior and Temporal Analysis")
st.markdown("""
This page presents a **temporal and behavioral analysis** of contributors:
- Identification of *top contributors* (P99)
- Grouping of temporal trajectories via **clustering**
- Detection of the **super core** of highly active contributors

The goal is to determine the **small fraction of contributors** who drive most of the platform’s activity, 
allowing targeted interventions for maximum impact in a public health context.
""")


# ==========================================================
#                SIDEBAR CONTROLS
# ==========================================================
st.sidebar.header("Clustering Parameters")

# --- Clustering parameter (only one kept) ---
n_clusters = st.sidebar.slider("Number of clusters", 2, 8, 3)


# ==========================================================
#                 PART 1: LORENZ CURVE
# ==========================================================
st.subheader("1 Contribution Concentration — Lorenz Curve")

nb_recipes_contributor = df_recipes['contributor_id'].value_counts()
total_recipes = nb_recipes_contributor.sum()
total_contributors = nb_recipes_contributor.size

# Fixed 10% threshold (no interactivity)
k_top = max(1, int(np.floor(0.10 * total_contributors)))
share_top10 = nb_recipes_contributor.sort_values(ascending=False).head(k_top).sum() / total_recipes

# Lorenz curve
counts_sorted = np.sort(nb_recipes_contributor.values)
cum_recipes = np.cumsum(counts_sorted) / counts_sorted.sum()
cum_contributors = np.arange(1, len(counts_sorted) + 1) / len(counts_sorted)

# Display metrics
col1, col2, col3 = st.columns(3)
col1.metric("Number of contributors", f"{total_contributors:,}".replace(",", " "))
col2.metric("Number of recipes", f"{total_recipes:,}".replace(",", " "))
col3.metric("Share of recipes (Top 10%)", f"{share_top10*100:.1f}%")

# Plot Lorenz
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=cum_contributors,
    y=cum_recipes,
    name="Contribution Distribution",))
fig.add_trace(go.Scatter(
    x=[0,1],
    y=[0,1],
    name="Perfect Equality",
    line={
        "color": "orange",
        "width":1,
        "dash": "dash"
    }))

fig.update_layout(
    title="Lorenz Curve — Contribution Inequality",
    xaxis_title="Cumulative share of contributors",
    yaxis_title="Cumulative share of recipes")

st.plotly_chart(fig)

st.markdown(f"""
**Analysis:**
- The blue curve shows the **actual distribution of contributions**, while the diagonal represents **perfect equality**.  
- The farther the Lorenz curve is from the diagonal, the stronger the concentration.  
- Here, **10% of contributors produce approximately {share_top10*100:.1f}% of all recipes**.  
""")


# ==========================================================
#                 PART 2: CLUSTERING & SUPER CORE
# ==========================================================

def build_activity_matrix(df: pd.DataFrame, freq="M") -> pd.DataFrame:
    df = df.copy()
    df["submitted"] = pd.to_datetime(df["submitted"], errors="coerce")
    df["month"] = df["submitted"].dt.to_period(freq).dt.to_timestamp()
    return (
        df.groupby(["contributor_id", "month"])["id"]
          .nunique()
          .unstack(fill_value=0)
          .sort_index(axis=1)
    )


def filter_top_contributors(df: pd.DataFrame, top_n=277) -> pd.DataFrame:
    top_authors = (
        df.groupby("contributor_id")["id"]
          .nunique()
          .sort_values(ascending=False)
          .head(top_n)
          .index
    )
    return df[df["contributor_id"].isin(top_authors)]


def prepare_activity_data(df: pd.DataFrame, top_n=277) -> pd.DataFrame:
    df_top = filter_top_contributors(df, top_n)
    return build_activity_matrix(df_top)


def perform_activity_clustering(activity, n_clusters=3, window=3, random_state=42):
    """Perform KMeans clustering using Z-score normalization."""
    smoothed = activity.T.rolling(window=window, min_periods=1).mean().T

    X = StandardScaler().fit_transform(smoothed)  # Z-score normalization

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


def summarize_temporal_clustering(df_recipes: pd.DataFrame, top_n=277, n_clusters=3):
    """Full pipeline: prepare data, cluster, and identify super core contributors."""

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
    results = summarize_temporal_clustering(df_recipes, n_clusters=n_clusters)

activity = results["activity_clustered"]
model = results["cluster_model"]
super_core_info = results["super_core_info"]
super_core_share = results["super_core_recipe_share"]

# ==========================================================
#               CLUSTER VISUALIZATION
# ==========================================================
st.subheader("2 Average Normalized Activity Over Time")

activity_cols = activity.columns[:-1]  # exclude cluster column
fig = go.Figure()

for c in range(results["n_clusters"]):
    fig.add_trace(
        go.Scatter(
            x=activity_cols,
            y=model.cluster_centers_[c],
            name=f"Cluster {c}")
    )

fig.update_layout(
    title="Average Normalized Activity Evolution (per cluster)",
    xaxis_title="Month",
    yaxis_title="Z-Score Activity Index")

st.plotly_chart(fig)

# ==========================================================
#               SUPER CORE ANALYSIS
# ==========================================================
st.header("Super Core Contributor Analysis")

st.subheader(" Contributor Targeting Summary and Cluster Dynamics")

"""
The Z-Score activity index represents each contributor’s relative participation dynamics — 
it shows how much their activity at a given time deviates from their own average.
"""

st.markdown("""
The analysis performed with a **4-cluster configuration** appears to be the most relevant, 
as it reveals **three well-defined groups of contributors** over time.

-  **Cluster 0 – Early Pioneers (2000–2004):** this first group emerged at the platform’s creation.  
  Their activity declined progressively after 2002 and completely faded out by 2004, 
  giving way to the next generation of contributors.  
- **Cluster 1 – Historical Core (2004–2015):** the dominant group, 
  sustaining most of the platform’s activity throughout its active lifespan.  
-  **Cluster 2 – Late Active Users (2007–2015):** a third group emerged in 2007 
  and coexisted for several years with the previous one.  
  Both clusters eventually disappeared by 2015, marking the end of significant contributor activity.

---
""")

# ==========================================================
#               CONCLUSION
# ==========================================================

st.header("Conclusion contributor Behavior and Temporal Analysis")

col1, col2, col3 = st.columns(3)
col1.metric("Contributors (P99)", "277")
col2.metric("Clusters 1 & 2 (4-cluster setup)", "38")
col3.metric("Active in last 6 months", "35")

"""
By focusing on the **two most active clusters (1 and 2)** — corresponding to the platform’s maturity phase (2007–2015):
- among the **277 contributors in the 99th percentile (P99)**, **38 major contributors** were identified;  
- applying an additional criterion of **recent activity (within the last six months)** 
  further narrows this group down to **35 key contributors**.

These 35 contributors form the **strategic core to retain, support, and guide** 
in promoting **public health objectives** and improving the **nutritional quality** of the recipes shared on the platform.

"""





