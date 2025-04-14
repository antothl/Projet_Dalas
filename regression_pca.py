import os
import pandas as pd

# Directories
project_dir = os.getcwd()
data_folder = os.path.join(project_dir, "datasets")
result_folder = os.path.join(project_dir, "results_final", "2_opponent_stats")

# ====== IMPORT DATA ======
df_matchs = pd.read_csv(os.path.join(data_folder, "matches.csv"))
df_tables = pd.read_csv(os.path.join(data_folder, "table_leagues.csv"))
df_teams = pd.read_csv(os.path.join(data_folder, "stats_teams.csv"))

print(df_matchs.columns)

regression_features_df = df_matchs[['league', 'season', 'matchday', 'date', 'home_team', 'home_score', 'away_score', 'away_team']]

# ====== CREATE FEATURES ======

# 1. ATTACK POTENTIAL