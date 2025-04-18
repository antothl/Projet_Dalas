import os
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
    'day': 'matchday',
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


# Compute total known values
df_teams["calc_sum_value"] = (
    df_teams["total_attack_value"] 
    + df_teams["total_midfield_value"] 
    + df_teams["total_defense_value"]
)

# Now calculate the ratios with respect to the new calc_sum_value
df_teams["attack_value_ratio"] = df_teams["total_attack_value"] / df_teams["calc_sum_value"]
df_teams["midfield_value_ratio"] = df_teams["total_midfield_value"] / df_teams["calc_sum_value"]
df_teams["defense_value_ratio"] = df_teams["total_defense_value"] / df_teams["calc_sum_value"]
df_teams.drop(columns=['calc_sum_value'], inplace=True)

# Convert matchday to int
df_matchs['matchday'] = pd.to_numeric(df_matchs['matchday'], errors='coerce').astype('Int64')

df_matchs.drop(columns=['Unnamed: 0'], inplace=True)

# Save all DataFrames to CSV
df_matchs.to_csv(os.path.join(data_folder, "matches.csv"), index=False)
df_tables.to_csv(os.path.join(data_folder, "table_leagues.csv"), index=False)
df_players.to_csv(os.path.join(data_folder, "player_values.csv"), index=False)
df_goals.to_csv(os.path.join(data_folder, "goalscorers_leagues.csv"), index=False)
df_teams.to_csv(os.path.join(data_folder, "stats_teams.csv"), index=False)