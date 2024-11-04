import requests
import pandas as pd

# Your API key from Football-Data.org
API_KEY = 'YOUR_API_KEY_HERE'

# Base URL for the Football-Data.org API
BASE_URL = 'https://api.football-data.org/v4/'

# Headers required for the API
headers = {'X-Auth-Token': API_KEY}

# Function to fetch matches from a specific competition and season
def fetch_matches(competition_id, season_start, season_end):
    url = f'{BASE_URL}competitions/{competition_id}/matches'
    params = {'dateFrom': season_start, 'dateTo': season_end}
    response = requests.get(url, headers=headers, params=params)
    return response.json()

# Function to process the API response and save data
def process_and_save_data(competition_id, season_start, season_end, output_file='data/football_matches.csv'):
    data = fetch_matches(competition_id, season_start, season_end)
    matches = []
    
    # Parse match details
    for match in data['matches']:
        # Check if full-time score is available
        if 'score' in match and 'fullTime' in match['score']:
            home_score = match['score']['fullTime'].get('home', None)
            away_score = match['score']['fullTime'].get('away', None)
        else:
            home_score = None
            away_score = None

        # Append match data to the list (even if score is missing)
        matches.append({
            'Match_ID': match['id'],
            'Date': match['utcDate'],
            'Home_Team': match['homeTeam']['name'],
            'Away_Team': match['awayTeam']['name'],
            'Home_Score': home_score,
            'Away_Score': away_score,
            'Status': match['status']
        })

    # Save to CSV
    matches_df = pd.DataFrame(matches)
    matches_df.to_csv(output_file, index=False)
    print(f"Data saved to {output_file}")

# Example call to fetch Premier League (competition_id = 2021) for 2023-2024 season
if __name__ == '__main__':
    season_start = '2023-08-01'  # Start of the 2023-2024 season
    season_end = '2024-05-31'    # End of the 2023-2024 season
    process_and_save_data(2021, season_start, season_end)
