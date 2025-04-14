import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

LEAGUES = {
    "Ligue 1": "FR1",
    "Premier League": "GB1",
    "LaLiga": "ES1",
    "Bundesliga": "L1",
    "Serie A": "IT1"
}

JOURNEES_PAR_LIGUE = {
    "Ligue 1": 34,
    "Premier League": 38,
    "La Liga": 38,
    "Bundesliga": 34,
    "Serie A": 38
}

all_data = []

SEASONS = ["2021"]

for season in SEASONS:
    for league, code in LEAGUES.items():
        TOTAL_JOURNEES = JOURNEES_PAR_LIGUE[league]
        
        for journee in range(1, TOTAL_JOURNEES + 1):
            url = f"https://www.transfermarkt.fr/{league.lower().replace(' ', '-')}/formtabelle/wettbewerb/{code}?saison_id={season}&min=1&max={journee}"
            response = requests.get(url, headers=HEADERS)
            
            if response.status_code != 200:
                print(f"⚠️ Erreur {response.status_code} pour {league} - Journée {journee}")
                continue  
            
            soup = BeautifulSoup(response.text, "html.parser")

            tables = soup.find_all("table")
            
            if len(tables) < 2:
                print(f"⚠️ Pas de tableau trouvé pour {league} - Journée {journee}")
                continue
            
            table = tables[1]  

            rows = table.find_all("tr")[1:]  

            for row in rows:
                cols = row.find_all("td")
                if len(cols) < 10: 
                    continue
                
                position = cols[0].text.strip()
                equipe = cols[1].find("a")["title"].strip() if cols[1].find("a") and "title" in cols[1].find("a").attrs else cols[1].text.strip()
                victoire=cols[4].text.strip()
                defaite=cols[6].text.strip()
                nul=cols[5].text.strip()
                difference=cols[8].text.strip()
                points = cols[9].text.strip()
                buts = cols[7].text.strip()  # Supposons que c'est la colonne contenant "20:15"
                buts_marques, buts_encaisses = buts.split(":")

                all_data.append({
                    "season": season,
                    "league": league,
                    "matchday": journee,
                    "psoition": position,
                    "club": equipe,
                    "wins": victoire,
                    "draws": nul,
                    "losses": defaite,
                    "goals_for": buts_marques,
                    "goals_against": buts_encaisses,
                    "goal_difference": difference,
                    "points": points
                })

            print(f"✅ {league} - Journée {journee} récupérée.")
             

df = pd.DataFrame(all_data)

print(df.head())

df.to_csv("datasets/table_leagues2021.csv", index=False, encoding="utf-8")
print("📂 Classements sauvegardés dans 'classements_5_grands_championnats.csv'")