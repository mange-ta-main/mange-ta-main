import streamlit as st
from utils.sidebar import kaggle_link
from utils.data_loader import load_data
from streamlit_option_menu import option_menu

from utils.navbar import nav


st.set_page_config(initial_sidebar_state="collapsed")

no_sidebar_style = """
    <style>
        div[data-testid="stSidebarNav"] {
            display: none;
        }
    </style>
"""
st.markdown(no_sidebar_style, unsafe_allow_html=True)

def main():
    
    
    # builds the sidebar menu    
    #kaggle_link()
    df_recipes, df_interactions = load_data()

    nav('Welcome')

    # Display basic info
    st.header("Data")
    st.title("RECIPES:")
    st.dataframe(df_recipes.head())
    st.title("INTERACTIONS:")
    st.dataframe(df_interactions.head())

if __name__ == '__main__':
    main()