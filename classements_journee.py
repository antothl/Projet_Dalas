import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# Headers pour éviter d'être bloqué par Transfermarkt
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# Codes des championnats
LEAGUES = {
    "Ligue 1": "FR1",
    "Premier League": "GB1",
    "LaLiga": "ES1",
    "Bundesliga": "L1",
    "Serie A": "IT1"
}

# Nombre total de journées (généralement 38 sauf Bundesliga : 34)
JOURNEES_PAR_LIGUE = {
    "Ligue 1": 34,
    "Premier League": 38,
    "LaLiga": 38,
    "Bundesliga": 34,
    "Serie A": 38
}

# Stockage des données
all_data = []

# Scraping des classements pour chaque championnat et journée
for league, code in LEAGUES.items():
    TOTAL_JOURNEES = JOURNEES_PAR_LIGUE[league]
    
    for journee in range(1, TOTAL_JOURNEES + 1):
        url = f"https://www.transfermarkt.fr/{league.lower().replace(' ', '-')}/formtabelle/wettbewerb/{code}?saison_id=2024&min=1&max={journee}"
        response = requests.get(url, headers=HEADERS)
        
        if response.status_code != 200:
            print(f"⚠️ Erreur {response.status_code} pour {league} - Journée {journee}")
            continue  # Passe à la prochaine journée
        
        soup = BeautifulSoup(response.text, "html.parser")

        # Trouver le tableau du classement
        tables = soup.find_all("table")
        
        if len(tables) < 2:
            print(f"⚠️ Pas de tableau trouvé pour {league} - Journée {journee}")
            continue
        
        table = tables[1]  # Le tableau du classement

        # Extraction des lignes du tableau
        rows = table.find_all("tr")[1:]  # Ignorer l'en-tête

        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 10:  # Vérifier que la ligne est correcte
                continue
            
            position = cols[0].text.strip()
            equipe = cols[1].find("a")["title"].strip() if cols[1].find("a") and "title" in cols[1].find("a").attrs else cols[1].text.strip()
            points = cols[9].text.strip()

            all_data.append({
                "Championnat": league,
                "Journée": journee,
                "Position": position,
                "Équipe": equipe,
                "Points": points
            })

        print(f"✅ {league} - Journée {journee} récupérée.")
        time.sleep(2)  # Pause pour éviter d'être bloqué

# Convertir en DataFrame
df = pd.DataFrame(all_data)

# Affichage des premières lignes pour vérification
print(df.head())

# Sauvegarde des données
df.to_csv("classements_5_grands_championnats.csv", index=False, encoding="utf-8")
print("📂 Classements sauvegardés dans 'classements_5_grands_championnats.csv'")
