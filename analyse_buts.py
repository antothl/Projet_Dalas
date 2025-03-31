import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

file_path = "datasets/matches_updated.csv"  
df = pd.read_csv(file_path)

championship_col = None
for col in df.columns:
    if "champ" in col.lower() or "league" in col.lower():
        championship_col = col
        break

df_long_buts = pd.concat([
    df[["Journee", "Equipe 1", "Score 1"]].rename(columns={"Equipe 1": "Equipe", "Score 1": "Buts"}),
    df[["Journee", "Equipe 2", "Score 2"]].rename(columns={"Equipe 2": "Equipe", "Score 2": "Buts"})
])

df_long_buts = df_long_buts.sort_values(by=["Equipe", "Journee"]).reset_index(drop=True)

df_long_buts["Buts_3matchs"] = df_long_buts.groupby("Equipe")["Buts"].rolling(window=3, min_periods=1).sum().reset_index(level=0, drop=True)

df = df.merge(df_long_buts, left_on=["Journee", "Equipe 1"], right_on=["Journee", "Equipe"], how="left").rename(columns={"Buts_3matchs": "Buts_t1"})
df = df.merge(df_long_buts, left_on=["Journee", "Equipe 2"], right_on=["Journee", "Equipe"], how="left").rename(columns={"Buts_3matchs": "Buts_t2"})

df = df.drop(columns=["Equipe_x", "Equipe_y"])

os.makedirs("results", exist_ok=True)

plt.figure(figsize=(12, 6))
sns.boxplot(data=df, x=championship_col, y="Buts_t1", hue="win_t1")
plt.title("Distribution du nombre de buts marqués (3 derniers matchs) par championnat et victoire")
plt.xlabel("Championnat")
plt.ylabel("Buts marqués sur 3 matchs")
plt.ylim(0, 10)
plt.legend(title="Victoire de l'équipe 1")
plt.xticks(rotation=45)
plt.savefig("results/boxplot_buts_par_championnat.png")
plt.show()

plt.figure(figsize=(10, 6))
win_rate_buts = df.groupby("Buts_t1")["win_t1"].mean()
sns.barplot(x=win_rate_buts.index, y=win_rate_buts.values, color="royalblue")
plt.title("Probabilité de victoire en fonction des buts marqués sur les 3 derniers matchs")
plt.xlabel("Buts marqués (3 derniers matchs)")
plt.ylabel("Taux de victoire (%)")
plt.ylim(0, 1)
plt.xticks(range(0, 10))
plt.savefig("results/taux_victoire_par_buts.png")
plt.show()

plt.figure(figsize=(12, 6))
win_rate_by_champ_buts = df.groupby([championship_col, "Buts_t1"])["win_t1"].mean().reset_index()
sns.barplot(data=win_rate_by_champ_buts, x="Buts_t1", y="win_t1", hue=championship_col, ci=None)
plt.title("Probabilité de victoire en fonction des buts marqués par championnat")
plt.xlabel("Buts marqués (3 derniers matchs)")
plt.ylabel("Taux de victoire (%)")
plt.ylim(0, 1)
plt.xticks(range(0, 10))
plt.legend(title="Championnat", bbox_to_anchor=(1, 1))
plt.savefig("results/taux_victoire_par_championnat_buts.png")
plt.show()


file_path = "datasets/matches_updated.csv"  
df = pd.read_csv(file_path)

def calculer_buts_encaisses(score1, score2):
    return score2 

df["buts_encaisses_t1"] = df.apply(lambda row: calculer_buts_encaisses(row["Score 1"], row["Score 2"]), axis=1)
df["buts_encaisses_t2"] = df.apply(lambda row: calculer_buts_encaisses(row["Score 2"], row["Score 1"]), axis=1)

df_long = pd.concat([
    df[["Journee", "Equipe 1", "buts_encaisses_t1"]].rename(columns={"Equipe 1": "Equipe", "buts_encaisses_t1": "Buts_encaisses"}),
    df[["Journee", "Equipe 2", "buts_encaisses_t2"]].rename(columns={"Equipe 2": "Equipe", "buts_encaisses_t2": "Buts_encaisses"})
])

df_long = df_long.sort_values(by=["Equipe", "Journee"]).reset_index(drop=True)

df_long["Buts_encaisses_3matchs"] = df_long.groupby("Equipe")["Buts_encaisses"].rolling(window=3, min_periods=1).sum().reset_index(level=0, drop=True)

df = df.merge(df_long, left_on=["Journee", "Equipe 1"], right_on=["Journee", "Equipe"], how="left").rename(columns={"Buts_encaisses_3matchs": "Buts_encaisses_t1"})
df = df.merge(df_long, left_on=["Journee", "Equipe 2"], right_on=["Journee", "Equipe"], how="left").rename(columns={"Buts_encaisses_3matchs": "Buts_encaisses_t2"})
df = df.drop(columns=["Equipe_x", "Equipe_y"])
df = df.drop_duplicates(subset=["Journee", "Equipe 1", "Equipe 2"])

championship_col = None
for col in df.columns:
    if "champ" in col.lower() or "league" in col.lower():
        championship_col = col
        break

plt.figure(figsize=(12, 6))
sns.boxplot(data=df, x=championship_col, y="Buts_encaisses_t1", hue="win_t1")
plt.title("Distribution des buts encaissés sur 3 matchs par championnat et victoire")
plt.xlabel("Championnat")
plt.ylabel("Buts encaissés sur 3 matchs")
plt.legend(title="Victoire de l'équipe 1")
plt.xticks(rotation=45)
plt.savefig("results/buts_encaisses_distribution.png")
plt.show()

plt.figure(figsize=(10, 6))
win_rate = df.groupby("Buts_encaisses_t1")["win_t1"].mean()
sns.barplot(x=win_rate.index, y=win_rate.values, color="red")
plt.title("Probabilité de victoire en fonction des buts encaissés sur les 3 derniers matchs")
plt.xlabel("Buts encaissés sur 3 matchs")
plt.ylabel("Taux de victoire (%)")
plt.ylim(0, 1)
plt.xticks(range(int(df["Buts_encaisses_t1"].min()), int(df["Buts_encaisses_t1"].max()) + 1))
plt.savefig("results/probabilite_victoire_buts_encaisses.png")
plt.show()

plt.figure(figsize=(12, 6))
win_rate_by_champ = df.groupby([championship_col, "Buts_encaisses_t1"])["win_t1"].mean().reset_index()

sns.barplot(data=win_rate_by_champ, x="Buts_encaisses_t1", y="win_t1", hue=championship_col, ci=None)
plt.title("Probabilité de victoire en fonction des buts encaissés par championnat")
plt.xlabel("Buts encaissés sur 3 matchs")
plt.ylabel("Taux de victoire (%)")
plt.ylim(0, 1)
plt.xticks(range(int(df["Buts_encaisses_t1"].min()), int(df["Buts_encaisses_t1"].max()) + 1))
plt.legend(title="Championnat", bbox_to_anchor=(1, 1))
plt.savefig("results/probabilite_victoire_buts_encaisses_championnat.png")
plt.show()