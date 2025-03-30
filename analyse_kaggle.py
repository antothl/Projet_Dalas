import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

final_merged_data = pd.read_csv('datasets/final_merged_data.csv')

club_games_filtered = pd.read_csv('datasets/kaggle_cleaned/club_games_filtered.csv')

club_games_merged = pd.merge(club_games_filtered, final_merged_data, left_on='club_id', right_on='id_kaggle', how='left')

plt.figure(figsize=(10, 6))
sns.boxplot(x='is_win', y='mean_value', data=club_games_merged)
plt.title('Distribution de la valeur marchande moyenne des clubs en fonction du résultat du match')
plt.xlabel('Victoire (1) / Défaite (0)')
plt.ylabel('Valeur marchande moyenne des clubs')
plt.show()

plt.figure(figsize=(10, 6))
sns.boxplot(x='is_win', y='avg_age', data=club_games_merged)
plt.title('Relation entre l\'âge moyen des joueurs et le résultat du match')
plt.xlabel('Victoire (1) / Défaite (0)')
plt.ylabel('Âge moyen des joueurs')
plt.show()

plt.figure(figsize=(10, 6))
sns.boxplot(x='is_win', y='total_defense_value', data=club_games_merged)
plt.title('Relation entre la valeur défensive et le résultat du match')
plt.xlabel('Victoire (1) / Défaite (0)')
plt.ylabel('Valeur défensive des clubs')
plt.show()

plt.figure(figsize=(10, 6))
sns.boxplot(x='is_win', y='total_attack_value', data=club_games_merged)
plt.title('Relation entre la valeur offensive et le résultat du match')
plt.xlabel('Victoire (1) / Défaite (0)')
plt.ylabel('Valeur offensive des clubs')
plt.show()

plt.figure(figsize=(10, 6))
sns.boxplot(x='is_win', y='total_midfield_value', data=club_games_merged)
plt.title('Relation entre la valeur du milieu de terrain et le résultat du match')
plt.xlabel('Victoire (1) / Défaite (0)')
plt.ylabel('Valeur du milieu de terrain des clubs')
plt.show()

plt.figure(figsize=(10, 6))
sns.boxplot(x='is_win', y='sum_value', data=club_games_merged)
plt.title('Relation entre la somme des valeurs marchandes et le résultat du match')
plt.xlabel('Victoire (1) / Défaite (0)')
plt.ylabel('Somme des valeurs marchandes des clubs')
plt.show()
