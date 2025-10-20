import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

import sys, os

# Chemin absolu vers la racine du projet
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))

# Ajoute le dossier "src" au sys.path pour rendre mange_ta_main importable
SRC_PATH = os.path.join(PROJECT_ROOT, "src")
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

from mange_ta_main.pages.synthese_William import summarize_temporal_clustering







# ==========================================================
#                       CONFIG PAGE
# ==========================================================
st.set_page_config(
    page_title="Analyse des contributeurs – Synthèse William",
    page_icon="📊",
    layout="wide",
)

st.title("📊 Synthèse : Fidélisation et Analyse des Contributeurs")
st.markdown("""
Cette page présente une **analyse temporelle et comportementale** des contributeurs :
- Identification des *top contributeurs* (P99)
- Regroupement des trajectoires temporelles par **clustering**
- Détection du **super cœur** de contributeurs actifs
""")


# ==========================================================
#                    CHARGEMENT DES DONNÉES
# ==========================================================

@st.cache_data
def load_data():
    """Charge les données locales depuis le dossier Data/"""
    df_recipes = pd.read_pickle("Data/RAW_recipes_local.pkl")
    return df_recipes


df_recipes = load_data()
st.success(f"✅ Données chargées : {df_recipes.shape[0]:,} recettes analysées")


# ==========================================================
#                    CALCUL DU PIPELINE
# ==========================================================

with st.spinner("Calcul des clusters d’activité..."):
    results = summarize_temporal_clustering(df_recipes)

activity = results["activity_clustered"]
cluster_stats = results["cluster_stats"]
super_core_info = results["super_core_info"]
super_core_share = results["super_core_recipe_share"]

st.success("✅ Analyse terminée avec succès !")


# ==========================================================
#                    RÉSULTATS GLOBAUX
# ==========================================================

st.header("📈 Résumé global des clusters")
st.dataframe(cluster_stats, use_container_width=True)

col1, col2, col3 = st.columns(3)
col1.metric("Nombre total de clusters", results["n_clusters"])
col2.metric("Taille du super cœur", len(super_core_info["super_coeur"]))
col3.metric("Part des recettes du super cœur", f"{super_core_share:.2%}")


# ==========================================================
#                    VISUALISATION DES CLUSTERS
# ==========================================================

st.subheader("Évolution moyenne standardisée de l’activité (par cluster)")

model = results["cluster_model"]
activity_cols = activity.columns[:-1]  # exclut la colonne 'cluster'

fig, ax = plt.subplots(figsize=(10, 5))
for c in range(results["n_clusters"]):
    ax.plot(activity_cols, model.cluster_centers_[c], label=f"Cluster {c}")
ax.set_title("Évolution moyenne standardisée par cluster")
ax.set_xlabel("Mois")
ax.set_ylabel("Z-score d’activité")
ax.legend()
ax.grid(alpha=0.3)
st.pyplot(fig)


# ==========================================================
#                ANALYSE DU SUPER CŒUR
# ==========================================================

st.header("❤️ Analyse du Super Cœur des contributeurs")
pct_inactifs = super_core_info["pct_inactifs"]
st.write(f"**% de contributeurs (clusters 0 et 3) inactifs avant 2013 :** {pct_inactifs:.1%}")

st.write(f"**Contributeurs actifs après 2013 (Super Cœur)** : {len(super_core_info['super_coeur'])}")
st.write(f"**Contributeurs réguliers (≥ 6 mois actifs)** : {len(super_core_info['super_coeur_reg'])}")

# Aperçu des contributeurs du super cœur
df_super = super_core_info["df_super_coeur"][["contributor_id", "submitted", "id"]]
st.dataframe(df_super.head(10), use_container_width=True)


# ==========================================================
#                    EXPORT DES RÉSULTATS
# ==========================================================

st.subheader("📤 Export des données")
csv = cluster_stats.to_csv(index=False).encode("utf-8")
st.download_button(
    "⬇️ Télécharger les statistiques de cluster (CSV)",
    csv,
    "cluster_stats.csv",
    "text/csv",
    key="download-cluster",
)

super_core_csv = df_super.to_csv(index=False).encode("utf-8")
st.download_button(
    "⬇️ Télécharger les contributeurs du super cœur (CSV)",
    super_core_csv,
    "super_coeur.csv",
    "text/csv",
    key="download-supercore",
)
