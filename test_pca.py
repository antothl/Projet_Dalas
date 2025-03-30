import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

# Charger les données
matches_df = pd.read_csv('datasets/matches_updated.csv')
stats_teams_df = pd.read_csv('datasets/stats_teams.csv')  

stats_teams_df.rename(columns={
    'mean_value': 'mean_value_team',
    'sum_value': 'sum_value_team',
    'max_value': 'max_value_team',
    'avg_age': 'avg_age_team',
    'total_attack_value': 'total_attack_value_team',
    'total_defense_value': 'total_defense_value_team',
    'total_midfield_value': 'total_midfield_value_team'
}, inplace=True)

matches_merged = pd.merge(matches_df, stats_teams_df, how='left', left_on=['Championnat', 'Saison', 'Equipe 1'], right_on=['league', 'season', 'club'], suffixes=('_t1', '_team1'))
matches_merged = pd.merge(matches_merged, stats_teams_df, how='left', left_on=['Championnat', 'Saison', 'Equipe 2'], right_on=['league', 'season', 'club'], suffixes=('_t2', '_team2'))

matches_merged['result_t1'] = matches_merged.apply(lambda row: 'win' if row['Score 1'] > row['Score 2'] 
                                                 else ('loss' if row['Score 1'] < row['Score 2'] else 'draw'), axis=1)

matches_merged['result_t2'] = matches_merged.apply(lambda row: 'win' if row['Score 2'] > row['Score 1'] 
                                                 else ('loss' if row['Score 2'] < row['Score 1'] else 'draw'), axis=1)

variables = ['Temp Max', 'Temp Min', 'Precipitations', 'mean_value_t1', 'sum_value_t1', 'max_value_t1', 'avg_age_t1',
             'mean_value_t2', 'sum_value_t2', 'max_value_t2', 'avg_age_t2']

X = matches_merged[variables]

X = X.fillna(X.mean())

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

pca = PCA(n_components=2)  
X_pca = pca.fit_transform(X_scaled)

df_pca = pd.DataFrame(X_pca, columns=['PC1', 'PC2'])

df_pca['result_t1'] = matches_merged['result_t1']

color_map = {'win': 'green', 'loss': 'red', 'draw': 'blue'}
df_pca['color'] = df_pca['result_t1'].map(color_map)

plt.figure(figsize=(8, 6))
plt.scatter(df_pca['PC1'], df_pca['PC2'], c=df_pca['color'], label=df_pca['result_t1'])
plt.xlabel('Composante Principale 1')
plt.ylabel('Composante Principale 2')
plt.title('PCA - Projection des matchs')
plt.legend(loc='best')
plt.show()

print(f"Variance expliquée par chaque composante: {pca.explained_variance_ratio_}")

print(matches_merged[['Equipe 1', 'Score 1', 'Equipe 2', 'Score 2', 'result_t1', 'result_t2']].head())
