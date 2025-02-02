import requests
from bs4 import BeautifulSoup
import pandas as pd

seasons = ['2020', '2021', '2022', '2023', '2024']
leagues = ['ENG.1', 'ita.1', 'ger.1', 'fra.1', 'esp.1']

# Parcourir chaque championnat
for league in leagues:
    league_data = []  # Stocker les données de toutes les saisons pour ce championnat
    
    for season in seasons:
        # URL de la page du classement
        url = f"https://www.espn.com/soccer/standings/_/league/{league}/season/{season}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        }
        
        response = requests.get(url, headers=headers)

        # Vérifier si la requête est réussie
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            tables = soup.find_all("table", class_="Table")
            
            if len(tables) >= 2:
                # Extraction des données des deux tableaux
                team_table = tables[0]
                stats_table = tables[1]
                team_rows = team_table.find("tbody").find_all("tr")
                stats_rows = stats_table.find("tbody").find_all("tr")
                
                if len(team_rows) == len(stats_rows):
                    for team_row, stats_row in zip(team_rows, stats_rows):
                        # Extraction des informations du premier tableau (rang et équipe)
                        rank_tag = team_row.find("span", class_="team-position")
                        rank = rank_tag.text.strip() if rank_tag else "N/A"
                        
                        team_tag = team_row.find("span", class_="hide-mobile")
                        team = team_tag.text.strip() if team_tag else "Équipe inconnue"
                        
                        # Extraction des statistiques du deuxième tableau
                        stats_columns = stats_row.find_all("td")
                        if len(stats_columns) >= 8:  # Vérification du nombre de colonnes
                            played = stats_columns[0].text.strip()
                            wins = stats_columns[1].text.strip()
                            draws = stats_columns[2].text.strip()
                            losses = stats_columns[3].text.strip()
                            goals_for = stats_columns[4].text.strip()
                            goals_against = stats_columns[5].text.strip()
                            goal_diff = stats_columns[6].text.strip()
                            points = stats_columns[7].text.strip()
                            
                            # Ajouter les données à la liste
                            league_data.append([
                                season, rank, team, played, wins, draws, losses,
                                goals_for, goals_against, goal_diff, points
                            ])
                        else:
                            print(f"Ligne de statistiques mal formée pour {team} ({season}).")
                else:
                    print(f"Nombre de lignes incohérent pour {league} ({season}).")
            else:
                print(f"Les tableaux nécessaires sont absents pour {league} ({season}).")
        else:
            print(f"Erreur lors de la requête {url} (code : {response.status_code})")
    
    # Enregistrement des données dans un fichier CSV
    if league_data:
        df = pd.DataFrame(league_data, columns=[
            "Season", "Rank", "Team", "Played", "Wins", "Draws", "Losses",
            "Goals For", "Goals Against", "Goal Difference", "Points"
        ])
        league_name = league.replace('.', '_')  # Remplacer les points dans le nom de fichier
        filename = f"{league_name}_standings.csv"
        df.to_csv(filename, index=False, encoding="utf-8")
        print(f"Fichier enregistré : {filename}")
    else:
        +
        print(f"Aucune donnée disponible pour {league}.")
