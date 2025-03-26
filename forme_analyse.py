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

df["points_t1"] = df.apply(lambda row: calculer_points(row["Score 1"], row["Score 2"]), axis=1)
df["points_t2"] = df.apply(lambda row: calculer_points(row["Score 2"], row["Score 1"]), axis=1)

df_long = pd.concat([
    df[["Journee", "Equipe 1", "points_t1"]].rename(columns={"Equipe 1": "Equipe", "points_t1": "Points"}),
    df[["Journee", "Equipe 2", "points_t2"]].rename(columns={"Equipe 2": "Equipe", "points_t2": "Points"})
])

df_long = df_long.sort_values(by=["Equipe", "Journee"]).reset_index(drop=True)

df_long["Forme_3matchs"] = df_long.groupby("Equipe")["Points"].rolling(window=3, min_periods=1).sum().reset_index(level=0, drop=True)

df = df.merge(df_long, left_on=["Journee", "Equipe 1"], right_on=["Journee", "Equipe"], how="left").rename(columns={"Forme_3matchs": "Forme_t1"})
df = df.merge(df_long, left_on=["Journee", "Equipe 2"], right_on=["Journee", "Equipe"], how="left").rename(columns={"Forme_3matchs": "Forme_t2"})

df = df.drop(columns=["Equipe_x", "Equipe_y"])

df = df.drop_duplicates(subset=["Journee", "Equipe 1", "Equipe 2"])

print(df[["Journee", "Equipe 1", "Forme_t1", "Equipe 2", "Forme_t2", "win_t1"]].head(10))

# Vérifier si une colonne de championnat existe
championship_col = None
for col in df.columns:
    if "champ" in col.lower() or "league" in col.lower():
        championship_col = col
        break

# Si une colonne de championnat est trouvée, tracer les bar plots
if championship_col:
    plt.figure(figsize=(12, 6))
    sns.barplot(data=df, x=championship_col, y="Forme_t1", hue="win_t1", ci=None)
    plt.title("Moyenne de la forme des équipes (3 derniers matchs) en fonction de la victoire")
    plt.xlabel("Championnat")
    plt.ylabel("Forme moyenne sur 3 matchs")
    plt.ylim(0, ) 
    plt.legend(title="Victoire de l'équipe 1")
    plt.xticks(rotation=45)
    plt.show()
else:
    print("Aucune colonne de championnat détectée dans le dataset.")

