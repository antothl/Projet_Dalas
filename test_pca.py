import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

# Charger les données (remplace les chemins des fichiers par les tiens)
df_matches = pd.read_csv("datasets/matches_updated.csv")  # Fichier des matchs
df_teams = pd.read_csv("datasets/stats_teams2.csv")  # Fichier des stats des équipes

# Ajouter une colonne qui indique si l'équipe 1 est à domicile (1) ou à l'extérieur (0)
df_matches['domicile_t1'] = 1  # Par défaut, on considère que l'équipe 1 est à domicile
df_matches['domicile_t2'] = 0  # Par défaut, l'équipe 2 est à l'extérieur
# Ajuster en fonction des scores : si l'équipe 1 perd, elle est à l'extérieur
df_matches.loc[df_matches['Score 1'] < df_matches['Score 2'], 'domicile_t1'] = 0
df_matches.loc[df_matches['Score 1'] < df_matches['Score 2'], 'domicile_t2'] = 1

# Sélectionner les variables pertinentes pour la PCA (par exemple, température, précipitations, valeur des équipes)
X = df_matches[['Temp Max', 'Temp Min', 'Precipitations', 'mean_value_t1', 'sum_value_t1', 'max_value_t1', 'avg_age_t1',
                'mean_value_t2', 'sum_value_t2', 'max_value_t2', 'avg_age_t2', 'domicile_t1', 'domicile_t2']].values

# Normaliser les données (très important avant d'appliquer la PCA)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Appliquer la PCA pour réduire à 2 dimensions
pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_scaled)

# Ajouter les résultats PCA au dataframe
df_matches['PCA1'] = X_pca[:, 0]
df_matches['PCA2'] = X_pca[:, 1]

# Visualiser les résultats avec des couleurs pour les victoires et les défaites
plt.figure(figsize=(8, 6))

# Colorier les points en fonction des résultats (victoire = 1, défaite = 0)
scatter = plt.scatter(df_matches['PCA1'], df_matches['PCA2'], c=df_matches['win_t1'], cmap='coolwarm', edgecolor='k', alpha=0.7)

# Ajouter une barre de couleurs pour indiquer les victoires (rouge) et les défaites (bleu)
plt.colorbar(scatter)

# Titres et labels
plt.title("PCA - Facteurs Influents sur la Victoire des Équipes")
plt.xlabel("Composante Principale 1")
plt.ylabel("Composante Principale 2")
plt.show()

# Affichage de la variance expliquée par chaque composante
print(f"Variance expliquée par chaque composante : {pca.explained_variance_ratio_}")
print(f"Variance cumulée : {np.cumsum(pca.explained_variance_ratio_)}")
