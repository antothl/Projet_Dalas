import pandas as pd 
import os 
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm

# Directories
project_dir = os.getcwd()
data_folder = os.path.join(project_dir, "datasets")
result_folder = os.path.join(project_dir, "results_final", "2_opponent_stats")

# ====== IMPORT DATA ======
df_matchs = pd.read_csv(os.path.join(data_folder, "matches.csv"))
df_tables = pd.read_csv(os.path.join(data_folder, "table_leagues.csv"))
df_teams = pd.read_csv(os.path.join(data_folder, "stats_teams.csv"))


# ====== GET POSITIONAL GAP STATISTIC ======

# 1) Merge: get AWAY position at each matchday
df_away = pd.merge(
    df_matchs,
    df_tables[["league", "season", "matchday", "club", "position"]],
    how="left",
    left_on=["league", "season", "matchday", "away_team"],
    right_on=["league", "season", "matchday", "club"]
).rename(columns={"position": "away_position", "club": "away_club_in_tables"})

# 2) Merge: get HOME position at each matchday
df_full = pd.merge(
    df_away,
    df_tables[["league", "season", "matchday", "club", "position"]],
    how="left",
    left_on=["league", "season", "matchday", "home_team"],
    right_on=["league", "season", "matchday", "club"]
).rename(columns={"position": "home_position", "club": "home_club_in_tables"})

# 4) Define pos_gap and goals_conceded_away (i.e., home_score)
df_full["pos_gap"] = df_full["away_position"] - df_full["home_position"]
df_full["goals_conceded_away"] = df_full["home_score"]

# Drop any rows with missing needed columns
df_full = df_full.dropna(subset=["pos_gap", "goals_conceded_away"])
df_full["home_win"] = (df_full["home_score"] > df_full["away_score"]).astype(int)


# Group by pos_gap and calculate mean home win rate
win_rate_by_gap = df_full.groupby("pos_gap")["home_win"].mean().reset_index()

# Linear regression: away_score ~ pos_gap
X = sm.add_constant(df_full["pos_gap"])
y = df_full["away_score"]

model = sm.OLS(y, X)
result = model.fit()
print(result.summary())


delta = result.params["pos_gap"]
impact_per_5 = delta * 5
print(f"For every 5-position increase in pos_gap, away score changes by {impact_per_5:.2f} goals.")

# plt.figure(figsize=(8, 5))
# sns.regplot(x="pos_gap", y="away_score", data=df_full, scatter_kws={'alpha':0.5}, line_kws={'color':'red'})
# plt.title("Away Score vs. Positional Gap")
# plt.xlabel("Positional Gap (Away Position - Home Position)")
# plt.ylabel("Away Team Score")
# plt.grid(True)
# plt.tight_layout()
# plt.show()


# ==== TEAM VALUE STATISTIC ====== 

df_teams_filtered = df_teams[["league", "season", "club", "sum_value"]]

# Step 2: Merge home team market value
df_matchs = df_matchs.merge(
    df_teams_filtered,
    left_on=["league", "season", "home_team"],
    right_on=["league", "season", "club"],
    how="left"
).rename(columns={"sum_value": "home_team_value"}).drop(columns=["club"])

# Step 3: Merge away team market value
df_matchs = df_matchs.merge(
    df_teams_filtered,
    left_on=["league", "season", "away_team"],
    right_on=["league", "season", "club"],
    how="left"
).rename(columns={"sum_value": "away_team_value"}).drop(columns=["club"])

df_matchs["realtive_value_difference"] = df_matchs['home_team_value'] - df_matchs['away_team_value']
df_matchs = df_matchs.dropna(subset=["home_score", "home_team_value", "away_team_value"])


# Define the independent and dependent variables
X = sm.add_constant(df_matchs["realtive_value_difference"])
y = df_matchs["home_score"]

# Fit linear regression
model = sm.OLS(y, X)
result = model.fit()

# Show summary
print(result.summary())

coef = result.params["realtive_value_difference"]
impact_5m = coef * 100_000_000
print(f"For every €100M increase in relative team value, home goals increase by {impact_5m:.3f}")

plt.figure(figsize=(8, 5))
sns.regplot(x="realtive_value_difference", y="home_score", data=df_matchs, scatter_kws={'alpha':0.4}, line_kws={'color':'red'})
plt.title("Home Team Goals vs. Relative Team Value Difference")
plt.xlabel("Relative Value Difference (€)")
plt.ylabel("Home Team Goals")
plt.grid(True)
plt.tight_layout()
plt.show()

