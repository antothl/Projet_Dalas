import os
import pandas as pd
import numpy as np
from form_stats import compute_rolling_stat, merge_rolling_stats
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from regression_visu import *
import statsmodels.api as sm
from datetime import datetime
from sklearn.linear_model import LogisticRegressionCV
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score, roc_curve, auc
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# Directories
project_dir = os.getcwd()
data_folder = os.path.join(project_dir, "datasets")
result_folder = os.path.join(project_dir, "results_final", "4_regression_analysis")

# ====== IMPORT DATA ======
df_matchs = pd.read_csv(os.path.join(data_folder, "matches.csv"))
df_tables = pd.read_csv(os.path.join(data_folder, "table_leagues.csv"))
df_teams = pd.read_csv(os.path.join(data_folder, "stats_teams.csv"))

# Create regression dataframe
regression_features_df = df_matchs[['league', 'season', 'matchday', 'date', 'home_team', 'home_score', 'away_score', 'away_team']].copy()
regression_features_df['home_win'] = (regression_features_df['home_score'] > regression_features_df['away_score']).astype(int)
regression_features_df['away_win'] = (regression_features_df['away_score'] > regression_features_df['home_score']).astype(int)

# ====== CREATE FEATURES ======

# (A) ATTACK POTENTIAL
# Join team statistics for Home team
regression_features_df = regression_features_df.merge(df_teams[["league", "season", "club", "attack_value_ratio", "defense_value_ratio", "sum_value", "avg_age",
                                                                "total_attack_value", "total_defense_value"]],
                                                      left_on=["league", "season", "home_team"],
                                                      right_on=["league", "season", "club"], how='left').rename(
                                                        columns={"attack_value_ratio": "home_attack_value_ratio",
                                                                 "total_attack_value": "home_attack_value",
                                                                 "total_defense_value": "home_defense_value",
                                                                 "defense_value_ratio": "home_defense_value_ratio",
                                                                 "avg_age": "home_avg_age",
                                                                 "sum_value":"home_team_value"}
                                                        ).drop(columns=["club"])
# Join team statistics for Away team
regression_features_df = regression_features_df.merge(df_teams[["league", "season", "club", "attack_value_ratio", "defense_value_ratio", "sum_value", "avg_age",
                                                                "total_attack_value", "total_defense_value"]],
                                                      left_on=["league", "season", "away_team"],
                                                      right_on=["league", "season", "club"], how='left').rename(
                                                        columns={"attack_value_ratio": "away_attack_value_ratio",
                                                                 "total_attack_value": "away_attack_value",
                                                                 "total_defense_value": "away_defense_value",
                                                                 "defense_value_ratio": "away_defense_value_ratio",
                                                                 "avg_age": "away_avg_age",
                                                                 "sum_value":"away_team_value"}
                                                        ).drop(columns=["club"])


# Join table stats for Home Team
regression_features_df = regression_features_df.merge(df_tables[['season', 'league', 'matchday', 'club',
                                                                'goals_for', 'goals_against']],
                                                        left_on=["league", "season", "matchday", "home_team"],
                                                        right_on=['league', 'season', 'matchday', 'club'], how='left').rename(
                                                            columns={'goals_for': 'home_goals_for',
                                                                     'goals_against': 'home_goals_against'}
                                                        ).drop(columns=['club'])

# Join table stats for away Team
regression_features_df = regression_features_df.merge(df_tables[['season', 'league', 'matchday', 'club',
                                                                'goals_for', 'goals_against']],
                                                        left_on=["league", "season", "matchday", "away_team"],
                                                        right_on=['league', 'season', 'matchday', 'club'], how='left').rename(
                                                            columns={'goals_for': 'away_goals_for',
                                                                     'goals_against': 'away_goals_against'}
                                                        ).drop(columns=['club'])


# ====== (B) SCORING POTENTIAL VS. TEAM ======
regression_features_df["home_score_potential"] = (regression_features_df["home_attack_value"] / regression_features_df["away_defense_value"])*\
                                                    (regression_features_df["home_goals_for"] - regression_features_df["home_goals_against"])
regression_features_df["away_score_potential"] = (regression_features_df["away_attack_value"] / regression_features_df["home_defense_value"])*\
                                                    (regression_features_df["away_goals_for"] - regression_features_df["away_goals_against"])

regression_features_df = regression_features_df.drop(columns=["home_attack_value", "away_attack_value",
                                                              "home_goals_for", "away_goals_for",
                                                              "home_goals_against", "away_goals_against"])


# (B.1) RELATIVE TEAM VALUES AND POTENTIAL
regression_features_df["home_relative_value_team"] = (regression_features_df["home_team_value"] - regression_features_df["away_team_value"])
regression_features_df["away_relative_value_team"] = (regression_features_df["away_team_value"] - regression_features_df["home_team_value"])

regression_features_df = regression_features_df.drop(columns=["home_avg_age", "away_avg_age",
                                                              "home_team_value", "away_team_value"])


# (C) CLEAN SHEET POTENTIAL
# Add positions for each matchday for HOME teams
regression_features_df = regression_features_df.merge(df_tables[["league", "season", "club", "matchday", "position"]],
                                                      left_on=["league", "season", "home_team", "matchday"],
                                                      right_on=["league", "season", "club", "matchday"], how='left').rename(
                                                          columns={"position": "home_position"}
                                                      ).drop(columns="club")
# Add positions for each matchday for AWAY teams
regression_features_df = regression_features_df.merge(df_tables[["league", "season", "club", "matchday", "position"]],
                                                      left_on=["league", "season", "away_team", "matchday"],
                                                      right_on=["league", "season", "club", "matchday"], how='left').rename(
                                                          columns={"position": "away_position"}
                                                      ).drop(columns="club")

print(regression_features_df.columns)

# Clean Sheet potential
regression_features_df["home_clean_sheet_potential"] =  (regression_features_df["away_position"] - regression_features_df["home_position"])\
                                                         / regression_features_df['home_defense_value_ratio']
regression_features_df["away_clean_sheet_potential"] =  (regression_features_df["home_position"] - regression_features_df["away_position"])\
                                                         / regression_features_df['away_defense_value_ratio']

regression_features_df = regression_features_df.drop(columns=["home_position", "away_position", "home_defense_value", "away_defense_value",
                                                              "home_defense_value_ratio", "away_defense_value_ratio"])

# (D) ATTACK CURRENT FORM
df_matchs = df_matchs.dropna()

# Attack form variables
stat_cols = [
    'shot_attempts',
    'shots_on_goal',
    'possession',
    'score'
]

# Rolling match statistics
for stat in stat_cols:
    if stat == 'score':
        rolling_stats = compute_rolling_stat(df_matchs, stat, agg_func="sum", window=3)
    else:
        rolling_stats = compute_rolling_stat(df_matchs, stat, agg_func="mean", window=3)

    df_matchs = merge_rolling_stats(df_matchs, rolling_stats, stat_name=stat, new_col_prefix=f"{stat}_last_3")


# Merge relavant variables for current feature
regression_features_df = regression_features_df.merge(df_matchs[['league', 'season', 'matchday', 'date', 'home_team', 'home_score',
                                                                 'away_score', 'away_team', 'home_shot_attempts_last_3', 'away_shot_attempts_last_3',
                                                                 'home_shots_on_goal_last_3', 'away_shots_on_goal_last_3',
                                                                 'home_score_last_3', 'away_score_last_3',                                                             
                                                                 'home_possession_last_3', 'away_possession_last_3']],
                                                      on=['league', 'season', 'matchday', 'date', 'home_team', 'home_score',
                                                                 'away_score', 'away_team'], how='left')

# Compute features
regression_features_df["home_attack_form"] = (regression_features_df["home_shot_attempts_last_3"])*\
                                                regression_features_df["home_possession_last_3"]* regression_features_df['home_score_last_3']
regression_features_df["away_attack_form"] = (regression_features_df["away_shot_attempts_last_3"])*\
                                                regression_features_df["away_possession_last_3"]*regression_features_df['away_score_last_3']


regression_features_df = regression_features_df.drop(columns=['home_shot_attempts_last_3', 'away_shot_attempts_last_3',
                                                              'home_shots_on_goal_last_3', 'away_shots_on_goal_last_3',
                                                                'home_possession_last_3', 'away_possession_last_3',
                                                                'home_score_last_3', 'away_score_last_3'])

df_matchs = df_matchs.drop(columns=['home_score_last_3', 'away_score_last_3'])


# (E) DEFENSE CURRENT FORM

df_matchs["home_corner_against"] = df_matchs["away_corner_kicks"]
df_matchs["away_corner_against"] = df_matchs["home_corner_kicks"]
df_matchs["home_goals_conceded"] = df_matchs["away_score"]
df_matchs["away_goals_conceded"] = df_matchs["home_score"]

# Attack form variables
stat_cols = [
    'saves',
    'corner_against',
    'goals_conceded'
]

# Rolling match statistics
for stat in stat_cols:
    if stat == 'yellow_cards' or stat=='goals_conceded':
        rolling_stats = compute_rolling_stat(df_matchs, stat, agg_func="sum", window=3)
    else:
        rolling_stats = compute_rolling_stat(df_matchs, stat, agg_func="mean", window=3)

    df_matchs = merge_rolling_stats(df_matchs, rolling_stats, stat_name=stat, new_col_prefix=f"{stat}_last_3")


regression_features_df = regression_features_df.merge(df_matchs[['league', 'season', 'matchday', 'date', 'home_team', 'home_score',
                                                                 'away_score', 'away_team', 'home_goals_conceded_last_3', 'away_goals_conceded_last_3',
                                                                 'home_saves_last_3', 'away_saves_last_3',
                                                                 'home_corner_against_last_3', 'away_corner_against_last_3']],
                                                      on=['league', 'season', 'matchday', 'date', 'home_team', 'home_score',
                                                                 'away_score', 'away_team'], how='left')


regression_features_df["home_defense_form"] = -1*(regression_features_df["home_goals_conceded_last_3"]*\
                                                 regression_features_df["home_saves_last_3"]*regression_features_df["home_corner_against_last_3"])

regression_features_df["away_defense_form"] = -1*(regression_features_df["away_goals_conceded_last_3"]*\
                                                 regression_features_df["away_saves_last_3"]*regression_features_df["away_corner_against_last_3"])

# Drop columns
regression_features_df = regression_features_df.drop(columns=['home_saves_last_3', 'away_saves_last_3',
                                                              'home_corner_against_last_3', 'away_corner_against_last_3'])


# (F) GENERAL FORM FEATURE 1

# stat_cols = ['score']

# # Rolling match statistics
# for stat in stat_cols:
#     rolling_stats = compute_rolling_stat(df_matchs, stat, agg_func="sum", window=3)
#     df_matchs = merge_rolling_stats(df_matchs, rolling_stats, stat_name=stat, new_col_prefix=f"{stat}_last_3")

# # Merge form stats
# regression_features_df = regression_features_df.merge(df_matchs[['league', 'season', 'matchday', 'date', 'home_team', 'home_score',
#                                                                  'away_score', 'away_team', 'home_score_last_3', 'away_score_last_3']],
#                                                       on=['league', 'season', 'matchday', 'date', 'home_team', 'home_score',
#                                                                  'away_score', 'away_team'], how='left')

# # Create Features
# regression_features_df["home_general_form1"] = regression_features_df["home_score_last_3"] / (regression_features_df["home_goals_conceded_last_3"] + 1)
# regression_features_df["away_general_form1"] = regression_features_df["away_score_last_3"] / (regression_features_df["away_goals_conceded_last_3"] + 1)

# regression_features_df = regression_features_df.drop(columns=['home_score_last_3', 'away_score_last_3',
#                                                               'home_goals_conceded_last_3', 'away_goals_conceded_last_3'])


# (G) GENERAL FORM FEATURE 2

# Create points won feature
df_matchs["home_points"] = (df_matchs["home_score"] > df_matchs["away_score"]) * 3 + (df_matchs["home_score"] == df_matchs["away_score"]) * 1
df_matchs["away_points"] = (df_matchs["away_score"] > df_matchs["home_score"]) * 3 + (df_matchs["away_score"] == df_matchs["home_score"]) * 1

# Compute rolling window stats
rolling_stats = compute_rolling_stat(df_matchs, "points", agg_func="sum", window=5)
df_matchs = merge_rolling_stats(df_matchs, rolling_stats, stat_name="points", new_col_prefix=f"points_last_5", window=5)


# Merge form stats
regression_features_df = regression_features_df.merge(df_matchs[['league', 'season', 'matchday', 'date', 'home_team', 'home_score',
                                                                 'away_score', 'away_team', 'home_points_last_5', 'away_points_last_5']],
                                                      on=['league', 'season', 'matchday', 'date', 'home_team', 'home_score',
                                                                 'away_score', 'away_team'], how='left')

# Create Features
regression_features_df = regression_features_df.rename(columns={"home_points_last_5":"home_general_form",
                                                                "away_points_last_5":"away_general_form"})




# ====== CREATE REGRESSION DATA ======

# Columns to use for the team stats (suffix stripped)
base_cols = [
    "attack_value_ratio", "relative_value_team","score_potential", "clean_sheet_potential",
    "attack_form", "defense_form", "general_form"
]

# 1. Create home team rows
home_df = regression_features_df[[
    'league', 'season', 'matchday', 'date',
    'home_team', 'away_team', 'home_win'
] + [f'home_{col}' for col in base_cols]].copy()

home_df.rename(columns={
    'home_team': 'team',
    'away_team': 'opponent',
    'home_win': 'win',
    **{f'home_{col}': col for col in base_cols}
}, inplace=True)

home_df['match'] = 1  # Home match

# 2. Create away team rows
away_df = regression_features_df[[
    'league', 'season', 'matchday', 'date',
    'away_team', 'home_team', 'away_win'
] + [f'away_{col}' for col in base_cols]].copy()

away_df.rename(columns={
    'away_team': 'team',
    'home_team': 'opponent',
    'away_win': 'win',
    **{f'away_{col}': col for col in base_cols}
}, inplace=True)

away_df['match'] = 0  # Away match

# 3. Combine both
regression_df = pd.concat([home_df, away_df], ignore_index=True)

# 4. Create dummy variables for league
league_dummies = pd.get_dummies(regression_df['league'], prefix='league')

# 5. Drop original 'league' column and concatenate dummies
regression_df = regression_df.drop(columns='league')
regression_df = pd.concat([regression_df, league_dummies], axis=1)

# Rename columns for easier manipulation
regression_df = regression_df.rename(columns={'league_Bundesliga': 'league_ger1',
                                              'league_La Liga': 'league_sp1',
                                              'league_Ligue 1': 'league_fr1',
                                              'league_Premier League':'league_eng1',
                                              'league_Serie A':'league_it1'})
# Drop unnecessary columns
regression_df = regression_df.drop(columns=['season', 'matchday', 'date'])
regression_df = regression_df.dropna()



# ====== PCA ANALYSIS ======

# 1. Define features for PCA (exclude target and identifiers)
features = [
    'attack_value_ratio', 'relative_value_team', 'score_potential', 'clean_sheet_potential',
    'attack_form', 'defense_form', 'general_form',
    'match',
    'league_ger1', 'league_sp1', 'league_fr1', 'league_eng1'] #it1 as base

# 2. Drop NaNs and scale features
df_pca = regression_df[features + ['win']].dropna().copy()
scaler = StandardScaler()
df_scaled = scaler.fit_transform(df_pca[features])

# 3. Fit PCA
pca = PCA(n_components=2)
principal_components = pca.fit_transform(df_scaled)

# 4. Create DataFrame with results
df_pca_result = pd.DataFrame(principal_components, columns=["PC1", "PC2"])
df_pca_result["win"] = df_pca["win"].values

# 5. Plot
explained_variance = pca.explained_variance_ratio_

plt.figure(figsize=(10, 6))
sns.scatterplot(
    data=df_pca_result,
    x="PC1", y="PC2",
    hue="win",
    palette="coolwarm",
    alpha=0.7
)

plt.title("PCA of Match Features (Win vs. Loss)", fontsize=14)
plt.xlabel(f"PC1 ({explained_variance[0]:.2%} variance explained)")
plt.ylabel(f"PC2 ({explained_variance[1]:.2%} variance explained)")
plt.legend(title="Win")
plt.grid(True)
plt.tight_layout()

# 6. Save the plot
plt.savefig(os.path.join(result_folder, "PCA_features.png"), dpi=300)
plt.close()


# ====== PCA PART 2 ======
pca = PCA()
pca.fit(df_scaled)

cumulative_variance = np.cumsum(pca.explained_variance_ratio_)

plt.figure(figsize=(8, 5))
plt.plot(range(1, len(cumulative_variance)+1), cumulative_variance, marker='o')
plt.axhline(y=0.9, color='r', linestyle='--')
plt.xlabel('Number of Principal Components')
plt.ylabel('Cumulative Explained Variance')
plt.grid(True)
plt.tight_layout()
plt.savefig(os.path.join(result_folder, "PCA_dim_variance.png"), dpi=300)
plt.close()


# ====== REGRESSION FIT ======

# 1. Define features and target
features = [
    'attack_value_ratio', 'relative_value_team', 'score_potential', 'clean_sheet_potential',
    'attack_form', 'defense_form','general_form',
    'match',
    'league_ger1', 'league_sp1', 'league_fr1', 'league_eng1', 'league_it1'
]
target = 'win'

# 2. Drop missing values
df_model = regression_df[features + [target]].dropna()

# 3. Split into train/test (90% train, 10% test)
X = df_model[features]
y = df_model[target]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.10, random_state=42, stratify=y
)

# 4. Optional: scale features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_train_scaled_df = pd.DataFrame(X_train_scaled, columns=features, index=X_train.index)
X_train_scaled_df = X_train_scaled_df.drop(columns=['league_it1'])

save_correlation_heatmap(X_train_scaled_df, result_folder, "correlation_features.png")

# 5. Add intercept term for statsmodels
X_train_scaled_df = sm.add_constant(X_train_scaled_df)

# 6. Fit logistic regression with statsmodels
logit_model = sm.Logit(y_train, X_train_scaled_df)
result = logit_model.fit()

# 7. Show full regression summary
# Create a timestamp string like '2025-04-14_15-30-22'
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# Create filename with timestamp
filename = f"logit_summary_{timestamp}.txt"

# Save the summary with the timestamped filename
with open(os.path.join(result_folder, filename), "w") as f:
    f.write(result.summary().as_text())


# === PREDICTION ON TEST SET ===

# Scale
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Logistic regression: AUC/ROC for class imbalance
lr_cv = LogisticRegressionCV(
    cv=5,
    penalty='l2',
    solver='lbfgs',  # use 'liblinear' if dataset is small
    scoring='roc_auc',
    max_iter=1000,
    class_weight='balanced',  # helpful for imbalanced classes
    random_state=42
)
lr_cv.fit(X_train_scaled, y_train)

# Probability prediction test set
y_pred_prob = lr_cv.predict_proba(X_test_scaled)[:, 1]

# Best threshold based on ROC curve
fpr, tpr, thresholds = roc_curve(y_test, y_pred_prob)
optimal_idx = np.argmax(tpr - fpr)
optimal_threshold = thresholds[optimal_idx]
print(f"Optimal threshold: {optimal_threshold:.3f}")

# Final prediction
y_pred = (y_pred_prob >= optimal_threshold).astype(int)

# Plot metrics
plot_classification_metrics(y_test, y_pred, result_folder, "metrics_sklearn_auc_optimized.png")

# Compute ROC/AUC
fpr, tpr, _ = roc_curve(y_test, y_pred_prob)
roc_auc = auc(fpr, tpr)

# Plot
plt.figure(figsize=(8, 6))
plt.plot(fpr, tpr, label=f"ROC curve (AUC = {roc_auc:.2f})", linewidth=2)
plt.plot([0, 1], [0, 1], 'k--', label='Random Classifier')  # diagonal line
plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")
plt.legend(loc="lower right")
plt.grid(True)
plt.tight_layout()
plt.savefig(f"{result_folder}/roc_curve.png")  # save to your result folder
plt.show()