import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from pathlib import Path

import streamlit as st

from utils.sidebar import kaggle_link
from utils.navbar import hide_page_navbar
from utils.navbar import nav
from assets import CAMENBEAR
from assets import SANTE_LOGO


st.set_page_config(page_title="Welcome", layout="wide")

# =========================================================================
# Customed navigation bar
# =========================================================================
# Hide navigation bar based on pages file names
hide_page_navbar()
# Generate customed navigation bar
nav('Welcome to NutriCorrelations')

kaggle_link()
st.sidebar.image(CAMENBEAR, width="stretch")

# =========================================================================
# Introduction
# =========================================================================

st.markdown("""
# Welcome to **NutriCorrelations**

### When Recipes Speak Health 🩺

In a world where food plays a central role in our well-being, understanding the connection between our culinary habits and public health has become essential. 
**NutriCorrelations** is a collaborative initiative between our organization and the Ministry of Health, aiming to explore these links using data from several sources.
            
As a first step towards understaning these links, we propose to analyse the 
[Food.com Recipes and Interactions dataset](https://www.kaggle.com/datasets/shuyangli94/food-com-recipes-and-user-interactions/data) made available by [kaggle](https://www.kaggle.com/).
This dataset consists of 180K+ recipes and 700K+ recipe reviews covering 18 years of user interactions and uploads on Food.com (formerly GeniusKitchen).         
       
Each recipe is rated based on nutritional value, taste, and practicality.
By cross-referencing this data with public health indicators, we aim to uncover meaningful correlations between certain types of dishes and observed health outcomes, such as chronic diseases, nutrient deficiencies, or obesity trends.

On this site, you’ll find **interactive statistics**, **clear visualizations**, and **accessible analyses** that reveal how our cooking habits and dietary patterns may impact our collective health.
            

Whether you’re a healthcare professional, researcher, educator, or simply curious, you’ll discover tools that will help you to better understand how our food habits and choices shape well-being.
            

Our mission: to **raise awareness**, **inform**, and **encourage** healthier eating habits through reliable data.
            

Explore, compare, and join a citizen-driven approach to informed nutrition.
""")

# =========================================================================
# Global research question
# =========================================================================
st.markdown("""
---
### Global Research Question

> **How can data from online recipes help us understand and improve eating behaviors from a public health perspective?**
---
""")

# ----------------------------------------
# Logo
# ----------------------------------------
col1, col2 = st.columns([1, 2])
with col2:
    st.image(SANTE_LOGO, width=300)
    st.markdown("""In partnership with Santé publique France""")
# ----------------------------------------