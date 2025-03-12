import requests
import re
import csv
import time
from bs4 import BeautifulSoup
from datetime import datetime


# Dictionnaire des clubs et de leurs villes
clubs_to_city = {
    "Manchester United": "Manchester",
    "Manchester City": "Manchester",
    "Liverpool": "Liverpool",
    "Chelsea": "Londres",
    "Arsenal": "Londres",
    "Tottenham": "Londres",
    "Leeds": "Leeds",
    "West Ham United": "Londres",
    "Aston Villa": "Birmingham",
    "Everton": "Liverpool",
    "Wolves": "Wolverhampton",
    "Newcastle": "Newcastle upon Tyne",
    "Southampton": "Southampton",
    "Crystal Palace": "Londres",
    "Brighton": "Brighton",
    "Burnley": "Burnley",
    "Watford": "Watford",
    "Norwich": "Norwich",
    "Fulham": "Londres",
    "Bournemouth": "Bournemouth",
    "Sheffield Utd": "Sheffield",
    "Brentford": "Londres",
    "Leicester": "Leicester",
    "Ipswich": "Ipswich",
    "Nottingham Forest": "Nottingham",
    "Luton": "Luton",
    
    "Real Madrid": "Madrid",
    "FC Barcelone": "Barcelone",
    "Atletico Madrid": "Madrid",
    "Sevilla": "Séville",
    "Real Sociedad": "Saint-Sébastien",
    "Villarreal": "Villarreal",
    "Real Betis": "Séville",
    "Valencia": "Valence",
    "Athletic Club": "Bilbao",
    "Espanyol": "Barcelone",
    "Granada CF": "Grenade",
    "Getafe": "Getafe",
    "Levante": "Valence",
    "Celta Vigo": "Vigo",
    "Eibar": "Eibar",
    "Osasuna": "Pampelune",
    "Alaves": "Vitoria-Gasteiz",
    "Elche": "Elche",
    "Mallorca": "Palma",
    "Cadiz": "Cadix",
    "Girona": "Gérone",
    "Las Palmas": "Las Palmas",
    "Almeria": "Almería",
    "Rayo Vallecano": "Madrid",
    "Valladolid": "Valladolid",
    
    "Juventus": "Turin",
    "Inter": "Milan",
    "AC Milan": "Milan",
    "AS Roma": "Rome",
    "Napoli": "Naples",
    "Lazio": "Rome",
    "Atalanta": "Bergame",
    "Fiorentina": "Florence",
    "Sampdoria": "Gênes",
    "Bologna": "Bologne",
    "Torino": "Turin",
    "Verona": "Vérone",
    "Udinese": "Udine",
    "Spezia": "La Spezia",
    "Empoli": "Empoli",
    "Genoa": "Gênes",
    "Salernitana": "Salerne",
    "Venezia": "Venise",
    "Cagliari": "Cagliari",
    "Sassuolo": "Sassuolo",
    "Cremonese": "Crémone",
    "Vicenza": "Vicence",
    "Pisa": "Pise",
    "Brescia": "Brescia",
    "Como": "Côme",
    "Frosinone": "Frosinone",
    "Lecce": "Lecce",
    "Monza": "Monza",
    
    "Bayern Munich": "Munich",
    "Borussia Dortmund": "Dortmund",
    "RB Leipzig": "Leipzig",
    "Bayer Leverkusen": "Leverkusen",
    "VfL Wolfsburg": "Wolfsbourg",
    "Union Berlin": "Berlin",
    "Eintracht Frankfurt": "Francfort",
    "Borussia Monchengladbach": "Mönchengladbach",
    "SC Freiburg": "Fribourg",
    "VfB Stuttgart": "Stuttgart",
    "FSV Mainz 05": "Mayence",
    "Hoffenheim": "Sinsheim",
    "Augsburg": "Augsbourg",
    "Arminia Bielefeld": "Bielefeld",
    "Köln": "Cologne",
    "Werder Bremen": "Brême",
    "Greuther Fürth": "Fürth",
    "VfL BOCHUM": "Bochum",
    "Hertha Berlin": "Berlin",
    "1899 Hoffenheim": "Sinsheim",
    "FC Augsburg": "Augsbourg",
    "FC Koln": "Cologne",
    "FC Heidenheim": "Heidenheim",
    "SV Darmstadt 98": "Darmstadt",
    "Fortuna Dusseldorf": "Düsseldorf",
    "FC Schalke 04": "Gelsenkirchen",
    "Hamburger SV": "Hambourg",
    "SpVgg Greuther Furth": "Fürth",
    
    "Paris Saint Germain": "Paris",
    "Marseille": "Marseille",
    "Lyon": "Lyon",
    "Monaco": "Monaco",
    "Lille": "Lille",
    "Nice": "Nice",
    "Saint Etienne": "Saint Etienne",
    "Bordeaux": "Bordeaux",
    "Nantes": "Nantes",
    "Rennes": "Rennes",
    "Montpellier": "Montpellier",
    "Angers": "Angers",
    "Lorient": "Lorient",
    "Strasbourg": "Strasbourg",
    "Troyes": "Troyes",
    "Clermont Foot": "Clermont-Ferrand",
    "Lens": "Lens",
    "Stade de Reims": "Reims",
    "Metz": "Metz",
    "Stade Brestois 29": "Brest",
    "LE Havre": "Le Havre",
    "Toulouse": "Toulouse",
    "Ajaccio": "Ajaccio",
    "Auxerre": "Auxerre",
    "Estac Troyes": "Troyes",
}



# En-têtes pour éviter d'être bloqué
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# Dictionnaire des championnats avec leur chemin dans l'URL
LEAGUES = {
    "La Liga": ("espagne", "la-liga"),
    "Ligue 1": ("france", "ligue-1"),
    "Bundesliga": ("allemagne", "bundesliga-1"),
    "Premier League": ("l-angleterre", "premier-league"),
    "Serie A": ("italie", "serie-a"),
}

# Liste des saisons à scraper
SEASONS = [2023, 2022, 2021]

# Nom du fichier CSV où les données seront enregistrées
FILENAME = "datasets/matches.csv"

# Fonction pour récupérer les coordonnées d'une ville avec l'API Nominatim
def get_lat_lon(city):
    """Récupère la latitude et la longitude d'une ville en utilisant l'API Nominatim."""
    url = f"https://nominatim.openstreetmap.org/search?q={city}&format=json"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if data:
            return float(data[0]["lat"]), float(data[0]["lon"])
    
    return None, None

# Fonction pour récupérer la météo le jour du match
def get_weather(lat, lon, date):
    """Récupère la météo historique d'un lieu et d'une date donnés."""
    url = f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date={date}&end_date={date}&daily=temperature_2m_max,temperature_2m_min,precipitation_sum&timezone=Europe/Paris"
    
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        if "daily" in data:
            temp_max = data["daily"]["temperature_2m_max"][0]
            temp_min = data["daily"]["temperature_2m_min"][0]
            precipitation = data["daily"]["precipitation_sum"][0]
            return temp_max, temp_min, precipitation
    print("❌ Erreur lors de la récupération des données météo.")
    return None, None, None

def scrape_matches(pays, championnat, saison):
    """Scrape les matchs pour un championnat et une saison donnée"""
    
    url = f"https://foot.be/ligues/{pays}/{championnat}/{saison}/matchs/"
    print(f"🔍 Scraping : {url}")

    response = requests.get(url, headers=HEADERS)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        matches = soup.find_all("div", class_="filterable-fixture")

        with open(FILENAME, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            
            if file.tell() == 0:
                writer.writerow(["Date", "Heure", "Équipe 1", "Score 1", "Score 2", "Équipe 2", "Championnat", "Saison", "Ville", "Temp Max", "Temp Min", "Précipitations"])
            
            for match in matches:
                try:
                    date_time = match.find("strong").text.strip()
                    date_time = date_time.split()[0]  # Extraction de la date uniquement
                    date_time = datetime.strptime(date_time, "%Y-%m-%d").strftime("%Y-%m-%d")
                    team_and_score = match.find_all("span", class_=re.compile(r"text-green-700 font-bold inline-block pt-1|inline-block pt-1"))
                    team1 = team_and_score[0].text.strip()
                    score1 = team_and_score[1].text.strip()
                    team2 = team_and_score[2].text.strip()
                    score2 = team_and_score[3].text.strip()
                    
                    city = clubs_to_city[team1]
                    lat, lon = get_lat_lon(city)
                    print(lat, lon)
                    temp_max, temp_min, precipitation = (None, None, None)
                    if lat and lon:
                        temp_max, temp_min, precipitation = get_weather(lat, lon, date_time)
                    
                    writer.writerow([date_time, team1, score1, score2, team2, championnat, saison, city, temp_max, temp_min, precipitation])
                    
                    print(f"{date_time}: {team1} {score1} - {score2} {team2} | Temp Max: {temp_max}°C, Temp Min: {temp_min}°C, Précipitations: {precipitation} mm")
                except Exception as e:
                    print("❌ Erreur lors du parsing d'un match :", e)
                    exit(1)
    else:
        print("⚠️ Échec de la récupération des données, statut :", response.status_code)

for league, (pays, championnat) in LEAGUES.items():
    print(f"\n🏆 {league} 🏆")
    for season in SEASONS:
        scrape_matches(pays, championnat, season)
# for clubs, city in clubs_to_city.items():
#     print(f"\n🏆 {get_lat_lon(city)} 🏆")
#     lat, lon=get_lat_lon(city)
#     print(f"\n🏆 {get_weather(lat,lon, '2023-08-01')} 🏆")