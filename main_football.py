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

# ==== 2. START INITIAL VISUALS ===== #

# Plot performances home games for each league
leagues_performances(df_matchs, result_folder)

# Plot performances in different weather conditions
plot_weather_impact(df_matchs, result_folder)

# Plot win-average market value correlations for each league
plot_win_value_corr(df_matchs, result_folder)

# Plot market values, ages - correlation plots
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


# Create a melted DataFrame for team 1: plot goal difference vs value ratios
df_plot_t1 = df_merged[[
    "Difference_t1",
    "attack_value_ratio_t1",
    "midfield_value_ratio_t1",
    "defense_value_ratio_t1"
]].copy()

df_melted_t1 = df_plot_t1.melt(id_vars="Difference_t1", var_name="Value Ratio Type", value_name="Ratio")

# Plot: Team 1 - Goal Difference vs Value Ratio
plt.figure(figsize=(8, 5))
sns.scatterplot(data=df_melted_t1, x="Ratio", y="Difference_t1", hue="Value Ratio Type")
plt.title("Team 1: Goal Difference vs Value Composition")
plt.xlabel("Value Ratio")
plt.ylabel("Goal Difference")
plt.grid(True, linestyle="--", alpha=0.3)
plt.tight_layout()
plt.show()

# Create a melted DataFrame for team 1: plot goals scored vs value ratios
df_plot_bp_t1 = df_merged[[
    "Buts Pour_t1",
    "attack_value_ratio_t1",
    "midfield_value_ratio_t1",
    "defense_value_ratio_t1"
]].copy()

df_melted_bp_t1 = df_plot_bp_t1.melt(id_vars="Buts Pour_t1", var_name="Value Ratio Type", value_name="Ratio")

# Plot: Team 1 - Goals Scored vs Value Ratio
plt.figure(figsize=(8, 5))
sns.scatterplot(data=df_melted_bp_t1, x="Ratio", y="Buts Pour_t1", hue="Value Ratio Type")
plt.title("Team 1: Goals Scored vs Value Composition")
plt.xlabel("Value Ratio")
plt.ylabel("Goals Scored")
plt.grid(True, linestyle="--", alpha=0.3)
plt.tight_layout()
plt.show()

# Correlation heatmap for team 1 stats
df_corr = df_merged[[
    "Buts Pour_t1", "Buts Contre_t1", "Difference_t1",
    "attack_value_ratio_t1", "midfield_value_ratio_t1", "defense_value_ratio_t1"
]].corr()

plt.figure(figsize=(8, 6))
sns.heatmap(df_corr, annot=True, cmap="coolwarm", fmt=".2f")
plt.title("Team 1: Correlation between Goal Stats and Value Ratios")
plt.tight_layout()
plt.show()