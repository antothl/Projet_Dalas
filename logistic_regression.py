from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report


import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

file_path_matches = "datasets/matches_updated.csv"
file_path_stats = "datasets/stats_teams.csv"

df_matches = pd.read_csv(file_path_matches)
df_stats = pd.read_csv(file_path_stats)

def determine_season(date):
    year = int(date[:4])
    month = int(date[5:7])
    return year if month >= 7 else year - 1

df_matches["season"] = df_matches["Date"].astype(str).apply(determine_season)

def calculer_points(score1, score2):
    return 3 if score1 > score2 else 1 if score1 == score2 else 0

df_matches["points_t1"] = df_matches.apply(lambda row: calculer_points(row["Score 1"], row["Score 2"]), axis=1)
df_matches["points_t2"] = df_matches.apply(lambda row: calculer_points(row["Score 2"], row["Score 1"]), axis=1)

df_long = pd.concat([
    df_matches[["Journee", "Equipe 1", "points_t1", "Score 1", "Score 2"]].rename(columns={"Equipe 1": "Equipe", "points_t1": "Points", "Score 1": "Buts_marques", "Score 2": "Buts_encaisses"}),
    df_matches[["Journee", "Equipe 2", "points_t2", "Score 2", "Score 1"]].rename(columns={"Equipe 2": "Equipe", "points_t2": "Points", "Score 2": "Buts_marques", "Score 1": "Buts_encaisses"})
])

df_long = df_long.sort_values(by=["Equipe", "Journee"]).reset_index(drop=True)

df_long["Forme_3matchs"] = df_long.groupby("Equipe")["Points"].rolling(window=3, min_periods=1).sum().reset_index(level=0, drop=True)
df_long["Buts_marques_3matchs"] = df_long.groupby("Equipe")["Buts_marques"].rolling(window=3, min_periods=1).sum().reset_index(level=0, drop=True)
df_long["Buts_encaisses_3matchs"] = df_long.groupby("Equipe")["Buts_encaisses"].rolling(window=3, min_periods=1).sum().reset_index(level=0, drop=True)

df_matches = df_matches.merge(df_long, left_on=["Journee", "Equipe 1"], right_on=["Journee", "Equipe"], how="left").rename(columns={"Forme_3matchs": "Forme_t1", "Buts_marques_3matchs": "Buts_marques_t1", "Buts_encaisses_3matchs": "Buts_encaisses_t1"})
df_matches = df_matches.drop(columns=["Equipe"])

df_stats = df_stats.rename(columns={"club": "Equipe", "season": "season_stats"})
df = df_matches.merge(df_stats, left_on=["Equipe 1", "season"], right_on=["Equipe", "season_stats"], how="left")
df = df.drop(columns=["Equipe", "season_stats"])

features = ["Buts_marques_t1", "Forme_t1", "Buts_encaisses_t1"]


df_cleaned = df.dropna(subset=features + ["win_t1"])

X_cleaned = df_cleaned[features]
y_cleaned = df_cleaned["win_t1"]


X_train, X_test, y_train, y_test = train_test_split(X_cleaned, y_cleaned, test_size=0.3, random_state=42)

model = LogisticRegression()

model.fit(X_train, y_train)

y_pred = model.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy: {accuracy:.2f}")

print("Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))
print("\nClassification Report:")
print(classification_report(y_test, y_pred))


from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report

model_rf = RandomForestClassifier(random_state=42)

model_rf.fit(X_train, y_train)

y_pred_rf = model_rf.predict(X_test)

print("Accuracy:", accuracy_score(y_test, y_pred_rf))
print(classification_report(y_test, y_pred_rf))
