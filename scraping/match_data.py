import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import os
import re
from datetime import datetime
from urllib.parse import urlparse, parse_qs

class ESPNLeagueScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.base_url = 'https://www.espn.com'
        self.leagues = [
            {'code': 'ENG.1', 'name': 'Premier League'},
            {'code': 'ESP.1', 'name': 'La Liga'},
            {'code': 'GER.1', 'name': 'Bundesliga'},
            {'code': 'ITA.1', 'name': 'Serie A'},
            {'code': 'FRA.1', 'name': 'Ligue 1'}
        ]
        self.seasons = ['2020','2021','2022','2023']

    # def get_teams(self, league_code, season):
    #     url = f"{self.base_url}/soccer/teams/_/league/{league_code}/season/{season}"
    #     print(f"Fetching teams for {league_code} in season {season}...")

    #     response = requests.get(url, headers=self.headers)
    #     if response.status_code != 200:
    #         print(f"Failed to retrieve teams: Status code {response.status_code}")
    #         return []

    #     soup = BeautifulSoup(response.text, 'html.parser')
    #     teams = []
    #     team_sections = soup.select('section.TeamLinks')

    #     for section in team_sections:
    #         team_link = section.select_one('a.AnchorLink[href*="/soccer/team/_/id/"]')
    #         if team_link:
    #             href = team_link.get('href')
    #             team_id_match = re.search(r'/id/(\d+)/', href)
    #             team_name_match = re.search(r'/([^/]+)$', href)

    #             if team_id_match and team_name_match:
    #                 team_id = team_id_match.group(1)
    #                 team_name = team_name_match.group(1).replace('-', ' ').title()
    #                 team_h2 = section.select_one('h2')
    #                 if team_h2:
    #                     team_name = team_h2.text.strip()
    #                 teams.append({
    #                     'id': team_id,
    #                     'name': team_name,
    #                     'url': self.base_url + href
    #                 })

    #     print(f"Found {len(teams)} teams for {league_code} in season {season}")
    #     return teams

    def get_teams(self, league_code, season):
        url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{league_code}/teams?season={season}"
        print(f"Fetching teams for {league_code} in season {season}...")

        response = requests.get(url, headers=self.headers)
        if response.status_code != 200:
            print(f"Failed to retrieve teams: Status code {response.status_code}")
            return []

        data = response.json()
        teams = []
        for team in data.get('sports', [])[0].get('leagues', [])[0].get('teams', []):
            team_info = team.get('team', {})
            teams.append({
                'id': team_info.get('id'),
                'name': team_info.get('displayName'),
                'url': team_info.get('links', [])[0].get('href') if team_info.get('links') else None
            })

        print(f"Found {len(teams)} teams for {league_code} in season {season}")
        return teams

    def get_team_matches(self, team, league_code, season):
        team_id = team['id']
        team_name = team['name']
        results_url = f"{self.base_url}/soccer/team/results/_/id/{team_id}/league/{league_code}/season/{season}"
        print(f"Fetching matches for {team_name} ({league_code} {season})...")

        response = requests.get(results_url, headers=self.headers)
        if response.status_code != 200:
            print(f"Failed to retrieve matches for {team_name}: Status code {response.status_code}")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        matches = []
        result_tables = soup.select('div.ResponsiveTable.Table__results')

        for table in result_tables:
            title_elem = table.select_one('div.Table__Title')
            month_year = title_elem.text.strip() if title_elem else "Unknown Date"
            rows = table.select('tbody.Table__TBODY tr')

            for row in rows:

                competition_cell = row.select_one('td:last-child')
                # if not competition_cell or league_code not in competition_cell.text:
                #     continue

                try:
                    date_cell = row.select_one('td:first-child div.matchTeams')
                    match_date = date_cell.text.strip() if date_cell else "Unknown"

                    home_team_cell = row.select_one('td div.local a.Table__Team')
                    away_team_cell = row.select_one('td div.away a.Table__Team')
                    home_team = home_team_cell.text.strip() if home_team_cell else "Unknown"
                    away_team = away_team_cell.text.strip() if away_team_cell else "Unknown"

                    score_cell = row.select_one('td span.Table__Team.score a[href*="/soccer/match/_/gameId/"]')
                    if score_cell:
                        match_url = self.base_url + score_cell.get('href')
                        score_text = score_cell.text.strip()
                        game_id_match = re.search(r'/gameId/(\d+)/', match_url)
                        game_id = game_id_match.group(1) if game_id_match else "unknown"
                        result_cell = row.select_one('td span[data-testid="result"] a')
                        match_status = result_cell.text.strip() if result_cell else ""

                        if match_status == "FT":
                            matches.append({
                                'league': league_code,
                                'season': season,
                                'date': f"{match_date}, {month_year}",
                                'home_team': home_team,
                                'away_team': away_team,
                                'score': score_text,
                                'game_id': game_id,
                                'match_url': match_url,
                                'team_source': team_name
                            })

                except Exception as e:
                    print(f"Error processing match row: {str(e)}")
                    continue
        
        print('Number Matches Retreived:', len(matches))
        return matches

    def get_match_stats(self, match):
        match_url = match['match_url']
        game_id = match['game_id']
        print(f"Processing match: {match['home_team']} vs {match['away_team']} ({match['league']} {match['season']})")
        time.sleep(random.uniform(1, 2))

        try:
            response = requests.get(match_url, headers=self.headers)
            if response.status_code != 200:
                print(f"Failed to retrieve match data: Status code {response.status_code}")
                return None

            soup = BeautifulSoup(response.text, 'html.parser')
            match_data = {
                'game_id': game_id,
                'league': match['league'],
                'season': match['season'],
                'date': match['date'],
                'home_team': match['home_team'],
                'away_team': match['away_team'],
                'score': match['score']
            }

            date_element = soup.select_one('div.n8.GameInfo__Location span.fw-bold')
            if date_element:
                match_data['full_date'] = date_element.text.strip()

            stats_section = soup.select_one('section[data-testid="prism-LayoutCard"]')
            if stats_section:
                desired_stats = ["Possession", "Shots on Goal", "Shot Attempts", "Yellow Cards", "Corner Kicks", "Saves"]
                stats_map = {
                    "Possession": ("home_possession", "away_possession"),
                    "Shots on Goal": ("home_shots_on_goal", "away_shots_on_goal"),
                    "Shot Attempts": ("home_shot_attempts", "away_shot_attempts"),
                    "Yellow Cards": ("home_yellow_cards", "away_yellow_cards"),
                    "Corner Kicks": ("home_corner_kicks", "away_corner_kicks"),
                    "Saves": ("home_saves", "away_saves")
                }
                stat_rows = stats_section.find_all('div', class_='LOSQp')
                for row in stat_rows:
                    label_elem = row.find('span', class_='OkRBU')
                    if not label_elem:
                        continue
                    label_text = label_elem.text.strip()
                    if label_text not in desired_stats:
                        continue
                    value_spans = row.find_all('span', class_='bLeWt')
                    if len(value_spans) >= 2:
                        home_val = value_spans[0].text.strip()
                        away_val = value_spans[1].text.strip()
                        home_key, away_key = stats_map[label_text]
                        match_data[home_key] = home_val
                        match_data[away_key] = away_val

            print('Number of columns match data:', len(match_data))
            return match_data

        except Exception as e:
            print(f"Error processing match {match_url}: {str(e)}")
            return None

    def deduplicate_matches(self, all_matches):
        unique_matches = {}
        for match in all_matches:
            game_id = match['game_id']
            if game_id not in unique_matches:
                unique_matches[game_id] = match
        print(f"Removed {len(all_matches) - len(unique_matches)} duplicate matches")
        return list(unique_matches.values())

    def scrape_all(self):
        all_stats = []
        for league in self.leagues:
            for season in self.seasons:
                teams = self.get_teams(league['code'], season)
                all_matches = []
                for team in teams:
                    matches = self.get_team_matches(team, league['code'], season)
                    all_matches.extend(matches)
                    time.sleep(random.uniform(2, 3))
                unique_matches = self.deduplicate_matches(all_matches)
                for i, match in enumerate(unique_matches):
                    print(f"\nProcessing match {i+1}/{len(unique_matches)} for {league['code']} {season}")
                    stats = self.get_match_stats(match)
                    if stats:
                        all_stats.append(stats)

        self.save_all_data(all_stats)
        return all_stats

    def save_all_data(self, data):
        if not data:
            print("No data to save")
            return

        if not os.path.exists('data'):
            os.makedirs('data')

        df = pd.DataFrame(data).fillna('N/A')
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"archive/data/top5leagues_all_stats_{timestamp}.csv"
        df.to_csv(filename, index=False)
        print(f"\nAll data saved to {filename}")
        print(f"\nDataset Summary:")
        print(f"Total matches: {len(df)}")
        print(f"Total statistics columns: {len(df.columns) - 7}")
        return df

if __name__ == "__main__":
    scraper = ESPNLeagueScraper()
    all_stats_df = scraper.scrape_all()
