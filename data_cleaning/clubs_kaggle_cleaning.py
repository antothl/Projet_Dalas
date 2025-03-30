import pandas as pd
from thefuzz import process

clubs = pd.read_csv("../datasets/kaggle_data/clubs.csv")
team_ids = pd.read_csv("../datasets/team_ids.csv")

championnats_cibles = {"FR1", "GB1", "IT1", "ES1", "L1"}
clubs = clubs[clubs["domestic_competition_id"].isin(championnats_cibles)]

team_names = team_ids["team"].unique()

def get_best_match(name, choices, threshold=80):
    match, score = process.extractOne(name, choices)
    return match if score >= threshold else None

clubs["matched_name"] = clubs["name"].apply(lambda x: get_best_match(x, team_names))

clubs_filtered = clubs.dropna(subset=["matched_name"])

clubs_filtered.to_csv("../datasets/kaggle_cleaned/clubs_filtered.csv", index=False)

print(f"Filtrage terminé. {len(clubs_filtered)} clubs correspondants trouvés. Fichier sauvegardé sous 'clubs_filtered.csv'.")
