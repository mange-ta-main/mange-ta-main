import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from pathlib import Path


import streamlit as st

st.header("Home Page")

# === Global style for buttons ===
st.markdown("""
    <style>
    div.stButton > button {
        background-color: #0066cc;
        color: white;
        border: none;
        padding: 10px 24px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 6px;
        cursor: pointer;
        border-radius: 8px;
        transition-duration: 0.3s;
    }
    div.stButton > button:hover {
        background-color: #45a049;
    }
    </style>
""", unsafe_allow_html=True)

# === Centered buttons on two rows ===
st.markdown("<div style='text-align:center'>", unsafe_allow_html=True)

# Row 1
row1_col1, row1_col2, row1_col3 = st.columns([1, 1, 1], gap="large")
with row1_col1:
    if st.button("To Cook or Not to Cook"):
        st.switch_page("pages/1_To_cook_or_Not_to_cook.py")
with row1_col2:
    if st.button("Healthyness"):
        st.switch_page("pages/0_Healthyness.py")
with row1_col3:
    if st.button("Contributor Activity"):
        st.switch_page("pages/Contributor_Activity_Analysis.py")

# Row 2
row2_col1, row2_col2, row2_col3 = st.columns([1, 1, 1], gap="large")
with row2_col1:
    if st.button("Popular Nutritional Score"):
        st.switch_page("pages/Popular_Nutricional_Score.py")
with row2_col2:
    if st.button("Univariate Tags"):
        st.switch_page("pages/4_univariate_tags.py")
with row2_col3:
    st.empty()  # spacing / alignment

st.markdown("</div>", unsafe_allow_html=True)

# === Introduction text ===
st.markdown("""
## Welcome to **NutriCorrelations**

### When Recipes Speak Health

In a world where food plays a central role in our well-being, understanding the connection between our culinary habits and public health has become essential.  
**NutriCorrelations** is a collaborative initiative between our organization and the Ministry of Health, aiming to explore these links using data from our peer-reviewed recipe database.

Each recipe in our collection is rated based on nutritional value, taste, and practicality.  
By cross-referencing this data with public health indicators, we aim to uncover meaningful correlations between certain types of dishes and observed health outcomes—such as chronic diseases, nutrient deficiencies, or obesity trends.

On this site, you’ll find **interactive statistics**, **clear visualizations**, and **accessible analyses** that reveal how dietary patterns impact our collective health.  
Whether you’re a healthcare professional, researcher, educator, or simply curious, you’ll discover tools here to better understand how our food choices shape well-being.

Our mission: to **raise awareness**, **inform**, and **encourage** healthier eating habits through reliable data.

Explore, compare, and join a citizen-driven approach to informed nutrition.
""")

# === Global research question / problématique ===
st.markdown("""
---
### Global Research Question

> **How can data from online recipes help us understand and improve eating behaviors from a public health perspective?**
---
""")


# === Simple centered logo at the bottom ===
st.markdown("<br><br>", unsafe_allow_html=True)  # spacing
st.markdown(
    """
    <div style="text-align:center;">
        <img src="../../data/Sante_logo.jpg" width="250">
        <p><em>In partnership with Santé publique France</em></p>
    </div>
    """,
    unsafe_allow_html=True)