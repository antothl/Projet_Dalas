import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns

file_path = "datasets/matches_updated.csv"  
df = pd.read_csv(file_path)
os.makedirs("results", exist_ok=True)

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

championship_col = None
for col in df.columns:
    if "champ" in col.lower() or "league" in col.lower():
        championship_col = col
        break

#Boxplot
plt.figure(figsize=(12, 6))
sns.boxplot(data=df, x=championship_col, y="Forme_t1", hue="win_t1")
plt.title("Distribution de la forme des équipes (3 derniers matchs) par championnat et victoire")
plt.xlabel("Championnat")
plt.ylabel("Forme sur 3 matchs")
plt.ylim(0, 10)  
plt.legend(title="Victoire de l'équipe 1")
plt.xticks(rotation=45)
plt.savefig("results/boxplot_forme_par_championnat.png")  # Sauvegarde
plt.show()

# Taux de victoire en fonction de la forme
plt.figure(figsize=(10, 6))
win_rate = df.groupby("Forme_t1")["win_t1"].mean()
sns.barplot(x=win_rate.index, y=win_rate.values, color="royalblue")
plt.title("Probabilité de victoire en fonction de la forme sur les 3 derniers matchs")
plt.xlabel("Forme (points sur les 3 derniers matchs)")
plt.ylabel("Taux de victoire (%)")
plt.ylim(0, 1)
plt.xticks(range(0, 10))  
plt.savefig("results/taux_victoire_par_forme.png")  # Sauvegarde
plt.show()

# Taux de victoire par championnat
plt.figure(figsize=(12, 6))
win_rate_by_champ = df.groupby([championship_col, "Forme_t1"])["win_t1"].mean().reset_index()
sns.barplot(data=win_rate_by_champ, x="Forme_t1", y="win_t1", hue=championship_col, ci=None)
plt.title("Probabilité de victoire en fonction de la forme par championnat")
plt.xlabel("Forme (points sur les 3 derniers matchs)")
plt.ylabel("Taux de victoire (%)")
plt.ylim(0, 1)  
plt.xticks(range(0, 10))  
plt.legend(title="Championnat", bbox_to_anchor=(1, 1))
plt.savefig("results/taux_victoire_par_championnat.png")  # Sauvegarde
plt.show()

#Meme analyse avec le nombre de buts marqués et encaissés