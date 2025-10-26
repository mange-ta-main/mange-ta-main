import streamlit as st
from streamlit_option_menu import option_menu

# Define the pages and their file paths
pages = {   'Welcome':'main.py',
            'Popular':'pages/Popular.py',
            'Healthyness':'pages/0_Healthyness.py'}

icons = ["house", "bar-chart", "gear"]

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