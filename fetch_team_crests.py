import requests
import os
import pandas as pd
from PIL import Image
from io import BytesIO

# Replace with your actual API key
api_key = '6873646605dd4457af95fabe8a0d261b'
api_url = 'https://api.football-data.org/v4/competitions/PL/teams?season=2023'
headers = {'X-Auth-Token': api_key}

# Path to standings data file (from process_data step)
data_file = 'data/standings_per_week.csv'

# Directory to save the crest images (Dash needs this folder name)
crest_dir = 'assets'

# Ensure the directory exists
os.makedirs(crest_dir, exist_ok=True)

# Load the team data from the standings file
standings_df = pd.read_csv(data_file)
teams_in_data = standings_df['Team'].unique()  # Extract unique teams from your data file

# Fetch team data from the football-data.org API (2023/24 season)
response = requests.get(api_url, headers=headers)
data = response.json()

# Create a dictionary for team crests (team name to crest URL)
team_crests = {team['name']: team['crest'] for team in data['teams']}

# Loop through each team in your standings data and download the crest
for team_name in teams_in_data:
    if team_name in team_crests:
        crest_url = team_crests[team_name]
        
        print(f"Downloading crest for {team_name}...")
        
        # Download the crest image
        img_response = requests.get(crest_url)
        
        # Check if the request was successful
        if img_response.status_code == 200:
            img = Image.open(BytesIO(img_response.content))
            
            # Save the image to the data/crests/ directory
            image_path = os.path.join(crest_dir, f"{team_name.replace(' ', '_')}_crest.png")
            img.save(image_path)
            print(f"Crest saved: {image_path}")
        else:
            print(f"Failed to download crest for {team_name}")
    else:
        print(f"No crest found for {team_name} in the API data.")

print("All relevant crests downloaded.")
