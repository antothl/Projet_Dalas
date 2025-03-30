import pandas as pd

games = pd.read_csv("../datasets/kaggle_data/games.csv")
clubs_filtered = pd.read_csv("../datasets/kaggle_cleaned/clubs_filtered.csv")

valid_club_ids = clubs_filtered["club_id"].unique()

games_filtered = games[
    (games["competition_type"] == "domestic_league") &  # Type de compétition
    (games["season"] >= 2021) &  # Saison >= 2021
    (games["home_club_id"].isin(valid_club_ids) | games["away_club_id"].isin(valid_club_ids))  # IDs des clubs dans clubs_filtered
]

games_filtered.to_csv("../datasets/kaggle_cleaned/games_filtered.csv", index=False)

print(f"Filtrage terminé. {len(games_filtered)} matchs correspondants trouvés. Fichier sauvegardé sous 'games_filtered.csv'.")
