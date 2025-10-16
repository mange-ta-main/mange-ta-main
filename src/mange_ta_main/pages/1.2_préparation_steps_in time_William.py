import numpy as np
import streamlit as st
import pandas as pd
import matplotlib
matplotlib.use('MacOSX')   # backend natif pour macOS
import matplotlib.pyplot as plt


df_recipes = pd.read_pickle("Data/RAW_recipes_local.pkl")
df_interactions = pd.read_pickle("Data/RAW_interactions_local.pkl")

# mise en forme de submitted
df_recipes['submitted'] = pd.to_datetime(df_recipes['submitted'],errors='coerce')
df = df_recipes[['n_steps','id','submitted','minutes']].copy()
df["month"] = df["submitted"].dt.to_period('M').dt.to_timestamp()
df = df.sort_values('month',ascending=True) 

df = df.drop('submitted',axis=1)
print(df.head())
# 
mean_time =df.groupby('month')['minutes'].agg('mean')
moyenne_étape_mois = df.groupby('month')['n_steps'].agg('mean')
print(df.head())


fig,axes = plt.subplots(2,1)

axes[0].plot(mean_time.index,mean_time,color='blue',label='évolution du temps moyen de préparation dans le temps')
axes[0].legend()
axes[1].plot(moyenne_étape_mois.index,moyenne_étape_mois,color='red',label='évolution du nombre d étape moyen dans le temps')
axes[1].legend()
plt.xlabel('mois')
plt.legend()
plt.show()
#nb_recettes_mois = df.groupby('month')['id'].count()



