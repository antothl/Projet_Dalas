import requests
from bs4 import BeautifulSoup

# URL de la page du classement
url = "https://www.espn.com/soccer/table/_/league/eng.1"

# Envoyer une requête HTTP GET
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"}
response = requests.get(url, headers=headers)

# Vérifier si la requête est réussie
if response.status_code == 200:
    soup = BeautifulSoup(response.content, "html.parser")
    
    # Trouver les deux tableaux
    tables = soup.find_all("table", class_="Table")
    
    if len(tables) >= 2:
        # Premier tableau : rang et nom de l'équipe
        team_table = tables[0]
        team_rows = team_table.find("tbody").find_all("tr")
        
        # Deuxième tableau : statistiques
        stats_table = tables[1]
        stats_rows = stats_table.find("tbody").find_all("tr")
        
        if len(team_rows) == len(stats_rows):  # Assurez-vous qu'ils ont la même longueur
            for team_row, stats_row in zip(team_rows, stats_rows):
                # Extraction des informations du premier tableau
                rank = team_row.find("span", class_="team-position").text.strip()  # Classement
                
                team_tag = team_row.find("span", class_="hide-mobile")
                if team_tag:
                    team = team_tag.text.strip()  # Nom complet de l'équipe
                else:
                    team = "Équipe inconnue"
                
                # Extraction des statistiques du deuxième tableau
                stats_columns = stats_row.find_all("td")
                played = stats_columns[0].text.strip()
                wins = stats_columns[1].text.strip()
                draws = stats_columns[2].text.strip()
                losses = stats_columns[3].text.strip()
                goals_for = stats_columns[4].text.strip()
                goals_against = stats_columns[5].text.strip()
                goal_diff = stats_columns[6].text.strip()
                points = stats_columns[7].text.strip()
                
                # Afficher les données extraites
                print(f"{rank}. {team} - Pts: {points}, Joués: {played}, G+: {goals_for}, G-: {goals_against}, Diff: {goal_diff}")
        else:
            print("Les tableaux n'ont pas le même nombre de lignes.")
    else:
        print("Impossible de trouver les deux tableaux nécessaires.")
else:
    print(f"Erreur lors de la requête (code : {response.status_code})")
