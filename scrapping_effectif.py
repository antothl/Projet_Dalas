import requests
from bs4 import BeautifulSoup
import time
import pandas as pd

# En-tête User-Agent pour éviter le blocage
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# Base URL de Transfermarkt
BASE_URL = "https://www.transfermarkt.fr"

# Dictionnaire des grands championnats avec leur code Transfermarkt
LEAGUES = {
    "Ligue 1": "FR1",
    "Premier League": "GB1",
    "La Liga": "ES1",
    "Bundesliga": "L1",
    "Serie A": "IT1"
}

# Plage des saisons à scraper
SEASONS = [2021, 2022, 2023]

def get_club_links(league_code, season):
    """Récupère les liens des clubs pour une ligue et une saison donnée."""
    url = f"{BASE_URL}/{league_code}/startseite/wettbewerb/{league_code}/plus/?saison_id={season}"
    response = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")

    club_links = {}

    # Sélection du tableau des équipes
    table = soup.find("table", class_="items")
    if table:
        rows = table.find_all("tr", class_=["odd", "even"])
        
        for row in rows:
            club_cell = row.find("td", class_="hauptlink")
            if club_cell:
                club_name = club_cell.text.strip()
                club_url = BASE_URL + club_cell.find("a")["href"]
                club_links[club_name] = club_url
    
    return club_links

def get_players_from_club(club_name, club_url, league_name, season):
    """Récupère les joueurs d'un club avec leur date de naissance et valeur marchande."""
    response = requests.get(club_url, headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")

    players = []
    
    # Sélection du tableau des joueurs
    table = soup.find("table", class_="items")
    if table:
        rows = table.find_all("tr", class_=["odd", "even"])
        
        for row in rows:
            player_cell = row.find("td", class_="hauptlink")
            if player_cell:
                player_name = player_cell.text.strip()

                # Date de naissance (colonne spécifique)
                dob_cells = row.find_all("td")[-4]
                dob = dob_cells.text.strip() if dob_cells else "N/A"

                # Valeur marchande (dernière colonne avant la fin de ligne)
                market_value_cell = row.find_all("td")[-1]
                market_value = market_value_cell.text.strip() if market_value_cell else "N/A"

                # Ajouter toutes les infos
                players.append((league_name, season, club_name, player_name, dob, market_value))
    
    return players

def main():
    all_players = []

    for season in SEASONS:
        for league_name, league_code in LEAGUES.items():
            print(f"📌 Scraping {league_name} - Saison {season}...")
            club_links = get_club_links(league_code, season)
            print(f"✅ {len(club_links)} clubs trouvés pour {league_name} ({season})")

            for club_name, club_url in club_links.items():
                print(f"➡ Scraping {club_name}...")
                players = get_players_from_club(club_name, club_url, league_name, season)
                all_players.extend(players)
                time.sleep(2)  # Pause pour éviter d'être bloqué

            time.sleep(5)  # Pause entre chaque ligue pour éviter d'être bloqué

    # Sauvegarde des données dans un seul fichier CSV
    df = pd.DataFrame(all_players, columns=["Championnat", "Saison", "Club", "Joueur", "Date de Naissance", "Valeur Marchande"])
    df.to_csv("datasets/joueurs_grands_championnats.csv", index=False, encoding="utf-8-sig")

    print("🎉 Scraping terminé ! Données enregistrées dans 'joueurs_grands_championnats.csv'.")

if __name__ == "__main__":
    main()
