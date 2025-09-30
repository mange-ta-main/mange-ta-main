import streamlit as st
import pandas as pd
from pathlib import Path


DATA_DIR = Path(__file__).parent.parent.parent / "data" / "dowloaded"

st.write(DATA_DIR)
