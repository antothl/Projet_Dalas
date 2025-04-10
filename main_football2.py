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
df_classements = pd.read_csv(os.path.join(data_folder, "classements_5_grands_championnats.csv"))

# ==== 1. DATA CLEAN ===== #

# Create table with ids for unique values for teams, players and leagues
if not os.path.exists(os.path.join(data_folder, "league_ids.csv")):
    create_id_tables(data_folder)

# Create general table with general statistics of teams
if not os.path.exists(os.path.join(data_folder, "stats_teams.csv")):
    df_teams = create_summary_stats_teams(data_folder)
else:
    df_teams = pd.read_csv(os.path.join(data_folder, "stats_teams.csv"))

df_teams["attack_value_ratio"] = df_teams["total_attack_value"] / df_teams["sum_value"]
df_teams["midfield_value_ratio"] = df_teams["total_midfield_value"] / df_teams["sum_value"]
df_teams["defense_value_ratio"] = df_teams["total_defense_value"] / df_teams["sum_value"]

# Clean team names for columns
df_matchs = clean_matching_names(df_classements, df_matchs, data_folder)

# Process match table to contain more detailed information
df_matchs = process_matches_table(df_teams, df_matchs, data_folder)

# Clean matches dataset for correct league names
df_matchs = clean_matches_league_names(df_matchs, data_folder)

# Assuming your DataFrame is called df and Journee is numeric
df_classements['Journee'] = pd.to_numeric(df_matchs['Journee'], errors='coerce')  # convert non-numeric to NaN
df_classements = df_classements.dropna(subset=['Journee'])                             # drop rows where Journee is NaN
df_classements['Journee'] = df_classements['Journee'].astype(int)                      # optional: convert to int
# Get the last journee per group
last_journee = df_classements.groupby(['Saison', 'Championnat', 'Equipe'])['Journee'].transform('max')

# Keep only rows where journee is the last for that team/league/season
last_day_stats = df_classements[df_classements['Journee'] == last_journee].reset_index(drop=True)

# 
last_day_stats = last_day_stats.rename(columns={
    'Saison': 'season',
    'Championnat': 'league',
    'Journee': 'matchday',
    'Position': 'position',
    'Equipe': 'club',
    'V': 'wins',
    'N': 'draws',
    'D': 'losses',
    'Buts Pour': 'goals_for',
    'Buts Contre': 'goals_against',
    'Difference': 'goal_difference',
    'Points': 'points'
})


df_teams_current = df_teams[['league', 'season', 'club', 'attack_value_ratio',
       'midfield_value_ratio', 'defense_value_ratio']]
last_day_stats = last_day_stats[['season', 'league', 'club', 'position', 'goals_against', 'goal_difference', 'points']]

merged_df = pd.merge(df_teams, last_day_stats, on=['season', 'league', 'club'], how='inner')

df_teams_current = df_teams_current[df_teams_current['season'] == 2023]
last_day_stats = last_day_stats[last_day_stats['season'] == 2023]
df_teams_current['league'] = df_teams_current.replace
df_teams_current = df_teams_current[df_teams_current['league'].isin(['Ligue 1', 'Premier League', 'La Liga'])]

print(last_day_stats['league'].unique())
print(df_teams_current['league'].unique())

sorted_teams_clubs = sorted(df_teams_current['club'].unique())
sorted_table_clubs = sorted(last_day_stats['club'].unique())
print(len(sorted_table_clubs))
for i in range(5):
    print(sorted_teams_clubs[i])
    print(sorted_table_clubs[i])

