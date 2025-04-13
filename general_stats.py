import os
from general_visu import *
import pandas as pd
from scipy.stats import f_oneway

# Directories
project_dir = os.getcwd()
data_folder = os.path.join(project_dir, "datasets")
result_folder = os.path.join(project_dir, "results_final", "1_general_stats")

# Charger les données
df_matchs = pd.read_csv(os.path.join(data_folder, "matches.csv"))
df_classements = pd.read_csv(os.path.join(data_folder, "table_leagues.csv"))
df_teams = pd.read_csv(os.path.join(data_folder, "stats_teams.csv"))

# ====== VALUE - GOAL STATS ======
# Assuming your DataFrame 
df_classements['matchday'] = pd.to_numeric(df_classements['matchday'], errors='coerce')  # convert non-numeric to NaN
df_classements_filter = df_classements.dropna(subset=['matchday'])                             # drop rows where Journee is NaN
df_classements_filter['matchday'] = df_classements_filter['matchday'].astype(int)                      # optional: convert to int

# Get the last matchday per group
last_matchday_stats = df_classements_filter.groupby(['season', 'league', 'club'])['matchday'].transform('max')

# Keep only rows where journee is the last for that team/league/season
last_day_stats = df_classements[df_classements['matchday'] == last_matchday_stats].reset_index(drop=True)

# Select relevant columns
df_teams_current = df_teams[['league', 'season', 'club', 'attack_value_ratio',
    'midfield_value_ratio', 'defense_value_ratio']]
last_day_stats = last_day_stats[['season', 'league', 'club', 'goals_for', 'goals_against', 'goal_difference', 'points']]

# Table of team values and goal stats of last game day
merged_table_teams = pd.merge(df_teams, last_day_stats, on=['season', 'league', 'club'], how='inner')
merged_table_teams = merged_table_teams[['attack_value_ratio', 'midfield_value_ratio', 'defense_value_ratio',
                                         'goals_for', 'goals_against', 'goal_difference']]

# Define variables
x_vars = ['attack_value_ratio', 'midfield_value_ratio', 'defense_value_ratio']
y_vars = ['goals_for', 'goal_difference', 'goals_against']

# Plot correlations
value_goals_correlation(merged_table_teams, x_vars, y_vars, result_folder, "scatter_matrix_value_goals.png")

# ====== AVERAGE AGE - INJURIES - MARKET VALUE ======
# Import data
kaggle_data = os.path.join(project_dir, "datasets", "kaggle_data")
df_clubs = pd.read_csv(os.path.join(kaggle_data, "clubs.csv"))
df_competitions = pd.read_csv(os.path.join(kaggle_data, "competitions.csv"))
df_games = pd.read_csv(os.path.join(kaggle_data, "games.csv"))
df_events = pd.read_csv(os.path.join(kaggle_data, "game_events.csv"))

# Filter clubs for only the major european leagues
df_competitions = df_competitions[df_competitions['is_major_national_league'] == True].reset_index(drop=True)
df_competitions = df_competitions[['competition_id', 'competition_code', 'name',
       'country_id', 'country_name', 'domestic_league_code', 'confederation']]

# Filter clubs based on those leagues
df_clubs = df_clubs[df_clubs['domestic_competition_id'].isin(df_competitions['competition_id'].unique())].reset_index(drop=True)

# Filter games for only clubs in major leagues
df_games = df_games[df_games['home_club_id'].isin(df_clubs['club_id'].unique())].reset_index(drop=True)
df_games = df_games[df_games['away_club_id'].isin(df_clubs['club_id'].unique())].reset_index(drop=True)
df_games = df_games[['game_id', 'competition_id', 'season', 'round', 'date', 'home_club_id',
       'away_club_id', 'home_club_goals', 'away_club_goals',
       'home_club_position', 'away_club_position']]

# Filter events for only relevant games
df_events = df_events[df_events['game_id'].isin(df_games['game_id'].unique())].reset_index(drop=True)

# Injury events
df_injuries = df_events[df_events['description'].str.contains('injury', case=False, na=False)].reset_index(drop=True)

# Count injuries per game and club
injury_counts = df_injuries.groupby(['game_id', 'club_id']).size().reset_index(name='injury_count')

# Merge injuries with games
df_merged = df_games.copy()

# Merge home injuries
df_merged = df_merged.merge(
    injury_counts, 
    left_on=['game_id', 'home_club_id'], 
    right_on=['game_id', 'club_id'], 
    how='left'
).rename(columns={'injury_count': 'home_injuries'}).drop(columns=['club_id'])

# Merge away injuries
df_merged = df_merged.merge(
    injury_counts, 
    left_on=['game_id', 'away_club_id'], 
    right_on=['game_id', 'club_id'], 
    how='left'
).rename(columns={'injury_count': 'away_injuries'}).drop(columns=['club_id'])

# Fill missing values (no injuries) with 0
df_merged['home_injuries'] = df_merged['home_injuries'].fillna(0).astype(int)
df_merged['away_injuries'] = df_merged['away_injuries'].fillna(0).astype(int)

# Melt home and away into one injury record per club per game
home_injuries = df_merged[['competition_id', 'season', 'home_club_id', 'home_injuries']].rename(
    columns={'home_club_id': 'club_id', 'home_injuries': 'injuries'}
)
away_injuries = df_merged[['competition_id', 'season', 'away_club_id', 'away_injuries']].rename(
    columns={'away_club_id': 'club_id', 'away_injuries': 'injuries'}
)

# Combine home and away records
injury_records = pd.concat([home_injuries, away_injuries], ignore_index=True)

# Group by competition, season, club and sum injuries
injury_totals = injury_records.groupby(['competition_id', 'season', 'club_id'], as_index=False)['injuries'].sum()

# Merge with club names
injury_totals = injury_totals.merge(df_clubs[['club_id', 'name']], on='club_id', how='left')
injury_totals = injury_totals[['competition_id', 'season', 'club_id', 'name', 'injuries']]
injury_totals = injury_totals[injury_totals['season'].isin([2021, 2022, 2023])]
injury_totals = injury_totals[injury_totals['competition_id'].isin(df_competitions['competition_id'].unique())]

df_team_ids = pd.read_csv(os.path.join(data_folder, "team_ids.csv"))
competitions_ids = pd.read_csv(os.path.join(data_folder, "competitions_ids.csv"))

# Merge injury totals with teams_ids using id_kaggle ↔ club_id
injury_totals_named = injury_totals.merge(
    df_team_ids[['team', 'id_kaggle']],
    left_on='club_id',
    right_on='id_kaggle',
    how='left'
)

# Drop duplicate 'name' and 'id_kaggle' columns if desired
injury_totals_named = injury_totals_named.drop(columns=['name', 'id_kaggle'])

injury_totals_named = injury_totals_named[['competition_id', 'season', 'team', 'injuries']]

# Merge to add league names to the injury totals
injury_totals_full = injury_totals_named.merge(
    competitions_ids,
    on='competition_id',
    how='left'
)

# Rearranged for clarity
injury_totals_full = injury_totals_full[['league', 'season', 'team', 'injuries']]

injury_totals_full = injury_totals_full.sort_values(by=['league', 'team']).reset_index(drop=True)

# Step 1: Clean and align text columns (just to be safe)
df_teams['club'] = df_teams['club'].str.strip()
injury_totals_full['team'] = injury_totals_full['team'].str.strip()

# Step 2: Merge on league, season, and club/team name
df_teams_with_injuries = df_teams.merge(
    injury_totals_full,
    left_on=['league', 'season', 'club'],
    right_on=['league', 'season', 'team'],
    how='left'
)

# Step 3: Drop the redundant 'team' column
df_teams_with_injuries = df_teams_with_injuries.drop(columns=['team'])

# Step 4: Fill NaN injuries with 0 (optional, if some teams had no injuries)
df_teams_with_injuries['injuries'] = df_teams_with_injuries['injuries'].fillna(0).astype(int)


# Simulate a minimal DataFrame for demonstration
sample_df = df_teams_with_injuries[['mean_value', 'avg_age', 'injuries']].dropna()

# Define variables
x_vars = ['injuries', 'mean_value']
y_vars = ['avg_age']

# Plot correlations
value_goals_correlation(df_teams_with_injuries, x_vars, y_vars, result_folder, "value_injury_age.png")

correlation_heatmap(
    df=df_teams_with_injuries,
    cols=['mean_value', 'avg_age', 'injuries'],
    result_folder=result_folder,
    filename='correlations_age_values.png'
)

# ====== MARKET VALUE GAP - TOP 5 vs. BOTTOM 5 ====== 
# Assuming your DataFrame 
df_classements['matchday'] = pd.to_numeric(df_classements['matchday'], errors='coerce')  # convert non-numeric to NaN
df_classements_filter = df_classements.dropna(subset=['matchday'])                             # drop rows where Journee is NaN
df_classements_filter['matchday'] = df_classements_filter['matchday'].astype(int)                      # optional: convert to int

# Get the last matchday per group
last_matchday_stats = df_classements_filter.groupby(['season', 'league', 'club'])['matchday'].transform('max')

# Keep only rows where journee is the last for that team/league/season
last_day_stats = df_classements[df_classements['matchday'] == last_matchday_stats].reset_index(drop=True)

# Merge final standings with teams value info
df_merged = pd.merge(
    last_day_stats,
    df_teams,
    how="left",
    on=["league", "season", "club"]
)

league_stats = []

# Step 1: Compute top/bottom 5 per season
for (league, season), group in df_merged.groupby(["league", "season"]):
    group_sorted = group.sort_values("position")

    n_teams = len(group_sorted)
    top_n = min(5, n_teams)
    bottom_n = min(5, n_teams)

    top_avg = group_sorted.head(top_n)["mean_value"].mean()
    bottom_avg = group_sorted.tail(bottom_n)["mean_value"].mean()

    league_stats.append({
        "league": league,
        "season": season,
        "top_avg_value": top_avg,
        "bottom_avg_value": bottom_avg
    })

# Step 2: Convert to DataFrame
df_seasonal = pd.DataFrame(league_stats)

# Step 3: Group by league and average across seasons
df_league_avg = df_seasonal.groupby("league")[["top_avg_value", "bottom_avg_value"]].mean().reset_index()

plot_avg_top_bottom_by_league(df_league_avg, result_folder, "value_best_worst.png")


# ====== GENERAL MATCH STATISTICS OF EACH LEAGUE ====== 

# 1. Compute per-match totals (home + away)
df_matchs["total_shots_on_goal"] = df_matchs["home_shots_on_goal"] + df_matchs["away_shots_on_goal"]
df_matchs["total_yellow_cards"] = df_matchs["home_yellow_cards"] + df_matchs["away_yellow_cards"]
df_matchs["total_corner_kicks"] = df_matchs["home_corner_kicks"] + df_matchs["away_corner_kicks"]
df_matchs["total_saves"] = df_matchs["home_saves"] + df_matchs["away_saves"]

print(df_matchs.columns)
# 2. Define column name mapping: df column name -> label for plot
column_map = {
    "total_shots_on_goal": "Shots on Goal",
    "total_yellow_cards": "Yellow Cards",
    "total_corner_kicks": "Corner Kicks",
    "total_saves": "Saves"
}

# ANOVA test on match variables per league
anova_results = []
for col, label in column_map.items():
    groups = [
        df_matchs[df_matchs['league'] == league][col].dropna()
        for league in df_matchs['league'].unique()
    ]
    if all(len(g) > 1 for g in groups):
        f_stat, p_val = f_oneway(*groups)
        anova_results.append({
            'Variable': label,
            'F-statistic': f_stat,
            'p-value': p_val
        })

# Save to DataFrame and export
df_anova = pd.DataFrame(anova_results)
df_anova.to_csv(os.path.join(result_folder, "ANOVA_match_statsp_league.csv"), index=False)

# 3. Group by league and compute averages
df_stats = df_matchs.groupby("league")[list(column_map.keys())].mean().reset_index()

# 4. Rename columns to display names
df_stats.rename(columns=column_map, inplace=True)

league_match_stats(df_stats, column_map, df_anova, result_folder, "league_match_stats.png")

