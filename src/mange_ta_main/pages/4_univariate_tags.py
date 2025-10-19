import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
from utils.data_loader import load_data
from utils.logger import get_logger

st.header('Tags')
title = 'Tags'
logger = get_logger()


# class TagsController:
#     _column = 'tags'
#
#     def __init__(self, recipes: pd.DataFrame):
#         self.recipes = recipes
#         self.tags_series = self._process_tags()


def get_tags_series() -> pd.Series:
    recipes, _ = load_data()
    series = recipes.set_index('id')['tags']\
        .dropna()\
        .apply(lambda x: x[1:-1].split(','))
    return series

@st.cache_data
def get_tags_exploded_series() -> pd.Series:
    series = get_tags_series()
    series = series.explode().str.strip().str[1:-1].str.strip() # removing the ''
    return series

def get_tags_counts_paginated(
    items_per_page: int,
    page_number: int
) -> tuple[pd.Series, int, int, int]:
    series = get_tags_exploded_series()
    series = series.value_counts()

    total_items = series.shape[0]
    total_pages = (total_items + items_per_page - 1) // items_per_page
    
    start_idx = (page_number - 1) * items_per_page
    end_idx = min(start_idx + items_per_page, total_items)
    
    # Get the subset of data for current page
    return series.iloc[start_idx:end_idx], start_idx, end_idx, total_pages

def cluster_tags():
    series = get_tags_exploded_series()
   
    # series[series[series == '60-minutes-or-less'].index]

    # [series == '30-minutes-or-less']

    unique_tags = series.unique()
    cooccurence_matrix = np.zeros((len(unique_tags), len(unique_tags)))

    cooccurence_df = pd.DataFrame(cooccurence_matrix, index=unique_tags, columns=unique_tags)

    # cooccurence_df.loc['low-sodium'][['course', 'cuisine']] += 1
    # cooccurence_df.loc['low-sodium']

    logger.info(f'matrix shape: {cooccurence_matrix.shape}')
    logger.info('computing Tag co-occurence matrix')
    for idx, tag in enumerate(unique_tags):
        recipes_with_tag = series[series == tag]
        tags_for_recipes = series[recipes_with_tag.index]

        unique_tags = tags_for_recipes.unique()
        tag_counts = tags_for_recipes.value_counts()
        # logger.info(f'Processing tag: {idx} - {tag} with {len(recipes_with_tag)} recipes and {len(tags_for_recipes)} sibling tags')
        cooccurence_df.loc[tag, unique_tags] = tag_counts

    logger.info('Tag co-occurence matrix computed')
    cooccurence_df.to_csv('tags_coocurence.csv')
    cooccurence_df


def set_page_number(page_number: int):
    st.session_state.page_number = page_number

def shift_page_number(by: int):
    st.session_state.page_number += by

def render_tags_bar_chart():
    # Initialize session state for page number if not exists
    if 'page_number' not in st.session_state:
        logger.info('Initializing page number in session state')
        st.session_state.page_number = 1
  

    current_page_data, start_idx, end_idx, total_pages = get_tags_counts_paginated(
        items_per_page=10,
        page_number=st.session_state.page_number)

    logger.info(f'current page {st.session_state.page_number}')
    # Create navigation controls
    col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])

    with col1:
        st.button(
            "⏮️ First",
            disabled=(st.session_state.page_number == 1),
            on_click=lambda: set_page_number(1))
    
    with col2:
        st.button(
            "◀️ Previous",
            disabled=(st.session_state.page_number == 1),
            on_click=lambda: shift_page_number(-1))
    
    with col3:
        st.markdown(f"<h4 style='text-align: center'>Page {st.session_state.page_number} of {total_pages}</h4>", 
                   unsafe_allow_html=True)
    
    with col4:
        st.button(
            "Next ▶️",
            disabled=(st.session_state.page_number == total_pages),
            on_click=lambda: shift_page_number(1))
    
    with col5:
        st.button(
            "Last ⏭️",
            disabled=(st.session_state.page_number == total_pages),
            on_click=lambda: set_page_number(total_pages))
    
    # # Alternative: Use a slider for navigation
    st.slider(
        "Or use slider to navigate:",
        min_value=1,
        max_value=total_pages,
        value=st.session_state.page_number,
        key='page_slider',
        on_change=lambda: set_page_number(st.session_state.page_slider))


    # Create the bar chart using plotly
    fig = px.bar(
        x=current_page_data.index,
        y=current_page_data.values,
        # orientation='h',
        title=f"{title} (Items {start_idx + 1}-{end_idx})",
        labels={'x': 'Count', 'y': 'Category'},
        text=current_page_data.values
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

    # NOTE: tags: low-sodium, desserts, low-carb, healthy, low-cholesterol,
    # NOTE: tags: low-chalorie, low-protein, low-saturated-fat, healthy2,
    # NOTE: tags: comfort-food, low-fat, very-low-carbs, high-protein

def render_tags_cluser():
    cluster_tags()


render_tags_bar_chart()
render_tags_cluser()


