import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
from utils.data_loader import load_data, load_tags
from utils.logger import get_logger
from utils.navbar import hide_page_navbar
from utils.navbar import nav
from utils.sidebar import kaggle_link
from assets import CAMENBEAR


st.set_page_config(page_title="Univariate Tags", layout="wide")

# =========================================================================
# Customed navigation bar
# =========================================================================
# Hide navigation bar based on pages file names
hide_page_navbar()
# Generate customed navigation bar
nav('Univariate Tags')

kaggle_link()
st.sidebar.image(CAMENBEAR, width="stretch")


st.header("Tags")
title = "Tags"
logger = get_logger()


# class TagsController:
#     _column = 'tags'
#
#     def __init__(self, recipes: pd.DataFrame):
#         self.recipes = recipes
#         self.tags_series = self._process_tags()


def get_tags_series() -> pd.Series:
    recipes, _ = load_data()
    series = (
        recipes.set_index("id")["tags"].dropna().apply(lambda x: x[1:-1].split(","))
    )
    series = series.explode().str.strip().str[1:-1].str.strip() # removing the ''
    return series


@st.cache_data
def get_tags_exploded_series() -> pd.Series:
    series = get_tags_series()
    series = series.explode().apply(lambda x: x.strip()[1:-1].strip())
    return series


def get_tags_counts_paginated(
    items_per_page: int, page_number: int
) -> tuple[pd.Series, int, int, int]:
    series = get_tags_exploded_series()
    series = series[
        series.isin(
            {
                "low-sodium",
                "main-dish",
                "desserts",
                "low-carb",
                "healthy",
                "low-cholesterol",
                "low-chalorie",
                "low-protein",
                "low-saturated-fat",
                "healthy2",
                "comfort-food",
                "low-fat",
                "very-low-carbs",
                "high-protein",
            }
        )
    ]
    series = series.value_counts()

    total_items = series.shape[0]
    total_pages = (total_items + items_per_page - 1) // items_per_page

    start_idx = (page_number - 1) * items_per_page
    end_idx = min(start_idx + items_per_page, total_items)

    # Get the subset of data for current page
    return series.iloc[start_idx:end_idx], start_idx, end_idx, total_pages

    # Method 3: K-Means Clustering on Co-occurrence Vectors
    # def kmeans_clustering(cooccurrence_df, n_clusters=3):
    #     """
    #     Use K-Means to cluster tags based on their co-occurrence patterns
    #     """
    #     # Normalize the co-occurrence matrix
    #     normalized = cooccurrence_df.values / (cooccurrence_df.values.sum(axis=1, keepdims=True) + 1e-10)
    #
    #     # Apply K-Means
    #     kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    #     cluster_labels = kmeans.fit_predict(normalized)
    #
    #     # Create cluster dictionary
    #     tag_clusters = {}
    #     for cluster_id in range(n_clusters):
    #         cluster_tags = cooccurrence_df.index[cluster_labels == cluster_id].tolist()
    #         tag_clusters[f'Cluster_{cluster_id}'] = cluster_tags

    return cluster_labels, tag_clusters


def cluster_tags():
    tags = get_tags_exploded_series()
    _, reviews = load_data()

    logger.info(reviews.columns)


def set_page_number(page_number: int):
    st.session_state.page_number = page_number


def shift_page_number(by: int):
    st.session_state.page_number += by


def render_tags_bar_chart():
    # Initialize session state for page number if not exists
    if "page_number" not in st.session_state:
        logger.info("Initializing page number in session state")
        st.session_state.page_number = 1

    current_page_data, start_idx, end_idx, total_pages = get_tags_counts_paginated(
        items_per_page=10, page_number=st.session_state.page_number
    )
    logger.info(f"current page {st.session_state.page_number}")
    # Create navigation controls
    col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])

    with col1:
        st.button(
            "⏮️ First",
            disabled=(st.session_state.page_number == 1),
            on_click=lambda: set_page_number(1),
        )

    with col2:
        st.button(
            "◀️ Previous",
            disabled=(st.session_state.page_number == 1),
            on_click=lambda: shift_page_number(-1),
        )

    with col3:
        st.markdown(
            f"<h4 style='text-align: center'>Page {st.session_state.page_number} of {total_pages}</h4>",
            unsafe_allow_html=True,
        )

    with col4:
        st.button(
            "Next ▶️",
            disabled=(st.session_state.page_number == total_pages),
            on_click=lambda: shift_page_number(1),
        )

    with col5:
        st.button(
            "Last ⏭️",
            disabled=(st.session_state.page_number == total_pages),
            on_click=lambda: set_page_number(total_pages),
        )

    # # Alternative: Use a slider for navigation
    st.slider(
        "Or use slider to navigate:",
        min_value=1,
        max_value=total_pages,
        value=st.session_state.page_number,
        key="page_slider",
        on_change=lambda: set_page_number(st.session_state.page_slider),
    )

    # Create the bar chart using plotly
    fig = px.bar(
        x=current_page_data.index,
        y=current_page_data.values,
        # orientation='h',
        title=f"{title} (Items {start_idx + 1}-{end_idx})",
        labels={"x": "Count", "y": "Category"},
        text=current_page_data.values,
    )

    # Update layout for better appearance
    # fig.update_traces(texttemplate='%{text}', textposition='outside')
    # fig.update_layout(
    #     height=max(400, len(current_page_data) * 40),  # Dynamic height based on items
    #     showlegend=False,
    #     xaxis_title="Count",
    #     yaxis_title="Category",
    #     yaxis={'categoryorder': 'total ascending'}  # Keep order from series
    # )
    #
    # # Display the chart
    st.plotly_chart(fig)

# def render_tags_pie_chart():
#     # Create pie chart
#     series = get_tags_exploded_series()
#     series = series.value_counts()
#     fig = px.pie(values=series.values,
#                  names=series.index,
#                  title='Tags distribution')
#
#     # Display in Streamlit
#     st.plotly_chart(fig)


# render_tags_pie_chart()
    # NOTE: tags: low-sodium, desserts, low-carb, healthy, low-cholesterol,
    # NOTE: tags: low-chalorie, low-protein, low-saturated-fat, healthy2,
    # NOTE: tags: comfort-food, low-fat, very-low-carbs, high-protein

# def render_tags_pie_chart():
#     # Create pie chart
#     series = get_tags_exploded_series()
#     series = series.value_counts()
#     fig = px.pie(values=series.values,
#                  names=series.index,
#                  title='Tags distribution')
#
#     # Display in Streamlit
#     st.plotly_chart(fig)


render_tags_bar_chart()
render_tags_cluser()
