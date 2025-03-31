import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

file_path = "datasets/matches_updated.csv"  
df = pd.read_csv(file_path)

def calculer_points(score1, score2):
    if score1 > score2:
        return 3  # Victoire
    elif score1 == score2:
        return 1  # Match nul
    else:
        return 0  # Défaite

def calculer_buts_marques(score1, score2):
    return score1

def calculer_buts_encaisses(score1, score2):
    return score2

df["points_t1"] = df.apply(lambda row: calculer_points(row["Score 1"], row["Score 2"]), axis=1)
df["buts_marques_t1"] = df.apply(lambda row: calculer_buts_marques(row["Score 1"], row["Score 2"]), axis=1)
df["buts_encaisses_t1"] = df.apply(lambda row: calculer_buts_encaisses(row["Score 1"], row["Score 2"]), axis=1)

df_long = pd.concat([
    df[["Journee", "Equipe 1", "points_t1", "buts_marques_t1", "buts_encaisses_t1"]].rename(columns={"Equipe 1": "Equipe"})
])

df_long = df_long.sort_values(by=["Equipe", "Journee"]).reset_index(drop=True)

df_long["Forme_3matchs"] = df_long.groupby("Equipe")["points_t1"].rolling(window=3, min_periods=1).sum().reset_index(level=0, drop=True)
df_long["Buts_marques_3matchs"] = df_long.groupby("Equipe")["buts_marques_t1"].rolling(window=3, min_periods=1).sum().reset_index(level=0, drop=True)
df_long["Buts_encaisses_3matchs"] = df_long.groupby("Equipe")["buts_encaisses_t1"].rolling(window=3, min_periods=1).sum().reset_index(level=0, drop=True)

df = df.merge(df_long, left_on=["Journee", "Equipe 1"], right_on=["Journee", "Equipe"], how="left").rename(columns={"Forme_3matchs": "Forme_t1", "Buts_marques_3matchs": "Buts_marques_t1", "Buts_encaisses_3matchs": "Buts_encaisses_t1"})
df = df.drop(columns=["Equipe"])

df_corr = df[["win_t1", "Forme_t1", "Buts_marques_t1", "Buts_encaisses_t1"]].corr()

plt.figure(figsize=(8, 6))
sns.heatmap(df_corr, annot=True, cmap="coolwarm", fmt=".2f", linewidths=0.5)
plt.title("Matrice de corrélation entre victoire, forme et buts sur 3 matchs")
plt.savefig("results/correlation_matrix_forme.png")
plt.show()
