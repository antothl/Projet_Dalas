import pandas as pd 
import os 
from opponent_visu import *
from scipy.stats import mannwhitneyu
from scipy.stats import shapiro

# Directories
project_dir = os.getcwd()
data_folder = os.path.join(project_dir, "datasets")
result_folder = os.path.join(project_dir, "results_final", "2_opponent_stats")

# ====== IMPORT DATA ======
df_matchs = pd.read_csv(os.path.join(data_folder, "matches.csv"))
df_tables = pd.read_csv(os.path.join(data_folder, "table_leagues.csv"))
df_teams = pd.read_csv(os.path.join(data_folder, "stats_teams.csv"))

# ====== ATTACK HOME <-> DEFENSE AWAY POTENTIAL ======
# Merge home team ratios
df_home = pd.merge(
    df_matchs,
    df_teams[["league", "season", "club", "total_attack_value", "total_defense_value"]],
    how="left",
    left_on=["league", "season", "home_team"],
    right_on=["league", "season", "club"]
).rename(columns={
    "total_attack_value": "home_attack_value",
    "total_defense_value": "home_defense_value",
    "club": "home_club"
})

# Merge away team ratios
df_full = pd.merge(
    df_home,
    df_teams[["league", "season", "club", "total_attack_value", "total_defense_value"]],
    how="left",
    left_on=["league", "season", "away_team"],
    right_on=["league", "season", "club"]
).rename(columns={
    "total_attack_value": "away_attack_value",
    "total_defense_value": "away_defense_value",
    "club": "away_club"
})

# We use home_attack_value / away_defense_value
df_full["home_attack_defense_ratio"] = (
    df_full["home_attack_value"] / df_full["away_defense_value"]
)

# Plot results
attack_defense_potential(df_full, result_folder, "attack_defense_potential.png")


# # ==== DEFENSE POTENTIAL AWAY <-> GOALS CONCEEDED ===== # #

# 1) Merge: get AWAY position at each matchday
df_away = pd.merge(
    df_matchs,
    df_tables[["league", "season", "matchday", "club", "position"]],
    how="left",
    left_on=["league", "season", "matchday", "away_team"],
    right_on=["league", "season", "matchday", "club"]
).rename(columns={"position": "away_position", "club": "away_club_in_tables"})

# 2) Merge: get HOME position at each matchday
df_away_home = pd.merge(
    df_away,
    df_tables[["league", "season", "matchday", "club", "position"]],
    how="left",
    left_on=["league", "season", "matchday", "home_team"],
    right_on=["league", "season", "matchday", "club"]
).rename(columns={"position": "home_position", "club": "home_club_in_tables"})

# 3) Merge: get AWAY defensive value
df_full = pd.merge(
    df_away_home,
    df_teams[["league", "season", "club", "total_defense_value"]],
    how="left",
    left_on=["league", "season", "away_team"],
    right_on=["league", "season", "club"]
).rename(columns={
    "total_defense_value": "away_defense_value",
    "club": "away_club_in_teams"
})

# 4) Define pos_gap and goals_conceded_away (i.e., home_score)
df_full["pos_gap"] = df_full["away_position"] - df_full["home_position"]
df_full["goals_conceded_away"] = df_full["home_score"]

# Drop any rows with missing needed columns
df_full = df_full.dropna(subset=["pos_gap", "away_defense_value", "goals_conceded_away"])

# 5) Create bins for pos_gap and away_defense_value
df_full["pos_gap_bin"] = pd.cut(df_full["pos_gap"], bins=5)
df_full["away_defense_bin"] = pd.qcut(df_full["away_defense_value"], q=5, duplicates="drop")

# Plot defensive potential away team
defensive_potential(df_full, result_folder, "defense_potential.png")

# ====== GOALS SCORED (HOME) - GOALS CONCEEDED (AWAY) ======

# 1) Aggregate HOME stats
df_home = (
    df_matchs
    .groupby(["home_team", "season"])
    .agg(
        avg_goals_scored_home=("home_score", "mean"),
        avg_goals_conceded_home=("away_score", "mean")
    )
    .reset_index()
    .rename(columns={"home_team": "team"})
)

# 2) Aggregate AWAY stats
df_away = (
    df_matchs
    .groupby(["away_team", "season"])
    .agg(
        avg_goals_scored_away=("away_score", "mean"),
        avg_goals_conceded_away=("home_score", "mean")
    )
    .reset_index()
    .rename(columns={"away_team": "team"})
)

# 3) Merge HOME & AWAY tables
df_merged = pd.merge(
    df_home, 
    df_away, 
    on=["team", "season"], 
    how="inner"
)

# 4) Melt into long format
df_melted = df_merged.melt(
    id_vars=["team", "season"], 
    value_vars=[
        "avg_goals_scored_home", "avg_goals_scored_away",
        "avg_goals_conceded_home", "avg_goals_conceded_away"
    ],
    var_name="variable",
    value_name="goals"
)

plot_violin_goals(df_melted, result_folder, "goal_H_A_differences.png")

# ====== EXTRA STATISTICAL TEST: to prove distribution is indeed different ======
# Apply Mann-Whitney U Test
home_scored = df_merged['avg_goals_scored_home']
away_scored = df_merged['avg_goals_scored_away']

home_conceded = df_merged['avg_goals_conceded_home']
away_conceded = df_merged['avg_goals_conceded_away']

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


# ====== PREVIOUS GAMES ANALYSES ====== #

# 1) Filter for seasons 2021 and 2022
df_prev = df_matchs[df_matchs['season'].isin([2021, 2022])].copy()

# 2) Compute points for home side
# 1 point if equal, else 0 points
df_prev['points_home'] = np.where(
    df_prev['home_score'] > df_prev['away_score'], 
    3, 
    np.where(df_prev['home_score'] == df_prev['away_score'], 1, 0)
)

df_prev['points_away'] = np.where(
    df_prev['away_score'] > df_prev['home_score'], 
    3, 
    np.where(df_prev['away_score'] == df_prev['home_score'], 1, 0)
)

# 4) Unpivot so each match -> 2 rows: (team, opponent, points)
#    Row 1 for home_team, Row 2 for away_team
rows_list = []
for idx, row in df_prev.iterrows():
    rows_list.append({
        'team': row['home_team'],
        'opponent': row['away_team'],
        'points': row['points_home']
    })
    rows_list.append({
        'team': row['away_team'],
        'opponent': row['home_team'],
        'points': row['points_away']
    })
df_unpivot = pd.DataFrame(rows_list)

# 5) Group by (team, opponent) to get total points in 2021-22 matchups
df_history = (
    df_unpivot
    .groupby(['team', 'opponent'], as_index=False)['points']
    .sum()
    .rename(columns={'points': 'points_2021_2022'})
)

# 1) Filter for 2023 matches
df_2023 = df_matchs[df_matchs['season'] == 2023].copy()

# 2) Merge to find how many points the HOME team (vs. AWAY team) got in 2021-2022
df_2023 = df_2023.merge(
    df_history, 
    how='left', 
    left_on=['home_team', 'away_team'], 
    right_on=['team', 'opponent']
)
# Column 'points_2021_2022' = total points home_team earned against away_team
df_2023.rename(columns={'points_2021_2022': 'home_prev_points'}, inplace=True)

# Drop the merge helper columns
df_2023.drop(columns=['team', 'opponent'], inplace=True)

# 3) Merge again for AWAY side’s perspective
df_2023 = df_2023.merge(
    df_history, 
    how='left', 
    left_on=['away_team', 'home_team'], 
    right_on=['team', 'opponent']
)
# Column 'points_2021_2022' = total points away_team earned against home_team
df_2023.rename(columns={'points_2021_2022': 'away_prev_points'}, inplace=True)

df_2023.drop(columns=['team', 'opponent'], inplace=True)

# If some matchups never occurred in 2021-22, fill NaN with 0
df_2023['home_prev_points'] = df_2023['home_prev_points'].fillna(0)
df_2023['away_prev_points'] = df_2023['away_prev_points'].fillna(0)

prob_winning_home_away(df_2023, result_folder, "prob_win_prevgames.png")