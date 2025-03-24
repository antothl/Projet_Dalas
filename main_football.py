import os
from utils import *
from visualizations import *
import pandas as pd

project_dir = os.getcwd()
data_folder = os.path.join(project_dir, "datasets")
result_folder = os.path.join(project_dir, "results")

# ==== 1. DATA CLEAN ===== #

# Create table with ids for unique values for teams, players and leagues
if not os.path.exists(os.path.join(data_folder, "league_ids.csv")):
    create_id_tables(data_folder)

# Create general table with general statistics of teams
if not os.path.exists(os.path.join(data_folder, "stats_teams.csv")):
    create_summary_stats_teams(data_folder)

# Clean team names for columns
clean_matching_names(data_folder)

# Process match table to contain more detailed information
process_matches_table(data_folder)

# ==== 2. START INITIAL VISUALS ===== #

# Plot performances home games for each league
leagues_performances(data_folder, result_folder)

# Plot performances in different weather conditions
plot_weather_impact(data_folder, result_folder)

# Plot win-average market value correlations for each league
plot_win_value_corr(data_folder, result_folder)
