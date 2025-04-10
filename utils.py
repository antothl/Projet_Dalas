import numpy as np
import os 
import pandas as pd 
import re
from datetime import datetime
import pickle

def create_id_tables(data_folder):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(os.path.join(data_folder,"table_leagues.csv"))

    # Create a new DataFrame with a unique team_id
    unique_teams = df['club'].drop_duplicates().reset_index(drop=True)
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
    df = pd.read_csv(os.path.join(data_folder,"player_values.csv"))

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
        mean_value=("Valeur Marchande", "mean"),
        sum_value=("Valeur Marchande", "sum"),
        max_value=("Valeur Marchande", "max"),
        avg_age=("age", "mean")
    ).reset_index()

    # Also include value per position area
    players_df = pd.read_csv(os.path.join(data_folder, "kaggle_data", "players.csv"))
    # Merge dataframes
    players_extended = df.merge(players_df[['name', 'sub_position', 'position']],
                                left_on="Joueur", right_on="name", how="left")
    players_extended["position"] = players_extended["position"].fillna('Missing')
    players_extended["sub_position"] = players_extended["sub_position"].fillna('Missing')
    

    # Step 1: Normalize position groups
    players_extended["position_group"] = players_extended["position"].replace({
        "Goalkeeper": "Defense",
        "Defender": "Defense",
        "Midfield": "Midfield",
        "Attack": "Attack"
    })

    # Step 2: Group by league/season/club/position_group and sum market value
    position_value = players_extended.groupby(["Championnat", "Saison", "Club", "position_group"])["Valeur Marchande"].sum().unstack(fill_value=0).reset_index()

    # Step 3: Rename columns
    position_value = position_value.rename(columns={
        "Defense": "total_defense_value",
        "Midfield": "total_midfield_value",
        "Attack": "total_attack_value"
    })

    # Step 4: Merge with df_stats
    df_stats = df_stats.merge(position_value, on=["Championnat", "Saison", "Club"], how="left")

    # Rename columns to english
    df_stats = df_stats.rename(columns={"Championnat": "league",
                             "Saison": "season",
                             "Club":"club"})
    
    # Save dataframe
    df_stats.to_csv(os.path.join(data_folder,"stats_teams.csv"), index=False)

    return df_stats


def clean_matching_names(df_classements, df_matchs, data_folder, create_map=False):
    
    if create_map:

        # Extraire les noms uniques des équipes dans df_matchs
        equipes_matchs = set(df_classements["Equipe"])

        # Créer un dictionnaire avec les noms à corriger (partie de gauche remplie)
        correspondance = {equipe: "" for equipe in sorted(equipes_matchs)}

        # Sauvegarder en fichier CSV ou JSON pour compléter manuellement
        pd.DataFrame.from_dict(correspondance, orient="index").to_csv(os.path.join(data_folder,"correspondance_equipes.csv"),
                                                                    header=["Nom correct"])

    # Load
    with open(os.path.join(data_folder, "team_maps_names.pkl"), "rb") as f:
        correspondance = pickle.load(f)

    # Remplacer les noms d'équipes dans df_matchs
    df_matchs["Equipe 1"] = df_matchs["Equipe 1"].replace(correspondance)
    df_matchs["Equipe 2"] = df_matchs["Equipe 2"].replace(correspondance)

    # Compute results without overwriting df_matchs
    results = df_matchs.apply(lambda row: determine_result(row['Score 1'], row['Score 2']), axis=1)
    df_matchs[['result_t1', 'result_t2']] = pd.DataFrame(results.tolist(), index=df_matchs.index)

    return df_matchs


def process_matches_table(stats_teams, df_matches, data_folder):

    stats_teams = stats_teams.drop(columns=["league"])

    # Fusionner les valeurs moyennes avec les matchs (Équipe 1 et Équipe 2)
    df_matchs = df_matches.merge(stats_teams, left_on=["season", "home_team"], right_on=["season", "club"], how="left")
    df_matchs.drop(columns=["club"], inplace=True)

    df_matchs = df_matchs.merge(stats_teams, left_on=["season", "away_team"], right_on=["season", "club"], how="left", suffixes=("_t1","_t2"))
    df_matchs.drop(columns=["club"], inplace=True)

    return df_matchs

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