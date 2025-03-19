import pandas as pd

# Charger les fichiers
df_matchs = pd.read_csv("datasets/matches.csv")
df_classement = pd.read_csv("datasets/classements_5_grands_championnats.csv")

# Construire la liste des équipes correctes depuis le classement
equipes_correctes = df_classement["Equipe"].unique()

# Créer un dictionnaire de correspondance (exemple)
correspondance = {
    "1899 Hoffenheim": "TSG 1899 Hoffenheim",
    "AC Milan": "AC Milan",
    "AS Roma": "AS Roma",
    "Ajaccio": "AC Ajaccio",
    "Alaves": "Deportivo Alavés",
    "Almeria": "UD Almería",
    "Angers": "Angers SCO",
    "Arminia Bielefeld": "Arminia Bielefeld",  # Pas dans la seconde liste, à compléter
    "Arsenal": "Arsenal FC",
    "Aston Villa": "Aston Villa",
    "Atalanta": "Atalanta BC",
    "Athletic Club": "Athletic Bilbao",
    "Atletico Madrid": "Atlético de Madrid",
    "Auxerre": "AJ Auxerre",
    "Bayer Leverkusen": "Bayer 04 Leverkusen",
    "Bayern Munich": "Bayern Munich",
    "Bologna": "FC Bologna",
    "Bordeaux": "FC Girondins de Bordeaux",  # Pas dans la seconde liste, à compléter
    "Borussia Dortmund": "Borussia Dortmund",
    "Borussia Monchengladbach": "Borussia Mönchengladbach",
    "Bournemouth": "AFC Bournemouth",
    "Brentford": "FC Brentford",
    "Brighton": "Brighton & Hove Albion",
    "Burnley": "Burnley FC",
    "Cadiz": "Cádiz CF",
    "Cagliari": "Cagliari Calcio",
    "Celta Vigo": "Celta Vigo",
    "Chelsea": "Chelsea FC",
    "Clermont Foot": "Clermont Foot 63",
    "Cremonese": "US Cremonese",
    "Crystal Palace": "Crystal Palace",
    "Eintracht Frankfurt": "Eintracht Francfort",
    "Elche": "Elche CF",
    "Empoli": "FC Empoli",
    "Espanyol": "Espanyol Barcelona",
    "Estac Troyes": "ESTAC Troyes",
    "Everton": "FC Everton",
    "FC Augsburg": "FC Augsburg",
    "FC Barcelone": "FC Barcelone",
    "FC Heidenheim": "1.FC Heidenheim 1846",
    "FC Koln": "1.FC Köln",
    "FC Schalke 04": "FC Schalke 04",
    "FSV Mainz 05": "1.FSV Mainz 05",
    "Fiorentina": "ACF Fiorentina",
    "Fortuna Dusseldorf": "",  # Pas dans la seconde liste, à compléter
    "Frosinone": "Frosinone Calcio",
    "Fulham": "FC Fulham",
    "Genoa": "Genoa CFC",
    "Getafe": "FC Getafe",
    "Girona": "Girona FC",
    "Granada CF": "FC Granada",
    "Hamburger SV": "",  # Pas dans la seconde liste, à compléter
    "Hertha Berlin": "Hertha BSC",
    "Inter": "Inter Milan",
    "Juventus": "Juventus Turin",
    "LE Havre": "Le Havre AC",
    "Las Palmas": "UD Las Palmas",
    "Lazio": "Lazio Rome",
    "Lecce": "US Lecce",
    "Leeds": "Leeds United",
    "Leicester": "Leicester City",
    "Lens": "RC Lens",
    "Levante": "UD Levante",  # Pas dans la seconde liste, à compléter
    "Lille": "LOSC Lille",
    "Liverpool": "FC Liverpool",
    "Lorient": "FC Lorient",
    "Luton": "Luton Town",
    "Lyon": "Olympique Lyonnais",
    "Mallorca": "RCD Mallorca",
    "Manchester City": "Manchester City",
    "Manchester United": "Manchester United",
    "Marseille": "Olympique de Marseille",
    "Metz": "FC Metz",
    "Monaco": "AS Monaco",
    "Montpellier": "Montpellier Hérault SC",
    "Monza": "AC Monza",
    "Nantes": "FC Nantes",
    "Napoli": "SSC Napoli",
    "Newcastle": "Newcastle United",
    "Nice": "OGC Nice",
    "Norwich": "Norwich City",  # Pas dans la seconde liste, à compléter
    "Nottingham Forest": "Nottingham Forest",
    "Osasuna": "CA Osasuna",
    "Paris Saint Germain": "Paris Saint-Germain",
    "RB Leipzig": "RB Leipzig",
    "Rayo Vallecano": "Rayo Vallecano",
    "Real Betis": "Real Betis Balompié",
    "Real Madrid": "Real Madrid",
    "Real Sociedad": "Real Sociedad",
    "Rennes": "Stade Rennais FC",
    "SC Freiburg": "SC Fribourg",
    "SV Darmstadt 98": "SV Darmstadt 98",
    "Saint Etienne": "AS Saint-Étienne",
    "Salernitana": "US Salernitana 1919",
    "Sampdoria": "UC Sampdoria",
    "Sassuolo": "US Sassuolo",
    "Sevilla": "Séville FC",
    "Sheffield Utd": "Sheffield United",
    "Southampton": "FC Southampton",
    "SpVgg Greuther Furth": "SpVgg Greuther Fürth",  # Pas dans la seconde liste, à compléter
    "Spezia": "Spezia Calcio",
    "Stade Brestois 29": "Stade Brestois 29",
    "Stade de Reims": "Stade de Reims",
    "Strasbourg": "RC Strasbourg Alsace",
    "Torino": "Torino FC",
    "Tottenham": "Tottenham Hotspur",
    "Toulouse": "Toulouse FC",
    "Udinese": "Udinese Calcio",
    "Union Berlin": "1.FC Union Berlin",
    "Valencia": "FC Valencia",
    "Valladolid": "Real Valladolid",
    "Venezia": "Venezia FC",
    "Verona": "Hellas Verona",
    "VfB Stuttgart": "VfB Stuttgart",
    "VfL BOCHUM": "VfL Bochum",
    "VfL Wolfsburg": "VfL Wolfsburg",
    "Villarreal": "Villarreal CF",
    "Watford": "FC Watford",  # Pas dans la seconde liste, à compléter
    "Werder Bremen": "SV Werder Bremen",
    "West Ham United": "West Ham United",
    "Wolves": "Wolverhampton Wanderers"
}


# Remplacer les noms d'équipes dans df_matchs
df_matchs["Equipe 1"] = df_matchs["Equipe 1"].replace(correspondance)
df_matchs["Equipe 2"] = df_matchs["Equipe 2"].replace(correspondance)

# Sauvegarder le fichier mis à jour
df_matchs.to_csv("datasets/matches.csv", index=False)

print("✅ Correction appliquée et fichier mis à jour !")
