import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os 
import seaborn as sns

# Apply global settings
plt.rcParams.update({
    'axes.spines.right': False,   # Enable right spine (solid)
    'axes.spines.top': False,     # Enable top spine (solid)
    'axes.grid': True,           # Enable grid
    'grid.alpha': 0.4,           # Make the grid transparent (adjust alpha)
    'xtick.direction': 'out',     # Tickmarks on x-axis (inside)
    'ytick.direction': 'out',     # Tickmarks on y-axis (inside)
    'grid.linestyle': '--',      # Dashed grid (can be changed)
    'axes.edgecolor': 'black',   # Ensure spines are visible
    'axes.linewidth': 1.2,        # Make spines slightly thicker
    'axes.labelsize': 11
})

def leagues_performances(data_folder, result_folder):
    # Charger le dataset
    df_matches = pd.read_csv(os.path.join(data_folder, "matches.csv"))

    # Filtrer les 5 grands championnats
    championnats = ["la-liga", "ligue-1", "premier-league", "bundesliga-1", "serie-a"]
    df_matches = df_matches[df_matches["Championnat"].isin(championnats)]

    # Déterminer le résultat du match
    conditions = [
        df_matches["Score 1"] > df_matches["Score 2"],
        df_matches["Score 1"] == df_matches["Score 2"],
        df_matches["Score 1"] < df_matches["Score 2"]
    ]
    choix = ["Victoire Domicile", "Nul", "Victoire Extérieur"]

    df_matches["Résultat"] = np.select(conditions, choix)

    # Calculer les pourcentages par championnat
    resultats = df_matches.groupby(["Championnat", "Résultat"]).size().unstack().apply(lambda x: x / x.sum(), axis=1) * 100

    # Affichage des résultats
    resultats.plot(kind="bar", stacked=True, figsize=(10, 6), colormap="coolwarm")

    plt.title("Répartition des résultats des matchs à domicile par championnat")
    plt.ylabel("Pourcentage (%)")
    plt.xticks(rotation=45)
    plt.legend(title="Résultat")
    plt.tight_layout()
    plt.savefig(os.path.join(result_folder, "performances_top5_leagues.png"))
    plt.close()


def plot_weather_impact(data_folder, result_folder):
    # Charger le dataset
    df = pd.read_csv(os.path.join(data_folder, "matches.csv"))

    # Calculer la température moyenne
    df["Temp Moyenne"] = (df["Temp Max"] + df["Temp Min"]) / 2

    # Définir les intervalles de température
    bins = [-np.inf, 10, 20, 30, np.inf]  # Catégories : <10°C, 10-20°C, 20-30°C, >30°C
    labels = ["<10°C", "10-20°C", "20-30°C", ">30°C"]
    df["Catégorie Temp"] = pd.cut(df["Temp Moyenne"], bins=bins, labels=labels)

    # Déterminer le résultat du match
    conditions = [
        df["Score 1"] > df["Score 2"],
        df["Score 1"] == df["Score 2"],
        df["Score 1"] < df["Score 2"]
    ]
    choix = ["Victoire Domicile", "Nul", "Victoire Extérieur"]
    df["Résultat"] = np.select(conditions, choix)

    # Calculer les pourcentages par catégorie de température
    resultats = df.groupby(["Catégorie Temp", "Résultat"], observed=False).size().unstack().apply(lambda x: x / x.sum(), axis=1) * 100

    # Affichage des résultats
    resultats.plot(kind="bar", stacked=True, figsize=(10, 6), colormap="coolwarm")
    plt.title("Impact de la température moyenne sur les résultats à domicile")
    plt.ylabel("Pourcentage (%)")
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(os.path.join(result_folder, "weather_conditions.png"))
    plt.close()


def plot_win_value_corr(data_folder, result_folder):
    # Charger les données
    df_matchs = pd.read_csv(os.path.join(data_folder, "matches_updated.csv"))

    # Liste des championnats
    championnats = df_matchs["Championnat"].unique()

    # Dictionnaire pour stocker les corrélations
    correlations = {}

    # Préparer les données de corrélation pour chaque championnat
    for champ in championnats:
        df_temp = df_matchs[df_matchs["Championnat"] == champ]
        corr = df_temp[["win_t1", "mean_value_t1", "mean_value_t2"]].corr()
        correlations[champ] = corr

    # Créer une figure avec 2 colonnes et 3 lignes (1 sous-graphe vide)
    fig, axes = plt.subplots(nrows=3, ncols=2, figsize=(12, 12))
    axes = axes.flatten()

    # Tracer les matrices de corrélation
    for i, champ in enumerate(championnats):
        sns.heatmap(correlations[champ], annot=True, cmap="coolwarm", ax=axes[i])
        axes[i].set_title(f"{champ}")

    # Masquer le dernier subplot si on a moins de 6
    if len(championnats) < len(axes):
        for j in range(len(championnats), len(axes)):
            fig.delaxes(axes[j])

    plt.tight_layout()
    plt.savefig(os.path.join(result_folder, "win_value_correlations.png"))