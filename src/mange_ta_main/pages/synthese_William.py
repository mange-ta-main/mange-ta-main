import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans


df_recipes = pd.read_pickle("Data/RAW_recipes_local.pkl")
df_interactions = pd.read_pickle("Data/RAW_interactions_local.pkl")

# ==========================================================
#        ANALYSE DE LA CONTRIBUTION DES CONTRIBUTEURS
# ==========================================================

def compute_contributor_stats(df_recipes):
    """
    Calcule les statistiques générales de contribution des contributeurs.
    Retourne :
    - total_recipes : nombre total de recettes
    - mean_contribution, min_contribution, max_contribution
    - distribution des contributions (nb_recipes_contributor)
    """
    nb_recipes_contributor = df_recipes['contributor_id'].value_counts()
    total_recipes = df_recipes.shape[0]
    mean_contribution = nb_recipes_contributor.mean()
    max_contribution = nb_recipes_contributor.max()
    min_contribution = nb_recipes_contributor.min()

    return {
        "total_recipes": total_recipes,
        "mean_contribution": mean_contribution,
        "max_contribution": max_contribution,
        "min_contribution": min_contribution,
        "nb_recipes_contributor": nb_recipes_contributor
    }


def percentile_analysis(nb_recipes_contributor, percentiles=[75, 90, 95, 99]):
    """
    Calcule les parts de contributeurs et de recettes par percentile (Q3, P90, P95, P99).
    Retourne un DataFrame résumant les résultats.
    """
    results = []
    total_recipes = nb_recipes_contributor.sum()
    total_contributors = nb_recipes_contributor.size

    for p in percentiles:
        seuil = np.percentile(nb_recipes_contributor, p)
        top_contributors = nb_recipes_contributor[nb_recipes_contributor > seuil]
        share_contributors = top_contributors.size / total_contributors
        share_recipes = top_contributors.sum() / total_recipes

        results.append({
            "percentile": p,
            "seuil": seuil,
            "nb_top_contributors": top_contributors.size,
            "share_contributors": share_contributors,
            "share_recipes": share_recipes
        })

    return pd.DataFrame(results)


def lorenz_curve(nb_recipes_contributor):
    """
    Calcule les données nécessaires à la courbe de Lorenz.
    Retourne deux vecteurs (x, y) : cumul contributeurs et cumul recettes.
    """
    counts_sorted = nb_recipes_contributor.sort_values(ascending=False).values
    cum_recipes = np.cumsum(counts_sorted) / np.sum(counts_sorted)
    cum_contributors = np.arange(1, len(counts_sorted)+1) / len(counts_sorted)
    return cum_contributors, cum_recipes


def high_contributor_band(df_recipes, low=1250, high=3500):
    """
    Identifie les contributeurs "hyperactifs" dans une bande de contributions.
    Retourne le nombre de contributeurs et leur part de contribution totale.
    """
    count = df_recipes['contributor_id'].value_counts()
    band = count[(count > low) & (count <= high)].sort_values(ascending=True)
    n_band = band.size
    share_band = band.sum() / count.sum()
    return {
        "n_contributors_band": n_band,
        "share_band": share_band,
        "band_details": band
    }


def summarize_contributor_analysis(df_recipes):
    """
    Fonction principale qui orchestre toute l’analyse.
    Retourne un dictionnaire avec toutes les métriques clés.
    """
    stats = compute_contributor_stats(df_recipes)
    nb_recipes_contributor = stats["nb_recipes_contributor"]

    # Analyse par percentiles
    percentiles_df = percentile_analysis(nb_recipes_contributor)

    # Courbe de Lorenz
    lorenz_x, lorenz_y = lorenz_curve(nb_recipes_contributor)

    # Bande des contributeurs hyperactifs
    band_stats = high_contributor_band(df_recipes)

    return {
        "general_stats": stats,
        "percentile_stats": percentiles_df,
        "lorenz_data": (lorenz_x, lorenz_y),
        "band_stats": band_stats
    }

resultats = summarize_contributor_analysis(df_recipes)


# ==========================================================
#         ANALYSE TEMPORELLE & CLUSTERING CONTRIBUTEURS
# ==========================================================

def build_activity_matrix(df, freq="M"):
    """
    Crée la matrice d'activité auteurs x période.
    Chaque ligne = un auteur, chaque colonne = un mois, chaque cellule = nb de recettes publiées.
    """
    df = df.copy()
    df["month"] = df["submitted"].dt.to_period(freq).dt.to_timestamp()
    activity = (
        df.groupby(["contributor_id", "month"])["id"]
          .nunique()
          .unstack(fill_value=0)
          .sort_index(axis=1)
    )
    return activity


def filter_top_contributors(df, top_n=277):
    """Filtre les top N contributeurs selon le nombre total de recettes publiées."""
    contrib_counts = df.groupby("contributor_id")["id"].nunique().sort_values(ascending=False)
    top_authors = contrib_counts.head(top_n).index
    return df[df["contributor_id"].isin(top_authors)]


def prepare_activity_data(df, top_n=277):
    """
    Prépare les données avant clustering :
    - filtre les top contributeurs
    - construit la matrice d'activité
    """
    df_top = filter_top_contributors(df, top_n)
    return build_activity_matrix(df_top)


def perform_activity_clustering(activity, n_clusters=4, window=3, random_state=42):
    """
    Standardise les trajectoires temporelles et applique un clustering KMeans.
    Retourne :
      - activity_df : DataFrame enrichie du cluster
      - model : objet KMeans entraîné
      - n_clusters_found : nombre de clusters détectés
    """
    scaler = StandardScaler()
    X = scaler.fit_transform(activity.rolling(window=window, axis=1, min_periods=1).mean())

    km = KMeans(n_clusters=n_clusters, random_state=random_state)
    labels = km.fit_predict(X)

    activity_clustered = activity.copy()
    activity_clustered["cluster"] = labels

    return activity_clustered, km, len(set(labels))


def get_cluster_contributors(activity_clustered, cluster_id):
    """Renvoie la liste des contributeurs appartenant à un cluster donné."""
    return activity_clustered.index[activity_clustered["cluster"] == cluster_id]


def compute_recipes_by_cluster(df_recipes, activity_clustered):
    """
    Calcule le nombre de recettes par cluster.
    Retourne un DataFrame (cluster_id, n_contributors, n_recipes)
    """
    data = []
    for c in sorted(activity_clustered["cluster"].unique()):
        contributors = get_cluster_contributors(activity_clustered, c)
        n_contrib = len(contributors)
        n_recipes = df_recipes[df_recipes["contributor_id"].isin(contributors)].shape[0]
        data.append({
            "cluster": c,
            "n_contributors": n_contrib,
            "n_recipes": n_recipes
        })
    return pd.DataFrame(data)


def identify_super_core(df_recipes, activity_clustered, active_clusters=[0, 3],
                        cutoff="2013-01-01", active_window=("2008-01-01", "2014-12-31"),
                        min_active_months=6):
    """
    Identifie les contributeurs du 'super cœur' :
      - appartenant aux clusters spécifiés (0 & 3 par défaut)
      - actifs après une date cutoff
      - actifs au moins sur N mois dans la fenêtre temporelle
    Retourne :
      - super_coeur : liste des contributeurs
      - super_coeur_reg : liste des contributeurs réguliers
      - pct_inactifs : % d'inactifs avant cutoff
      - df_super_coeur : sous-ensemble du df_recipes
    """
    START, END = pd.Timestamp(active_window[0]), pd.Timestamp(active_window[1])
    cutoff = pd.Timestamp(cutoff)

    # 🩹 Sécurisation des dates
    df_recipes = df_recipes.copy()
    df_recipes["submitted"] = pd.to_datetime(df_recipes["submitted"], errors="coerce")

    # Cibles : contributeurs des clusters sélectionnés
    targets = activity_clustered.index[activity_clustered["cluster"].isin(active_clusters)]

    # Dernière publication par contributeur
    last_pub = df_recipes.groupby("contributor_id")["submitted"].max()

    # Retirer les contributeurs sans date valide
    last_pub = last_pub.dropna()

    # % d'inactifs avant cutoff
    if not last_pub.loc[targets].empty:
        pct_inactifs = (last_pub.loc[targets] < cutoff).mean()
    else:
        pct_inactifs = np.nan

    # Super cœur : actifs après cutoff
    super_coeur = [cid for cid in targets if last_pub.get(cid, pd.Timestamp.min) >= cutoff]

    # Régularité (≥ N mois actifs sur la période)
    df_win = df_recipes[(df_recipes["submitted"] >= START) & (df_recipes["submitted"] <= END)]
    df_win = df_win[df_win["contributor_id"].isin(targets)].copy()
    df_win["month"] = df_win["submitted"].dt.to_period("M").dt.to_timestamp()

    mois_actifs = (df_win.groupby(["contributor_id", "month"])["id"].nunique() > 0)\
        .groupby("contributor_id").sum()

    super_coeur_reg = mois_actifs[mois_actifs >= min_active_months].index.tolist()

    # Sous-ensemble du DataFrame principal
    df_super_coeur = df_recipes[df_recipes["contributor_id"].isin(super_coeur)]

    return {
        "super_coeur": super_coeur,
        "super_coeur_reg": super_coeur_reg,
        "pct_inactifs": pct_inactifs,
        "df_super_coeur": df_super_coeur
    }

def summarize_temporal_clustering(df_recipes, top_n=277, n_clusters=4):
    """
    Fonction principale : pipeline complet de clustering d'activité et d'identification du super cœur.
    """
    df = df_recipes.copy()
    df["submitted"] = pd.to_datetime(df["submitted"], errors="coerce")
    df = df.sort_values("submitted")

    # Étape 1 : Préparation
    activity = prepare_activity_data(df, top_n)

    # Étape 2 : Clustering
    activity_clustered, model, n_clusters_found = perform_activity_clustering(activity, n_clusters)

    # Étape 3 : Statistiques globales des clusters
    cluster_stats = compute_recipes_by_cluster(df_recipes, activity_clustered)

    # Étape 4 : Super cœur
    super_core_info = identify_super_core(df_recipes, activity_clustered)

    # Étape 5 : Contribution du super cœur
    n_recettes_sc = df[df["contributor_id"].isin(super_core_info["super_coeur"])]["id"].nunique()
    repartition_sc = n_recettes_sc / df["id"].nunique()

    return {
        "activity_matrix": activity,
        "activity_clustered": activity_clustered,
        "cluster_model": model,
        "n_clusters": n_clusters_found,
        "cluster_stats": cluster_stats,
        "super_core_info": super_core_info,
        "super_core_recipe_share": repartition_sc
    }


results = summarize_temporal_clustering(df_recipes)