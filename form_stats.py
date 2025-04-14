import os
from form_visu import *
import pandas as pd

# Directories
project_dir = os.getcwd()
data_folder = os.path.join(project_dir, "datasets")
result_folder = os.path.join(project_dir, "results_final", "3_form_stats")

# Charger les données
df_matchs = pd.read_csv(os.path.join(data_folder, "matches.csv"))
df_classements = pd.read_csv(os.path.join(data_folder, "table_leagues.csv"))
df_teams = pd.read_csv(os.path.join(data_folder, "stats_teams.csv"))

# Calculate rollai scored over last 3 matches
def compute_rolling_stat(df, stat_col, agg_func="sum", window=3):

    home_col = f"home_{stat_col}"
    away_col = f"away_{stat_col}"

    if home_col not in df.columns or away_col not in df.columns:
        raise ValueError(f"Missing one or both of columns: '{home_col}' and '{away_col}'")

    # Combine home and away stats
    long_df = pd.concat([
        df[["season", "matchday", "home_team", home_col]].rename(
            columns={"home_team": "team", home_col: "value"}
        ),
        df[["season", "matchday", "away_team", away_col]].rename(
            columns={"away_team": "team", away_col: "value"}
        )
    ])

    # Sort and compute match order
    long_df = long_df.sort_values(by=["team", "season", "matchday"]).reset_index(drop=True)
    long_df["match_order"] = long_df.groupby(["team", "season"]).cumcount()

    # Compute rolling
    rolling_df = (
        long_df[["team", "season", "match_order", "value"]]
        .set_index("match_order")
        .groupby(["team", "season"])["value"]
        .rolling(window=window, min_periods=1)
        .agg(agg_func)
        .reset_index()
        .rename(columns={"value": f"{stat_col}_last_{window}"})
    )

    # Merge back
    result = long_df.merge(rolling_df, on=["team", "season", "match_order"], how="left")
    return result.drop(columns=["value"])


def merge_rolling_stats(df, rolling_stats, stat_name, new_col_prefix, window=3):
    
    # Make sure home and away match orders are available
    if "home_match_order" not in df.columns:
        df["home_match_order"] = df.groupby(["home_team", "season"]).cumcount()
    if "away_match_order" not in df.columns:
        df["away_match_order"] = df.groupby(["away_team", "season"]).cumcount()

    # Merge home stat
    df = df.merge(
        rolling_stats.rename(columns={f"{stat_name}_last_{window}": f"home_{new_col_prefix}"}),
        left_on=["home_team", "season", "home_match_order"],
        right_on=["team", "season", "match_order"],
        how="left"
    ).drop(columns=["team", "match_order"])

    # Merge away stat
    df = df.merge(
        rolling_stats.rename(columns={f"{stat_name}_last_{window}": f"away_{new_col_prefix}"}),
        left_on=["away_team", "season", "away_match_order"],
        right_on=["team", "season", "match_order"],
        how="left"
    ).drop(columns=["team", "match_order"])

    df = df.drop(columns=["matchday"])

    # Clean matchday columns
    matchday_cols = [col for col in df.columns if col.startswith("matchday")]
    if "matchday_x" in matchday_cols:
        df = df.rename(columns={"matchday_x": "matchday"})
    if "matchday_y" in matchday_cols:
        df = df.drop(columns=["matchday_y"])

    return df

stat_cols = [
    'points',
    'shot_attempts',
    'yellow_cards',
    'saves',
    'possession',
    'score',
    'goals_conceded'
]

averaging_stats = [
    'shot_attempts', 'saves', 'possession'
]

# Make sure your df is named df_matchs
df = df_matchs.copy()

# Compute extra features
df["home_goals_conceded"] = df["away_score"]
df["away_goals_conceded"] = df["home_score"]
df["home_points"] = (df["home_score"] > df["away_score"]) * 3 + (df["home_score"] == df["away_score"]) * 1
df["away_points"] = (df["away_score"] > df["home_score"]) * 3 + (df["away_score"] == df["home_score"]) * 1
df["home_win"] = (df["home_score"] > df["away_score"]).astype(int)
df["away_win"] = (df["home_score"] < df["away_score"]).astype(int)


df = df.dropna()

# Rolling match statistics
for stat in stat_cols:
    if stat in averaging_stats:
        rolling_stats = compute_rolling_stat(df, stat, agg_func="mean", window=3)
    else:
        rolling_stats = compute_rolling_stat(df, stat, agg_func="sum", window=3)

    df = merge_rolling_stats(df, rolling_stats, stat_name=stat, new_col_prefix=f"{stat}_last_3")


# ====== GOALS SCORED - CONCEEDED FORM ======

# Prepare home side
home = df[["season", "home_team", "home_score_last_3", "home_goals_conceded_last_3", "home_win"]].copy()
home.columns = ["season", "team", "score_last_3", "conceded_last_3", "win"]

# Prepare away side
away = df[["season", "away_team", "away_score_last_3", "away_goals_conceded_last_3", "away_win"]].copy()
away.columns = ["season", "team", "score_last_3", "conceded_last_3", "win"]

# Combine both sides
combined = pd.concat([home, away], ignore_index=True)

# Group and compute win rates
scored = combined.groupby("score_last_3")["win"].mean().reset_index()
scored["type"] = "Goals Scored"
scored = scored.rename(columns={"score_last_3": "goals", "win": "win_rate"})

conceded = combined.groupby("conceded_last_3")["win"].mean().reset_index()
conceded["type"] = "Goals Conceded"
conceded = conceded.rename(columns={"conceded_last_3": "goals", "win": "win_rate"})

df_full = pd.concat([scored, conceded], ignore_index=True)

plot_win_rate_by_goals_scored_and_conceded(df_full, result_folder, "goals_form_win_rate.png")


# ====== GOALS SCORED - WIN RATE (BY LEAGUE) ======

# Prepare home side
home = df[["league", "home_team", "home_score_last_3", "home_win"]].copy()
home.columns = ["league", "team", "score_last_3", "win"]

# Prepare away side
away = df[["league", "away_team", "away_score_last_3", "away_win"]].copy()
away.columns = ["league", "team", "score_last_3", "win"]

# Combine both
df_full = pd.concat([home, away], ignore_index=True)

plot_goals_boxplot(df_full, result_folder, "goals_form_by_league.png")


# ====== ATTACK FORM - GOALS SCORED ======

# Prepare home side
home = df[["home_team", "home_possession_last_3", "home_shot_attempts_last_3", "home_score"]].copy()
home.columns = ["team", "possession", "shots", "goals"]

# Prepare away side
away = df[["away_team", "away_possession_last_3", "away_shot_attempts_last_3", "away_score"]].copy()
away.columns = ["team", "possession", "shots", "goals"]

# Combine both sides
df_full = pd.concat([home, away], ignore_index=True)

plot_possession_shots_goals_heatmap(df_full, result_folder, "attack_form_goals.png")


# ====== DEFENSE FORM - GOALS CONCEEDED 

# Prepare home side
home = df[[
    "home_team",
    "home_yellow_cards_last_3",
    "home_saves_last_3",
    "home_goals_conceded_last_3"
]].copy()
home.columns = ["team", "yellow_cards", "saves", "goals_conceded"]

# Prepare away side
away = df[[
    "away_team",
    "away_yellow_cards_last_3",
    "away_saves_last_3",
    "away_goals_conceded_last_3"
]].copy()
away.columns = ["team", "yellow_cards", "saves", "goals_conceded"]

# Combine
combined = pd.concat([home, away], ignore_index=True)

plot_yellows_saves_goals_conceded_heatmap(combined, result_folder, "defense_form_goals.png")

# ====== POINTS FORM - WIN RATE BY LEAGUE  ====

rolling_stats = compute_rolling_stat(df, "points", agg_func="sum", window=5)
df = merge_rolling_stats(df, rolling_stats, stat_name="points", new_col_prefix=f"points_last_5", window=5)

print(df.columns)

# Prepare home side
home = df[["league", "home_team", "home_points_last_5", "home_win"]].copy()
home.columns = ["league", "team", "points_last_5", "win"]

# Prepare away side
away = df[["league", "away_team", "away_points_last_5", "away_win"]].copy()
away.columns = ["league", "team", "points_last_5", "win"]

# Combine home and away sides
combined = pd.concat([home, away], ignore_index=True)

plot_win_rate_by_recent_points(combined, result_folder, "points_form_by_league.png")