import streamlit as st
import os


def kaggle_link():    
    st.sidebar.markdown(
        """       
        <div align="center">
        
        <p><b>
        <big><big>
            Data made available by
        </big></big>
        </b></p>
        
        <a href="https://www.kaggle.com/datasets/shuyangli94/food-com-recipes-and-user-interactions/data" target="_blank">
            <img src="https://www.kaggle.com/static/images/logos/kaggle-logo-transparent.svg" width="150">
        </a>
        
        </div>
        """,
        unsafe_allow_html=True
    )