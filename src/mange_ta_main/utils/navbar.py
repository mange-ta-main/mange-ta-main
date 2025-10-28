import streamlit as st
from streamlit_option_menu import option_menu


def hide_page_navbar():
    st.set_page_config(initial_sidebar_state="collapsed")

    no_sidebar_style = """
        <style>
            div[data-testid="stSidebarNav"] {
                display: none;
            }
        </style>
    """
    st.markdown(no_sidebar_style, unsafe_allow_html=True)


# Define the pages and their file paths
pages = {   'Data':'main.py',
            'Welcome to NutriCorrelations':'pages/Introduction_NutriCorrelation.py',
            'To cook or NOT to COOK?':'pages/To_cook_or_Not_to_cook.py',
            'Contributor Activity Analysis':'pages/Contributor_Activity_Analysis.py',
            'Healthiness':'pages/Healthiness.py',
            'Popular Nutritional Score':'pages/Popular_Nutricional_Score.py',
            'Univariate Tags':'pages/Univariate_Tags.py',}

icons = ["database", "house", "clock", "graph-up","heart-pulse","graph-up-arrow","tags"]

# Create a list of the page names
page_list = list(pages.keys())

def nav(current_page=page_list[0]):

    with st.sidebar:
        p = option_menu("Page Menu", page_list, 
            default_index=page_list.index(current_page), 
            orientation="vertical",
            icons=icons)

        if current_page != p:
            st.switch_page(pages[p])