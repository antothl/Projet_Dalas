import pandas as pd
import numpy as np

# Charger les fichiers
df_joueurs = pd.read_csv("datasets/joueurs_grands_championnats.csv")
df_matchs = pd.read_csv("datasets/matches.csv")

# Nettoyer la colonne "Valeur marchande"
def convertir_valeur(val):
    if isinstance(val, str):
        val = val.replace(" K €", "000").replace(" M €", "000000").replace(" €", "")
        try:
            return int(val)
        except ValueError:
            return np.nan
    return np.nan

df_joueurs["Valeur"] = df_joueurs["Valeur Marchande"].apply(convertir_valeur)

# Calculer la valeur moyenne par équipe et saison
df_valeurs = df_joueurs.groupby(["Saison", "Club"])["Valeur"].mean().reset_index()
df_valeurs.rename(columns={"Valeur": "Valeur Moyenne"}, inplace=True)

# Fusionner les valeurs moyennes avec les matchs (Équipe 1 et Équipe 2)
df_matchs = df_matchs.merge(df_valeurs, left_on=["Saison", "Equipe 1"], right_on=["Saison", "Club"], how="left")
df_matchs.rename(columns={"Valeur Moyenne": "Valeur Moyenne Équipe 1"}, inplace=True)
df_matchs.drop(columns=["Club"], inplace=True)

df_matchs = df_matchs.merge(df_valeurs, left_on=["Saison", "Equipe 2"], right_on=["Saison", "Club"], how="left")
df_matchs.rename(columns={"Valeur Moyenne": "Valeur Moyenne Équipe 2"}, inplace=True)
df_matchs.drop(columns=["Club"], inplace=True)

# Créer une colonne "Win" : 1 si Équipe 1 gagne, 0 sinon
df_matchs["Win"] = np.where(df_matchs["Score 1"] > df_matchs["Score 2"], 1, 0)

# Analyse de la corrélation
corr = df_matchs[["Win", "Valeur Moyenne Équipe 1", "Valeur Moyenne Équipe 2"]].corr()
print(corr)

# Sauvegarde du fichier mis à jour
df_matchs.to_csv("datasets/matches_updated.csv", index=False)
