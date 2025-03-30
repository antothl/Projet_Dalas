import pandas as pd

stats_teams = pd.read_csv('datasets/stats_teams.csv')
teams_ids = pd.read_csv('datasets/team_ids.csv')
clubs_filtered = pd.read_csv('datasets/kaggle_cleaned/clubs_filtered.csv')
print(teams_ids.columns)
# Fusionner stats_teams avec teams_ids sur le nom de l'équipe
merged_stats_teams = pd.merge(stats_teams, teams_ids, left_on='club', right_on='team', how='left')

# Fusionner ensuite avec clubs_filtered en utilisant l'id kaggle
final_merged_data = pd.merge(merged_stats_teams, clubs_filtered, left_on='id_kaggle', right_on='club_id', how='left')

# Afficher les premières lignes pour vérifier le résultat
print(final_merged_data.head())

# Sauvegarder le fichier final dans un CSV
final_merged_data.to_csv('datasets/final_merged_data.csv', index=False)
