import streamlit as st

def kaggle_link():
    st.sidebar.markdown(
        """
        <a href="https://www.kaggle.com/datasets/shuyangli94/food-com-recipes-and-user-interactions/data" target="_blank">
            <img src="https://www.kaggle.com/static/images/logos/kaggle-logo-transparent.svg" width="100">
        </a>
        """,
        unsafe_allow_html=True
    )
