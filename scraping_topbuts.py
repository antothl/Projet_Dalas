import requests
from bs4 import BeautifulSoup
import pandas as pd

# URL de la page Wikipédia
urls = ["https://fr.wikipedia.org/wiki/Meilleurs_buteurs_du_championnat_de_France_de_football","https://fr.wikipedia.org/wiki/Meilleurs_buteurs_du_championnat_d%27Espagne_de_football","https://fr.wikipedia.org/wiki/Meilleurs_buteurs_du_championnat_d%27Italie_de_football","https://fr.wikipedia.org/wiki/Meilleurs_buteurs_du_championnat_d%27Angleterre_de_football","https://fr.wikipedia.org/wiki/Meilleurs_buteurs_du_championnat_d%27Allemagne_de_football"]
leagues = ['Ligue 1', 'Liga', 'Serie A', 'Premier League', 'Bundesliga']
all_data = []

for url,league in zip(urls,leagues) :
    # Envoyer une requête HTTP GET
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"}
    response = requests.get(url, headers=headers)

    # Vérifier si la requête est réussie
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Trouver le titre "Palmarès par édition"
        heading = soup.find("h3", {"id": lambda x: x and "Palmarès_par_édition" in x})
        if heading:
            # Trouver le tableau suivant le titre
            table = heading.find_next("table", class_="wikitable")
            
            if table:
                # Extraire les données du tableau
                rows = table.find_all("tr")
                
                for row in rows[1:]:  # Ignorer la première ligne (en-têtes)
                    columns = row.find_all(["td", "th"])
                    if len(columns) >= 4:  # Vérifier qu'il y a suffisamment de colonnes
                        season = columns[0].text.strip()  # Saison
                        player = columns[1].text.strip()  # Joueur
                        team = columns[2].text.strip()  # Équipe
                        goals = columns[3].text.strip()  # Nombre de buts
                        
                        # Ajouter les données extraites à la liste
                        all_data.append({
                            "Championnat": league,
                            "Saison": season,
                            "Joueur": player,
                            "Équipe": team,
                            "Buts": goals
                        })
                
            else:
                print("Tableau introuvable après le titre 'Palmarès par édition'.")
        else:
            print("Titre 'Palmarès par édition' introuvable.")
    else:
        print(f"Erreur lors de la requête (code : {response.status_code})")

df = pd.DataFrame(all_data)
filename = f"top_buts.csv"
df.to_csv(filename, index=False, encoding="utf-8")
