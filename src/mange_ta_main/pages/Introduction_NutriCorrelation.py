import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from pathlib import Path
#from pages import Popular_Nutricional_Score #Contributor_Activity_Analysis


col1, col2 = st.columns([1, 5])
with col1:
    #radio buttons on the left to go directly to the pages
    page = st.radio("Interactive Statistics", ['Popular_Nutricional_Score', 'Contributor_Activity_Analysis'])
    
    if page == "Popular_Nutricional_Score":
        st.write("Not available 1")  #Popular_Nutricional_Score.show()
    elif page == "1_To_cook_or_Not_to_cook":
        st.write("Not available")  #Contributor_Activity_Analysis.show()

        
with col2:
    # Introduction text
    st.markdown("""
    ## Welcome to NutriCorrelations

    ###When Recipes Speak Health 

    In a world where food plays a central role in our well-being, understanding the connection
    between our culinary habits and public health has become essential. NutriCorrelations is 
    a collaborative initiative between our organization and the Ministry of Health, 
    aiming to explore these links through data from our peer-reviewed recipe database. 

    Each recipe in our collection is rated based on nutritional value, taste, and practicality.
    By cross-referencing this data with public health indicators, we seek to identify meaningful
    correlations between certain types of dishes and observed health outcomes—such as chronic illnesses, deficiencies, or obesity. 

    On this site, you’ll find **interactive statistics, clear visualizations**, and **accessible analyses**
    that highlight dietary trends and their impacts. Whether you’re a healthcare professional, researcher,
    educator, or simply curious, you’ll discover tools here to better understand how our food choices influence collective health. 

    Our mission: to **raise awareness, inform**, and **encourage** healthier eating habits based on concrete data. 

    Explore, compare, and take part in a citizen-driven approach to informed nutrition. 
    """)

