import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

file_path_matches = "datasets/matches_updated.csv"
file_path_stats = "datasets/stats_teams.csv"

df_matches = pd.read_csv(file_path_matches)
df_stats = pd.read_csv(file_path_stats)

def determine_season(date):
    year = int(date[:4]) 
    month = int(date[5:7]) 
    return year if month >= 7 else year - 1  

df_matches["season"] = df_matches["Date"].astype(str).apply(determine_season)

def calculer_points(score1, score2):
    if score1 > score2:
        return 3  # Victoire
    elif score1 == score2:
        return 1  # Match nul
    else:
        return 0  # Défaite

df_matches["points_t1"] = df_matches.apply(lambda row: calculer_points(row["Score 1"], row["Score 2"]), axis=1)
df_matches["points_t2"] = df_matches.apply(lambda row: calculer_points(row["Score 2"], row["Score 1"]), axis=1)

df_long = pd.concat([
    df_matches[["Journee", "Equipe 1", "points_t1", "Score 1", "Score 2"]].rename(columns={"Equipe 1": "Equipe", "points_t1": "Points", "Score 1": "Buts_marques", "Score 2": "Buts_encaisses"}),
    df_matches[["Journee", "Equipe 2", "points_t2", "Score 2", "Score 1"]].rename(columns={"Equipe 2": "Equipe", "points_t2": "Points", "Score 2": "Buts_marques", "Score 1": "Buts_encaisses"})
])

df_long = df_long.sort_values(by=["Equipe", "Journee"]).reset_index(drop=True)

df_long["Forme_3matchs"] = df_long.groupby("Equipe")["Points"].rolling(window=3, min_periods=1).sum().reset_index(level=0, drop=True)
df_long["Buts_marques_3matchs"] = df_long.groupby("Equipe")["Buts_marques"].rolling(window=3, min_periods=1).sum().reset_index(level=0, drop=True)
df_long["Buts_encaisses_3matchs"] = df_long.groupby("Equipe")["Buts_encaisses"].rolling(window=3, min_periods=1).sum().reset_index(level=0, drop=True)

df_matches = df_matches.merge(df_long, left_on=["Journee", "Equipe 1"], right_on=["Journee", "Equipe"], how="left").rename(columns={"Forme_3matchs": "Forme_t1", "Buts_marques_3matchs": "Buts_marques_t1", "Buts_encaisses_3matchs": "Buts_encaisses_t1"})
df_matches = df_matches.drop(columns=["Equipe"])

df_stats = df_stats.rename(columns={"club": "Equipe", "season": "season_stats"})
df = df_matches.merge(df_stats, left_on=["Equipe 1", "season"], right_on=["Equipe", "season_stats"], how="left")
df = df.drop(columns=["Equipe", "season_stats"])

corr_features = ["Forme_t1", "Buts_marques_t1", "Buts_encaisses_t1", "sum_value", "max_value", "mean_value", "total_attack_value", "total_defense_value", "total_midfield_value", "Temp Max","Precipitations","Temp Min", "win_t1"]
corr_matrix = df[corr_features].corr()

plt.figure(figsize=(10, 8))
sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", fmt=".2f", linewidths=0.5)
plt.title("Matrice de corrélation entre victoire et différentes métriques")
plt.savefig("results/correlation_matrix.png")
plt.show()
