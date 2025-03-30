import pandas as pd

# Charger les fichiers
games_events = pd.read_csv("../datasets/kaggle_data/game_events.csv")
games_filtered = pd.read_csv("../datasets/kaggle_cleaned/games_filtered.csv")

valid_game_ids = games_filtered["game_id"].unique()

games_events_filtered = games_events[games_events["game_id"].isin(valid_game_ids)]

games_events_filtered.to_csv("../datasets/kaggle_cleaned/games_events_filtered.csv", index=False)

print(f"Filtrage terminé. {len(games_events_filtered)} événements correspondants trouvés. Fichier sauvegardé sous 'games_events_filtered.csv'.")
