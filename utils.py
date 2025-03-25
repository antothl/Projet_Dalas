import numpy as np
import os 
import pandas as pd 
import re
from datetime import datetime
import pickle

def create_id_tables(data_folder):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(os.path.join(data_folder,"classements_5_grands_championnats.csv"))

    # Create a new DataFrame with a unique team_id
    unique_teams = df['Equipe'].drop_duplicates().reset_index(drop=True)
    teams_df = pd.DataFrame({'team': unique_teams})
    teams_df['team_id'] = teams_df.index + 1
    teams_df.to_csv(os.path.join(data_folder,"team_ids.csv"), index=False)

    # Create a new DataFrame with a unique team_id
    unique_leagues = df['Championnat'].drop_duplicates().reset_index(drop=True)
    leages_df = pd.DataFrame({'League': unique_leagues})
    leages_df['league_id'] = leages_df.index + 1
    leages_df.to_csv(os.path.join(data_folder,"league_ids.csv"), index=False)


def create_summary_stats_teams(data_folder):

    # Read csv file
    df = pd.read_csv(os.path.join(data_folder,"joueurs_grands_championnats.csv"))

    # Dictionary for month mapping (French to English)
    mois_fr_en = { 
        "janv": "Jan", "févr": "Feb", "mars": "Mar", "avr": "Apr", "mai": "May", "juin": "Jun",
        "juil": "Jul", "août": "Aug", "sept": "Sep", "oct": "Oct", "nov": "Nov", "déc": "Dec"
    }

    # Function to extract date and age
    def extract_date_age(value):
        match = re.match(r"(\d{1,2}) (\w+)\.? (\d{4}) \((\d+)\)", value)
        if match:
            day, month_fr, year, age = match.groups()
            month_en = mois_fr_en.get(month_fr, month_fr)  # Convert French month to English
            birth_date = datetime.strptime(f"{day} {month_en} {year}", "%d %b %Y").date()  # Convert to date format
            return birth_date, int(age)
        return None, None

    # Apply transformation to the entire column
    df[["birth_date", "age"]] = df["Date de Naissance"].apply(lambda x: pd.Series(extract_date_age(x)))
    
    # Function to convert values
    def convert_value(value):
        value = value.strip()  # Remove leading/trailing spaces

        if value == "-":  # Handle unknown values
            return float(0.0)  # Convert to NaN (Not a Number)

        value = value.replace("€", "").strip()  # Remove euro sign
        value = value.replace(",", ".")  # Ensure decimal point is in correct format
        
        if "mio." in value:  # Convert million values
            return float(value.replace("mio.", "").strip()) * 1_000_000
        elif "K" in value:  # Convert thousand values
            return float(value.replace("K", "").strip()) * 1_000
        else:
            return float(value)  # Convert plain numbers

    # Apply transformation to entire column
    df["Valeur Marchande"] = df["Valeur Marchande"].apply(convert_value)

    # features for each team
    df_stats = df.groupby(["Championnat", "Saison", "Club"]).agg(
        mean_value=("Valeur Marchande", "sum"),
        sum_value=("Valeur Marchande", "mean"),
        max_value=("Valeur Marchande", "max"),
        avg_age=("age", "mean")
    ).reset_index()

    df_stats.rename(columns={"Championnat": "league",
                             "Saison": "season",
                             "Club":"club"})

    df_stats.to_csv(os.path.join(data_folder,"stats_teams.csv"), index=False)


def clean_matching_names(data_folder, create_map=False):
    
    if create_map:
        df_classement = pd.read_csv(os.path.join(data_folder,"classements_5_grands_championnats.csv"))

        # Extraire les noms uniques des équipes dans df_matchs
        equipes_matchs = set(df_classement["Equipe"])

        # Créer un dictionnaire avec les noms à corriger (partie de gauche remplie)
        correspondance = {equipe: "" for equipe in sorted(equipes_matchs)}

        # Sauvegarder en fichier CSV ou JSON pour compléter manuellement
        pd.DataFrame.from_dict(correspondance, orient="index").to_csv(os.path.join(data_folder,"orrespondance_equipes.csv"),
                                                                    header=["Nom correct"])

    # Charger les fichiers
    df_matchs = pd.read_csv(os.path.join(data_folder, "matches.csv"))
    df_classement = pd.read_csv(os.path.join(data_folder, "classements_5_grands_championnats.csv"))

    # Load
    with open(os.path.join(data_folder, "team_maps_names.pkl"), "rb") as f:
        correspondance = pickle.load(f)

    # Remplacer les noms d'équipes dans df_matchs
    df_matchs["Equipe 1"] = df_matchs["Equipe 1"].replace(correspondance)
    df_matchs["Equipe 2"] = df_matchs["Equipe 2"].replace(correspondance)

    # Sauvegarder le fichier mis à jour
    df_matchs.to_csv("datasets/matches.csv", index=False)


def process_matches_table(data_folder):
    stats_teams = pd.read_csv(os.path.join(data_folder, "stats_teams.csv"))
    games_leagues = pd.read_csv(os.path.join(data_folder, "matches.csv"))

    stats_teams = stats_teams.drop(columns=["Championnat"])

    # Fusionner les valeurs moyennes avec les matchs (Équipe 1 et Équipe 2)
    df_matchs = games_leagues.merge(stats_teams, left_on=["Saison", "Equipe 1"], right_on=["Saison", "Club"], how="left")
    df_matchs.drop(columns=["Club"], inplace=True)

    df_matchs = df_matchs.merge(stats_teams, left_on=["Saison", "Equipe 2"], right_on=["Saison", "Club"], how="left", suffixes=("_t1","_t2"))
    df_matchs.drop(columns=["Club"], inplace=True)

    # Créer une colonne "Win" : 1 si Équipe 1 gagne, 0 sinon
    df_matchs["win_t1"] = np.where(df_matchs["Score 1"] > df_matchs["Score 2"], 1, 0)

    # Sauvegarde du fichier mis à jour
    df_matchs.to_csv(os.path.join(data_folder, "matches_updated.csv"), index=False)

def clean_matches_league_names(df_matchs, data_folder):
    league_mapping = {
        "ligue-1": "Ligue 1",
        "premier-league": "Premier League",
        "la-liga": "LaLiga",
        "bundesliga-1": "Bundesliga",
        "serie-a": "Serie A"
    }
    df_matchs["Championnat"] = df_matchs["Championnat"].map(league_mapping)
    df_matchs.to_csv(os.path.join(data_folder, "matches_updated.csv"), index=False)

# Assume df is your DataFrame
def determine_result(score1, score2):
    if score1 > score2:
        return 1, 0  # Team 1 wins, Team 2 loses
    elif score1 < score2:
        return 0, 1  # Team 2 wins, Team 1 loses
    else:
        return 0.5, 0.5  # Draw
    

def merge_table_matches(df_matchs, df_classements):
    # plot_mv_age_leagues(df_teams, result_folder)
    df_matchs_cl = df_matchs.drop(columns=['Ville', 'Temp Max', 'Temp Min',
        'Precipitations', 'mean_value_t1', 'sum_value_t1', 'max_value_t1',
        'avg_age_t1', 'mean_value_t2', 'sum_value_t2', 'max_value_t2',
        'avg_age_t2', 'win_t1'])

    df_classements["Journee"] = df_classements["Journee"].astype(str)
    df_matchs_cl["Journee"] = df_matchs_cl["Journee"].astype(str)

    df_merged = pd.merge(
        df_matchs_cl,
        df_classements,
        how="left",
        left_on=["Saison", "Championnat", "Journee", "Equipe 1"],
        right_on=["Saison", "Championnat", "Journee", "Equipe"],
        suffixes=('', '_t1')
    )

    df_merged = pd.merge(
        df_merged,
        df_classements,
        how="left",
        left_on=["Saison", "Championnat", "Journee", "Equipe 2"],
        right_on=["Saison", "Championnat", "Journee", "Equipe"],
        suffixes=('_t1', '_t2')  # Final merged columns: _t1 for team 1, _t2 for team 2
    )

    df_merged = df_merged.drop(columns=["Equipe_t1", "Equipe_t2"])

    # Season 2021 not present in both datasets
    df_merged = df_merged.dropna()

    # Compute results without overwriting df_matchs
    results = df_merged.apply(lambda row: determine_result(row['Score 1'], row['Score 2']), axis=1)
    df_merged[['result_t1', 'result_t2']] = pd.DataFrame(results.tolist(), index=df_merged.index)

    return df_merged 