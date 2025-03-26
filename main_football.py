import os
from utils import *
from visualizations import *
import pandas as pd
from scipy.stats import mannwhitneyu

project_dir = os.getcwd()
data_folder = os.path.join(project_dir, "datasets")
result_folder = os.path.join(project_dir, "results")

# Charger les données
df_matchs = pd.read_csv(os.path.join(data_folder, "matches_updated.csv"))
df_classements = pd.read_csv(os.path.join(data_folder, "classements_5_grands_championnats.csv"))
df_teams = pd.read_csv(os.path.join(data_folder, "stats_teams.csv"))

# ==== 1. DATA CLEAN ===== #

# Create table with ids for unique values for teams, players and leagues
if not os.path.exists(os.path.join(data_folder, "league_ids.csv")):
    create_id_tables(data_folder)

# Create general table with general statistics of teams
if not os.path.exists(os.path.join(data_folder, "stats_teams2.csv")):
    df_team_stats = create_summary_stats_teams(data_folder)
else:
    df_team_stats = pd.read_csv(os.path.join((data_folder, "stats_teams2.csv")))

print(df_team_stats.head())

# Clean team names for columns
clean_matching_names(data_folder)

# Process match table to contain more detailed information
process_matches_table(data_folder)

# Clean matches dataset for correct league names
clean_matches_league_names(df_matchs, data_folder)

# ==== 2. START INITIAL VISUALS ===== #

# Plot performances home games for each league
leagues_performances(df_matchs, result_folder)

# Plot performances in different weather conditions
plot_weather_impact(df_matchs, result_folder)

# Plot win-average market value correlations for each league
plot_win_value_corr(data_folder, result_folder)

match_mv_pearson(df_matchs, result_folder)

df_merged = merge_table_matches(df_matchs, df_classements)

# Prepare additional features
df_merged["goal_diff_gap"] = df_merged["Difference_t1"] - df_merged["Difference_t2"]
df_merged["offense_score_t1"] = df_merged["Buts Pour_t1"] - df_merged["Buts Contre_t2"]
df_merged["points_gap"] = df_merged["Points_t1"] - df_merged["Points_t2"]
df_merged["rank_diff"] = df_merged["Position_t2"] - df_merged["Position_t1"]
df_merged["result_label"] = df_merged["result_t1"].map({0.0: "L", 0.5: "D", 1.0: "W"})

goals_rankings_results_plots(df_merged, result_folder)

# Build home team rows
home_df = df_matchs[["Score 1", "Score 2"]].copy()
home_df.columns = ["goals_scored", "goals_conceded"]
home_df["location"] = "Home"

# Build away team rows
away_df = df_matchs[["Score 2", "Score 1"]].copy()
away_df.columns = ["goals_scored", "goals_conceded"]
away_df["location"] = "Away"

# Combine both
df_goals = pd.concat([home_df, away_df], ignore_index=True)

goals_home_away(df_goals, result_folder)

# Separate goals by location
home_scored = home_df["goals_scored"]
away_scored = away_df["goals_scored"]
home_conceded = home_df["goals_conceded"]
away_conceded = away_df["goals_conceded"]

# Apply Mann-Whitney U Test
stat_scored, p_scored = mannwhitneyu(home_scored, away_scored, alternative="two-sided")
stat_conceded, p_conceded = mannwhitneyu(home_conceded, away_conceded, alternative="two-sided")

# Save results in a table
test_results = pd.DataFrame({
    "Test": ["Goals Scored", "Goals Conceded"],
    "U Statistic": [stat_scored, stat_conceded],
    "p-value": [p_scored, p_conceded],
    "Significant": [p_scored < 0.05, p_conceded < 0.05]
})

test_results.to_csv(os.path.join(result_folder, "tests_home_away.csv"), index=False)

plot_goals_pleague(df_merged, result_folder)

# print(position_value)