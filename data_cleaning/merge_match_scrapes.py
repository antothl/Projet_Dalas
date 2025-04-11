import os
import pandas as pd

# Directories
project_dir = os.getcwd()
data_folder = os.path.join(project_dir, "datasets")
data_scraped = os.path.join(project_dir, "data")

# Import data
scraped_data1 = pd.read_csv( os.path.join(data_scraped, "top5leagues_all_stats_20250411_123845.csv"))
scraped_data2 = pd.read_csv( os.path.join(data_scraped, "top5leagues_all_stats_20250411_140548.csv"))
scraped_data = pd.concat([scraped_data2, scraped_data1], axis=0)
df_matches = pd.read_csv(os.path.join(data_folder, "matches.csv"))

# We'll keep only the first three components: weekday, short month, day, and year
def clean_date_string(s):
    parts = s.split(', ')
    if len(parts) >= 3:
        # Expected structure: ['Sun', 'May 22', 'May', '2022']
        # So take the 2nd and last part: 'May 22' and '2022'
        date_part = parts[1]  # e.g., 'May 22'
        year_part = parts[-1]  # e.g., '2022'
        return f"{date_part}, {year_part}"
    return s  # fallback

# Apply to column
scraped_data['date'] = scraped_data['date'].apply(clean_date_string)

# Step 2: Convert to datetime
scraped_data['date'] = pd.to_datetime(scraped_data['date'], format='%b %d, %Y', errors='coerce')

league_mapping = {
    'ENG.1': 'Premier League',
    'ESP.1': 'La Liga',
    'GER.1': 'Bundesliga',
    'ITA.1': 'Serie A',
    'FRA.1': 'Ligue 1'
}

# Step 2: Apply the mapping
scraped_data['league'] = scraped_data['league'].map(league_mapping)


# # Group by league and get unique home teams
# league_teams_dict = (
#     scraped_data
#     .groupby('league')['home_team']
#     .unique()
#     .apply(list)  # ensure it's a list, not a NumPy array
#     .to_dict()
# )

# # Step 1: Sort team lists alphabetically
# sorted_league_teams_dict = {
#     league: sorted(teams)
#     for league, teams in league_teams_dict.items()
# }

# # Step 2: Custom JSON serialization with line breaks between teams
# def custom_json_format(data):
#     formatted = "{\n"
#     for league, teams in data.items():
#         formatted += f'  "{league}": [\n'
#         for team in teams:
#             formatted += f'    "{team}",\n'
#         if teams:
#             formatted = formatted.rstrip(",\n") + "\n"  # remove last comma
#         formatted += "  ],\n"
#     formatted = formatted.rstrip(",\n") + "\n}"  # remove last comma
#     return formatted

# # Step 3: Write to file
# with open("league_teams_formatted.json", "w", encoding="utf-8") as f:
#     f.write(custom_json_format(sorted_league_teams_dict))

# print(df_matches.head())

# # Group by league and get unique home teams
# league_teams_dict = (
#     df_matches
#     .groupby('league')['home_team']
#     .unique()
#     .apply(list)  # ensure it's a list, not a NumPy array
#     .to_dict()
# )

# # Step 1: Sort team lists alphabetically
# sorted_league_teams_dict = {
#     league: sorted([team for team in teams if isinstance(team, str)])
#     for league, teams in league_teams_dict.items()
# }

# # Step 2: Custom JSON serialization with line breaks between teams
# def custom_json_format(data):
#     formatted = "{\n"
#     for league, teams in data.items():
#         formatted += f'  "{league}": [\n'
#         for team in teams:
#             formatted += f'    "{team}",\n'
#         if teams:
#             formatted = formatted.rstrip(",\n") + "\n"  # remove last comma
#         formatted += "  ],\n"
#     formatted = formatted.rstrip(",\n") + "\n}"  # remove last comma
#     return formatted

# # Step 3: Write to file
# with open("league_teams_formatted_true.json", "w", encoding="utf-8") as f:
#     f.write(custom_json_format(sorted_league_teams_dict))


team_name_mapping = {
    "1. FC Heidenheim 1846": "1.FC Heidenheim 1846",
    "1. FC Union Berlin": "1.FC Union Berlin",
    "Bayer Leverkusen": "Bayer 04 Leverkusen",
    "Borussia Monchengladbach": "Borussia Mönchengladbach",
    "Eintracht Frankfurt": "Eintracht Francfort",
    "FC Cologne": "1.FC Köln",
    "Hertha Berlin": "Hertha BSC",
    "Mainz": "1.FSV Mainz 05",
    "SC Freiburg": "SC Fribourg",
    "Schalke 04": "FC Schalke 04",
    "SpVgg Greuther Furth": "SpVgg Greuther Fürth",
    "TSG Hoffenheim": "TSG 1899 Hoffenheim",
    "Werder Bremen": "SV Werder Bremen",
    "Alavés": "Deportivo Alavés",
    "Almería": "UD Almería",
    "Athletic Club": "Athletic Bilbao",
    "Atlético Madrid": "Atlético de Madrid",
    "Barcelona": "FC Barcelone",
    "Cádiz": "Cádiz CF",
    "Elche": "Elche CF",
    "Espanyol": "Espanyol Barcelona",
    "Getafe": "FC Getafe",
    "Granada": "FC Granada",
    "Las Palmas": "UD Las Palmas",
    "Levante": "UD Levante",
    "Mallorca": "RCD Mallorca",
    "Osasuna": "CA Osasuna",
    "Sevilla": "Séville FC",
    "Valencia": "FC Valencia",
    "Villarreal": "Villarreal CF",
    "Bordeaux": "FC Girondins de Bordeaux",
    "Brest": "Stade Brestois 29",
    "Clermont Foot": "Clermont Foot 63",
    "Lens": "RC Lens",
    "Lille": "LOSC Lille",
    "Lorient": "FC Lorient",
    "Lyon": "Olympique Lyonnais",
    "Marseille": "Olympique de Marseille",
    "Metz": "FC Metz",
    "Montpellier": "Montpellier Hérault SC",
    "Nantes": "FC Nantes",
    "Nice": "OGC Nice",
    "Saint-Etienne": "AS Saint-Étienne",
    "Stade Rennais": "Stade Rennais FC",
    "Strasbourg": "RC Strasbourg Alsace",
    "Troyes": "ESTAC Troyes",
    "Arsenal": "Arsenal FC",
    "Brentford": "FC Brentford",
    "Everton": "FC Everton",
    "Fulham": "FC Fulham",
    "Liverpool": "FC Liverpool",
    "Southampton": "FC Southampton",
    "Watford": "FC Watford",
    "AC Milan": "AC Milan",
    "AS Roma": "AS Roma",
    "Atalanta": "Atalanta BC",
    "Bologna": "FC Bologna",
    "Cagliari": "Cagliari Calcio",
    "Cremonese": "US Cremonese",
    "Empoli": "FC Empoli",
    "Fiorentina": "ACF Fiorentina",
    "Frosinone": "Frosinone Calcio",
    "Genoa": "Genoa CFC",
    "Inter Milan": "Inter Milan",
    "Juventus": "Juventus Turin",
    "Lazio": "Lazio Rome",
    "Lecce": "US Lecce",
    "Monza": "AC Monza",
    "Napoli": "SSC Napoli",
    "Salernitana": "US Salernitana 1919",
    "Sampdoria": "UC Sampdoria",
    "Sassuolo": "US Sassuolo",
    "Spezia": "Spezia Calcio",
    "Torino": "Torino FC",
    "Udinese": "Udinese Calcio",
    "Venezia": "Venezia FC"
}


scraped_data['home_team'] = scraped_data['home_team'].replace(team_name_mapping)
scraped_data['away_team'] = scraped_data['away_team'].replace(team_name_mapping)


# Ensure both date columns are datetime
df_matches['date'] = pd.to_datetime(df_matches['date'])
scraped_data['date'] = pd.to_datetime(scraped_data['date'])


print(scraped_data.columns)

# Columns to join on
join_keys = ['league', 'season', 'date', 'home_team', 'away_team']

# Columns to merge (just the stats from scraped_data)
stats_columns = [
    'home_shots_on_goal', 'away_shots_on_goal',
    'home_shot_attempts', 'away_shot_attempts',
    'home_yellow_cards', 'away_yellow_cards',
    'home_corner_kicks', 'away_corner_kicks',
    'home_saves', 'away_saves',
    'home_possession', 'away_possession'
]

# Before merge: print row counts
print("🔎 BEFORE MERGE")
print(f"df_matches shape: {df_matches.shape}")
print(f"scraped_data shape: {scraped_data.shape}")
print(f"Stats rows to join: {scraped_data[stats_columns].notna().any(axis=1).sum()} rows with stats")

# Perform the left join
df_merged = df_matches.merge(
    scraped_data[join_keys + stats_columns],
    on=join_keys,
    how='left'
)

# After merge: print new shape and count how many rows got stats
print("\n✅ AFTER MERGE")
print(f"df_merged shape: {df_merged.shape}")

# Check how many rows have stats now
num_with_stats = df_merged[stats_columns].notna().any(axis=1).sum()
print(f"Rows with at least one stat merged in: {num_with_stats} / {df_merged.shape[0]}")


# Convert possession columns from '60.2%' to float: 60.2
for col in ['home_possession', 'away_possession']:
    df_merged[col] = (
        df_merged[col]
        .str.rstrip('%')      # remove the '%' sign
        .astype(float)        # convert to float
    )


df_merged.to_csv(os.path.join(data_folder, "matches.csv"))

print(df_merged.head())