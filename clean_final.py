import os
from utils import *
from visualizations import *
import pandas as pd
from scipy.stats import mannwhitneyu

project_dir = os.getcwd()
data_folder = os.path.join(project_dir, "datasets")
result_folder = os.path.join(project_dir, "results")

# Charger les données
df_matchs = pd.read_csv(os.path.join(data_folder, "matches.csv"))
df_tables = pd.read_csv(os.path.join(data_folder, "table_leagues.csv"))
df_players = pd.read_csv(os.path.join(data_folder, "player_values.csv"))
df_goals = pd.read_csv(os.path.join(data_folder, "goalscorers_leagues.csv"))
df_teams = pd.read_csv(os.path.join(data_folder, "stats_teams.csv"))

# Rename columns to all be corresponding to eachother
df_matchs = df_matchs.rename(columns={
    'Journee': 'matchday',
    'Date': 'date',
    'Equipe 1': 'home_team',
    'Score 1': 'home_score',
    'Score 2': 'away_score',
    'Equipe 2': 'away_team',
    'Championnat': 'league',
    'Saison': 'season',
    'Ville': 'city',
    'Temp Max': 'temp_max',
    'Temp Min': 'temp_min',
    'Precipitations': 'precipitations'
})

df_players = df_players.rename(columns={
    'Championnat': 'league',
    'Saison': 'season',
    'Club': 'club',
    'Joueur': 'player',
    'Date de Naissance': 'birthdate',
    'Valeur Marchande': 'market_value'
})

df_tables = df_tables.rename(columns={
    'Championnat': 'league',
    'Saison': 'season',
    'Equipe': 'club',
    'Position': 'position',
    'V': 'wins',
    'N': 'draws',
    'D': 'losses',
    'Buts Pour': 'goals_for',
    'Buts Contre': 'goals_against',
    'Difference': 'goal_difference',
    'Points': 'points'
})

df_teams = df_teams.rename(columns={
    'league': 'league',
    'season': 'season',
    'club': 'club',
    'mean_value': 'mean_value',
    'sum_value': 'sum_value',
    'max_value': 'max_value',
    'avg_age': 'avg_age',
    'total_attack_value': 'total_attack_value',
    'total_defense_value': 'total_defense_value',
    'total_midfield_value': 'total_midfield_value',
    'Missing': 'missing'
})

df_goals = df_goals.rename(columns={
    'Championnat': 'league',
    'Saison': 'season',
    'Joueur': 'player',
    'Équipe': 'club',
    'Buts': 'goals'
})


league_map = {
    'la-liga': 'La Liga',
    'LaLiga': 'La Liga',
    'Liga': 'La Liga',
    'ligue-1': 'Ligue 1',
    'Ligue 1': 'Ligue 1',
    'bundesliga-1': 'Bundesliga',
    'Bundesliga': 'Bundesliga',
    'premier-league': 'Premier League',
    'Premier League': 'Premier League',
    'serie-a': 'Serie A',
    'Serie A': 'Serie A'
}

df_matchs['league'] = df_matchs['league'].replace(league_map)
df_tables['league'] = df_tables['league'].replace(league_map)
df_players['league'] = df_players['league'].replace(league_map)
df_goals['league']   = df_goals['league'].replace(league_map)
df_teams['league']   = df_teams['league'].replace(league_map)


# Save all DataFrames to CSV
df_matchs.to_csv(os.path.join(data_folder, "matches.csv"), index=False)
df_tables.to_csv(os.path.join(data_folder, "table_leagues.csv"), index=False)
df_players.to_csv(os.path.join(data_folder, "player_values.csv"), index=False)
df_goals.to_csv(os.path.join(data_folder, "goalscorers_leagues.csv"), index=False)
df_teams.to_csv(os.path.join(data_folder, "stats_teams.csv"), index=False)