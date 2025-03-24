import numpy as np
import os 
import pandas as pd 
import re
from datetime import datetime


def create_id_tables(data_folder):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(os.path.join(data_folder,"classements_5_grands_championnats.csv"))

    # Create a new DataFrame with a unique team_id
    unique_teams = df['Équipe'].drop_duplicates().reset_index(drop=True)
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
        sum_value=("Valeur Marchande", "sum"),
        max_value=("Valeur Marchande", "max"),
        avg_age=("age", "mean")
    ).reset_index()

    df_stats.rename(columns={"Championnat": "league",
                             "Saison": "season",
                             "Club":"club"})

    df_stats.to_csv(os.path.join(data_folder,"stats_teams.csv"), index=False)


data_folder = r"datasets"

create_summary_stats_teams(data_folder)

