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

def leagues_performances(df_matches, result_folder):

    # Déterminer le résultat du match
    conditions = [
        df_matches["Score 1"] > df_matches["Score 2"],
        df_matches["Score 1"] == df_matches["Score 2"],
        df_matches["Score 1"] < df_matches["Score 2"]
    ]

    choix = ["Victoire Domicile", "Nul", "Victoire Extérieur"]

    df_matches["win_t1"] = np.select(conditions, choix)

    # Calculer les pourcentages par championnat
    resultats = df_matches.groupby(["Championnat", "win_t1"]).size().unstack().apply(lambda x: x / x.sum(), axis=1) * 100

    # Affichage des résultats
    resultats.plot(kind="bar", stacked=True, figsize=(10, 6), colormap="coolwarm")

    plt.title("Répartition des résultats des matchs à domicile par championnat")
    plt.ylabel("Pourcentage (%)")
    plt.xticks(rotation=45)
    plt.legend(title="Result (T1)")
    plt.tight_layout()
    plt.savefig(os.path.join(result_folder, "performances_top5_leagues.png"))
    plt.close()


def plot_weather_impact(df, result_folder):

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


def plot_win_value_corr(df_matchs, result_folder):

    # Liste des championnats
    championnats = df_matchs["Championnat"].unique()

    # Dictionnaire pour stocker les corrélations
    correlations = {}

    # Préparer les données de corrélation pour chaque championnat
    for champ in championnats:
        df_temp = df_matchs[df_matchs["Championnat"] == champ]
        corr = df_temp[["result_t1", "mean_value_t1", "mean_value_t2"]].corr()
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
    plt.close()

def match_mv_pearson(df_matchs, result_folder):

    # Step 2: Create long-format DataFrame
    df_long = pd.concat([
        df_matchs[['Equipe 1', 'mean_value_t1', 'avg_age_t1', 'sum_value_t1', 'result_t1']].rename(columns={
            'Equipe 1': 'Equipe',
            'mean_value_t1': 'mean_value',
            'avg_age_t1': 'avg_age',
            'sum_value_t1': 'sum_value',
            'result_t1': 'result'
        }),
        df_matchs[['Equipe 2', 'mean_value_t2', 'avg_age_t2', 'sum_value_t2', 'result_t2']].rename(columns={
            'Equipe 2': 'Equipe',
            'mean_value_t2': 'mean_value',
            'avg_age_t2': 'avg_age',
            'sum_value_t2': 'sum_value',
            'result_t2': 'result'
        })
    ], ignore_index=True)

    # Step 3: Create subplots for mean_value, avg_age, and sum_value
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    # Plot 1: mean_value vs result
    sns.regplot(data=df_long, x='mean_value', y='result', logistic=True, ci=None, ax=axes[0])
    corr1 = df_long[['mean_value', 'result']].corr().iloc[0, 1]
    axes[0].text(df_long['mean_value'].min(), 0.90, f"Pearson r = {corr1:.2f}", 
                bbox=dict(boxstyle="round", facecolor="lightyellow", edgecolor="gray"))
    axes[0].set_title("Market Value vs Match Result")
    axes[0].set_xlabel("Mean Market Value")
    axes[0].set_ylabel("Match Result")

    # Plot 2: avg_age vs result
    sns.regplot(data=df_long, x='avg_age', y='result', logistic=True, ci=None, ax=axes[1])
    corr2 = df_long[['avg_age', 'result']].corr().iloc[0, 1]
    axes[1].text(df_long['avg_age'].min(), 0.90, f"Pearson r = {corr2:.2f}", 
                bbox=dict(boxstyle="round", facecolor="lightyellow", edgecolor="gray"))
    axes[1].set_title("Average Age vs Match Result")
    axes[1].set_xlabel("Average Age")
    axes[1].set_ylabel("Match Result")

    # Plot 3: sum_value vs result
    sns.regplot(data=df_long, x='sum_value', y='result', logistic=True, ci=None, ax=axes[2])
    corr3 = df_long[['sum_value', 'result']].corr().iloc[0, 1]
    axes[2].text(df_long['sum_value'].min(), 0.90, f"Pearson r = {corr3:.2f}", 
                bbox=dict(boxstyle="round", facecolor="lightyellow", edgecolor="gray"))
    axes[2].set_title("Total Market Value vs Match Result")
    axes[2].set_xlabel("Total Market Value")
    axes[2].set_ylabel("Match Result")

    plt.tight_layout()
    plt.savefig(os.path.join(result_folder, "results_team_pearson.png"))
    plt.close()

def plot_mv_age_leagues(df_teams, result_folder):
    df_grouped = df_teams.groupby("Championnat")[["sum_value", "avg_age"]].mean().reset_index()

    # Set up the figure and axes
    fig, ax1 = plt.subplots(figsize=(10, 6))

    # Bar width and positions
    x = range(len(df_grouped))
    bar_width = 0.4

    # Plot average market value on ax1
    ax1.bar([i - bar_width/2 for i in x], df_grouped["sum_value"], width=bar_width, label="Market Value (€)", color="skyblue")
    ax1.set_ylabel("Average Market Value (€)")
    ax1.tick_params(axis='y')

    # Create a second y-axis
    ax2 = ax1.twinx()
    ax2.bar([i + bar_width/2 for i in x], df_grouped["avg_age"], width=bar_width, label="Average Age", color="lightcoral")
    ax2.set_ylim((20,30))
    ax2.set_ylabel("Average Age")
    ax2.tick_params(axis='y')

    # X-axis settings
    ax1.set_xticks(x)
    ax1.set_xticklabels(df_grouped["Championnat"], rotation=45)
    ax1.set_xlabel("League")
    plt.title("Average Market Value and Age by League")

    # Grid and layout
    ax1.grid(axis='y', linestyle='--', alpha=0.3)
    fig.tight_layout()
    plt.savefig(os.path.join(result_folder, "market_value_age_leagues.png"))
    plt.close()



def goals_rankings_results_plots(df_merged, result_folder):
    # Custom color mapping
    custom_palette = {
        "L": "lightcoral",
        "D": "moccasin",
        "W": "lightgreen"
    }

    # Analysis 1: Goal Difference vs Match Result
    plt.figure(figsize=(6, 4))
    sns.boxplot(
        data=df_merged,
        x="result_label",
        y="goal_diff_gap",
        hue="result_label",
        palette=custom_palette,
        legend=True)

    plt.xlabel("Match Result (T1)")
    plt.ylabel("Goal Difference Gap")
    plt.grid(axis='y', linestyle='--', alpha=0.4)
    plt.tight_layout()
    plt.savefig(os.path.join(result_folder, "goals_vs_results.png"))
    plt.close()

    # Analysis 2: Offensive vs Defensive Strength
    plt.figure(figsize=(6, 4))
    sns.boxplot(data=df_merged, x="result_label", y="offense_score_t1", hue="result_label", palette=custom_palette, legend=True)
    plt.title("Team 1 Offensive Potential vs Match Result")
    plt.xlabel("Match Result (Team 1)")
    plt.ylabel("GF (T1) - GA (T2)")
    plt.grid(axis='y', linestyle='--', alpha=0.4)
    plt.tight_layout()
    plt.savefig(os.path.join(result_folder, "off_def_vs_results.png"))
    plt.close()

    # Analysis 3: Points Gap and Ranking Difference vs Match Result
    fig, axs = plt.subplots(1, 2, figsize=(12, 4))

    sns.boxplot(data=df_merged, x="result_label", y="points_gap", ax=axs[0], hue="result_label", palette=custom_palette, legend=True)
    axs[0].set_title("Points Gap vs Match Result")
    axs[0].set_xlabel("Match Result (Team 1)")
    axs[0].set_ylabel("Points T1 - Points T2")
    axs[0].grid(axis='y', linestyle='--', alpha=0.4)

    sns.boxplot(data=df_merged, x="result_label", y="rank_diff", ax=axs[1], hue="result_label", palette=custom_palette, legend=True)
    axs[1].set_title("Ranking Difference vs Match Result")
    axs[1].set_xlabel("Match Result (Team 1)")
    axs[1].set_ylabel("Position T2 - Position T1")
    axs[1].grid(axis='y', linestyle='--', alpha=0.4)

    plt.tight_layout()
    plt.savefig(os.path.join(result_folder, "point_gap_vs_results.png"))
    plt.close()

    # Analysis 4: Correlation Heatmap
    correlation_features = [
        "Points_t1", "Points_t2", "goal_diff_gap", "rank_diff",
        "Buts Pour_t1", "Buts Contre_t2", "offense_score_t1", "result_t1"
    ]
    plt.figure(figsize=(8, 6))
    sns.heatmap(df_merged[correlation_features].corr(), annot=True, cmap="coolwarm", fmt=".2f")
    plt.title("Correlation Matrix: Match Result vs Team Stats")
    plt.tight_layout()
    plt.savefig(os.path.join(result_folder, "Correlation_map.png"))
    plt.close()


def goals_home_away(df_goals, result_folder):

    # Create subplots
    fig, axs = plt.subplots(1, 2, figsize=(12, 5))

    # Goals Scored
    sns.boxplot(data=df_goals, x="location", y="goals_scored", ax=axs[0], hue="location", palette={"Home": "skyblue", "Away": "orange"})
    axs[0].set_title("Goals Scored per Match")
    axs[0].set_xlabel("Match Location")
    axs[0].set_ylabel("Goals Scored")

    # Goals Conceded
    sns.boxplot(data=df_goals, x="location", y="goals_conceded", ax=axs[1], hue="location", palette={"Home": "skyblue", "Away": "orange"}, legend=True)
    axs[1].set_title("Goals Conceded per Match")
    axs[1].set_xlabel("Match Location")
    axs[1].set_ylabel("Goals Conceded")
    plt.tight_layout()
    plt.savefig(os.path.join(result_folder, "goals_home_away.png"))
    plt.close()


def plot_goals_pleague(df_merged, result_folder):
    # Use the currently loaded match data instead of df_matchs
    df_metrics = pd.DataFrame({
        "Avg Goals per Match": df_merged["Score 1"].groupby(df_merged["Championnat"]).mean() + df_merged["Score 2"].groupby(df_merged["Championnat"]).mean(),
        "Avg Goal Diff Gap": df_merged.groupby("Championnat")["goal_diff_gap"].mean(),
        "Avg Offensive Score": df_merged.groupby("Championnat")["offense_score_t1"].mean()
    }).reset_index()

    # Melt the dataframe to long format for seaborn
    df_melted = df_metrics.melt(id_vars="Championnat", var_name="Metric", value_name="Value")

    # Plot grouped barplot
    plt.figure(figsize=(10, 6))
    sns.barplot(data=df_melted, x="Championnat", y="Value", hue="Metric")

    plt.title("Comparison of Goal Metrics by League")
    plt.xlabel("League")
    plt.ylabel("Average Value")
    plt.xticks(rotation=45)
    plt.grid(axis='y', linestyle='--', alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(result_folder, "goals_pleague.png"))
    plt.close()