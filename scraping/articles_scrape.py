import bs4
import re
import os
from urllib import request

url_teams = "https://www.espn.co.uk/football/teams"
prefix = "https://www.espn.co.uk"
base_folder = "articles"

request_text = request.urlopen(url_teams).read()
page = bs4.BeautifulSoup(request_text, "lxml")

# print(page)

elements = page.find_all("option")

url_team_pages = []

# Print the elements and their text content
for element in elements:
    data_team_url = element.get("data-url")  # Safely get the 'data-url' attribute
    if data_team_url:
        url_team_pages.append(data_team_url)


# Regular expression for the desired URL pattern
pattern = r'^/football/teams/_/league/[A-Z]+\.1.*$'

# Filter the URLs using a list comprehension
urls_top_leagues = [url for url in url_team_pages if re.match(pattern, url)]
urls_top_leagues = urls_top_leagues[:8]

for url_league in urls_top_leagues:
    
    league_name = url_league.rsplit("/", 1)[-1]
    target_folder = os.path.join(base_folder, league_name)

    if not os.path.exists(target_folder):  # Check if the folder already exists
        os.mkdir(target_folder)


    # Leagues in team
    url_top_leagues_full = prefix + url_league

    request_text_league = request.urlopen(url_top_leagues_full).read()
    page_league = bs4.BeautifulSoup(request_text_league, "lxml")

    team_sections = page_league.find_all("section", class_="TeamLinks flex items-center")

    # Retrieve and print all href attributes
    team_links = [sec.find("a", href=True)['href'] for sec in team_sections]

    for url_team in team_links:
        
        team_name = url_team.rsplit("/", 1)[-1]
        target_folder_team = os.path.join(base_folder, league_name, team_name)

        if not os.path.exists(target_folder_team):  # Check if the folder already exists
            os.mkdir(target_folder_team)

        # Team
        url_single_team = prefix + url_team

        request_text_team = request.urlopen(url_single_team).read()
        page_team = bs4.BeautifulSoup(request_text_team, "lxml")

        article_sections = page_team.find_all("article")

        article_links = []

        # Loop through each article section
        for sec in article_sections:
            # Find the first <a> tag with an href attribute
            link = sec.find("a", href=True)
            if link:  # Check if an <a> tag with href exists
                href = link["href"]  # Extract the href attribute
                article_links.append(href)  # Add the href to the list

        
        article_id = 1
        for article_url in article_links:
            url_article = prefix + article_url

            request_article = request.urlopen(url_article).read()
            page_article = bs4.BeautifulSoup(request_article, "lxml")

            article_text_string = [section.text.strip() for section in page_article.find_all("p")]
            article_text = " ".join(article_text_string).replace("\n", " ")
            
            file_name = f"article{article_id}.txt"
            file_path = os.path.join(target_folder_team, file_name)

            # Save the text to the file
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(article_text)

            article_id += 1




