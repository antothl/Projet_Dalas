import pandas as pd


df_classement = pd.read_csv("datasets/classements_5_grands_championnats.csv")

# Extraire les noms uniques des équipes dans df_matchs
equipes_matchs = set(df_classement["Equipe"])

# Créer un dictionnaire avec les noms à corriger (partie de gauche remplie)
correspondance = {equipe: "" for equipe in sorted(equipes_matchs)}

# Sauvegarder en fichier CSV ou JSON pour compléter manuellement
pd.DataFrame.from_dict(correspondance, orient="index").to_csv("datasets/correspondance_equipes.csv", header=["Nom correct"])

print("✅ Dictionnaire généré ! Complète les correspondances dans 'datasets/correspondance_equipes.csv'.")
