import requests
import re
import csv
from bs4 import BeautifulSoup

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
    "Osasuna": "Pamplune",
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
    "Ligue 1": ("france", "ligue-1"),
    "La Liga": ("espagne", "la-liga"),
    "Bundesliga": ("allemagne", "bundesliga-1"),
    "Premier League": ("l-angleterre", "premier-league"),
    "Serie A": ("italie", "serie-a"),
}

# Liste des saisons à scraper
SEASONS = [2023, 2022, 2021]  # Modifier si besoin

# Nom du fichier CSV où les données seront enregistrées
FILENAME = "datasets/matches.csv"

def scrape_matches(pays, championnat, saison):
    """Scrape les matchs pour un championnat et une saison donnée"""
    
    url = f"https://foot.be/ligues/{pays}/{championnat}/{saison}/matchs/"
    print(f"🔍 Scraping : {url}")

    # Récupérer la page
    response = requests.get(url, headers=HEADERS)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")

        # Trouver tous les blocs contenant les matchs
        matches = soup.find_all("div", class_="filterable-fixture")

        # Ouvrir le fichier CSV en mode ajout (append)
        with open(FILENAME, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            
            # Si le fichier est vide, ajouter l'en-tête
            if file.tell() == 0:
                writer.writerow(["Date", "Heure", "Équipe 1", "Score 1", "Score 2", "Équipe 2", "Championnat", "Saison", "Ville"])
            
            for match in matches:
                try:
                    # Extraction de la date et de l'heure
                    date_time = match.find("strong").text.strip()

                    # Extraction des équipes et des scores
                    team_and_score = match.find_all("span", class_=re.compile(r"text-green-700 font-bold inline-block pt-1|inline-block pt-1"))

                    team1 = team_and_score[0].text.strip()
                    score1 = team_and_score[1].text.strip()
                    team2 = team_and_score[2].text.strip()
                    score2 = team_and_score[3].text.strip()

                    # Écrire les données dans le fichier CSV
                    writer.writerow([date_time, team1, score1, score2, team2, championnat, saison, clubs_to_city[team1]])

                    # Afficher pour vérifier
                    print(f"{date_time}: {team1} {score1} - {score2} {team2}")
                except Exception as e:
                    print("❌ Erreur lors du parsing d'un match :", e)
                    exit(1)
    else:
        print("⚠️ Échec de la récupération des données, statut :", response.status_code)

# Lancer le scraping pour tous les championnats et saisons
for league, (pays, championnat) in LEAGUES.items():
    print(f"\n🏆 {league} 🏆")
    
    for season in SEASONS:
        scrape_matches(pays, championnat, season)
