import pandas as pd
import streamlit as st
from mange_ta_main.data import load_data


st.header('Tags')

def get_unique(column: str, df: pd.DataFrame):
    series = df[column].dropna().apply(lambda x: x[1:-1].split(','))
    series_exploded = series.explode()
    series_counts = series_exploded.value_counts()

    st.dataframe(series_counts.head())



get_unique('ingredients', load_data())

