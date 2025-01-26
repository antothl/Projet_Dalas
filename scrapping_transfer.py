from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import time
from bs4 import BeautifulSoup



# Configuration de Selenium (mode sans interface graphique)
options = Options()
options.add_argument("--headless")  # Mode sans affichage
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

service = Service("C:/chromedriver-win64/chromedriver.exe")
driver = webdriver.Chrome(service=service, options=options)

# Ouvrir la page des transferts sur ESPN
url = "https://www.espn.com/soccer/transfers"
driver.get(url)

# Attendre que la page se charge
time.sleep(5)

# Scroller jusqu'à la fin pour charger toutes les données dynamiques
last_height = driver.execute_script("return document.body.scrollHeight")
while True:
    # Scroller vers le bas
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)  # Attendre que la page charge les nouvelles données

    # Vérifier si le scroll atteint le bas de la page
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

# Extraire le contenu HTML une fois toutes les données chargées
html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')

# Fermer le navigateur
driver.quit()

# Trouver toutes les lignes du tableau des transferts
rows = soup.find_all('tr', class_='Table__TR Table__TR--sm Table__even')

# Parcourir chaque ligne pour extraire les données
for row in rows:
    # Extraire la date (première colonne)
    date = row.find_all('td')[0].find('span', class_='w-100').text.strip()

    # Cas où le joueur a un lien (balise <a>)
    player_name_tag = row.find_all('td')[1]  # La colonne contenant le nom du joueur
    player_link = player_name_tag.find('a', class_='AnchorLink')  # Chercher une balise <a>
    
    if player_link:
        # Si une balise <a> est trouvée
        player_name = player_link.text.strip()
    else:
        # Sinon, chercher dans une balise <span>
        player_name_span = player_name_tag.find('span')  # Chercher une balise <span>
        player_name = player_name_span.text.strip() if player_name_span else "Nom inconnu"
    
    # Extraire les autres données (par exemple, le club de départ, etc.)
    from_club = row.find_all('td')[2].find('span', class_='hide-mobile').text.strip()
    to_club = row.find_all('td')[4].find('span', class_='hide-mobile').text.strip()
    fee = row.find_all('td')[5].find('span', class_='w-100').text.strip()

    # Afficher les données extraites
    print(f"Joueur : {player_name}, De : {from_club}, À : {to_club}, Montant : {fee}")
