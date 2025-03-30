import pandas as pd

club_games = pd.read_csv("../datasets/kaggle_data/club_games.csv")
clubs_filtered = pd.read_csv("../datasets/kaggle_cleaned/clubs_filtered.csv")

valid_club_ids = clubs_filtered["club_id"].unique()

club_games_filtered = club_games[club_games["club_id"].isin(valid_club_ids)]

club_games_filtered.to_csv("../datasets/kaggle_cleaned/club_games_filtered.csv", index=False)

print(f"Filtrage terminé. {len(club_games_filtered)} jeux correspondants trouvés. Fichier sauvegardé sous 'club_games_filtered.csv'.")
