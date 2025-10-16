import pandas as pd
import streamlit as st
import plotly.express as px
import logging
from utils.data_loader import load_data
from utils.logger import get_logger

st.header('Tags')
title = 'Tags'
logger = get_logger()

@st.cache_data
def get_processed_data(column: str) -> pd.Series:
    recipes, _ = load_data()
    series = recipes[column].dropna().apply(lambda x: x[1:-1].split(','))
    series = series.explode()
    series = series.value_counts()
    return series


@st.cache_data
def get_page_data(column: str, items_per_page: int, page_number: int) -> pd.Series:
    series = get_processed_data(column)

    if 'total_pages' not in st.session_state\
            or 'total_items' not in st.session_state\
            or 'items_per_page' not in st.session_state\
            or st.session_state.items_per_page != items_per_page:
        total_items = series.shape[0]
        total_pages = (total_items + items_per_page - 1) // items_per_page
        st.session_state.items_per_page = items_per_page
        st.session_state.total_pages = total_pages
        st.session_state.total_items = total_items
    else:
        total_pages = st.session_state.total_pages
        total_items = st.session_state.total_items
    
    start_idx = (page_number - 1) * items_per_page
    end_idx = min(start_idx + items_per_page, total_items)
    
    # Get the subset of data for current page
    return series.iloc[start_idx:end_idx], start_idx, end_idx


def set_page_number(page_number: int):
    st.session_state.page_number = page_number

def shift_page_number(by: int):
    st.session_state.page_number += by

def render():
    
    # Initialize session state for page number if not exists
    if 'page_number' not in st.session_state:
        logger.info('Initializing page number in session state')
        st.session_state.page_number = 1
  
    #

    logger.info(f'current page {st.session_state.page_number}')
    # Create navigation controls
    col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])

    total_pages = 100 
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

    current_page_data, start_idx, end_idx = get_page_data(
        'tags',
        items_per_page=10,
        page_number=st.session_state.page_number)

    # Create the bar chart using plotly
    fig = px.bar(
        x=current_page_data.index,
        y=current_page_data.values,
        # orientation='h',
        title=f"{title} (Items {start_idx + 1}-{end_idx})",
        labels={'x': 'Count', 'y': 'Category'},
        text=current_page_data.values
    )
    # 
    # # Update layout for better appearance
    # # fig.update_traces(texttemplate='%{text}', textposition='outside')
    # # fig.update_layout(
    # #     height=max(400, len(current_page_data) * 40),  # Dynamic height based on items
    # #     showlegend=False,
    # #     xaxis_title="Count",
    # #     yaxis_title="Category",
    # #     yaxis={'categoryorder': 'total ascending'}  # Keep order from series
    # # )
    # 
    # # Display the chart
    st.plotly_chart(fig)
    # 
    # # # Optional: Display the data in a table
    # # with st.expander("View data table"):
    # #     df_display = pd.DataFrame({
    # #         'Category': current_page_data.index,
    # #         'Count': current_page_data.values,
    # #         'Percentage': (current_page_data.values / series.sum() * 100).round(2)
    # #     })
    # #     st.dataframe(df_display, use_container_width=True)
    # 
    # return current_page_data


render()
