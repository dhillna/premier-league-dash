import pandas as pd

# Load match data from CSV
def load_data(file_path='data/football_matches.csv'):
    return pd.read_csv(file_path)

# Assign game weeks to each match based on the team's match order
def assign_game_weeks(matches_df):
    matches_df['Game_Week'] = 0  # Initialize game week column
    
    # Process each team independently to ensure we assign game weeks correctly
    teams = pd.concat([matches_df['Home_Team'], matches_df['Away_Team']]).unique()
    
    # For each team, assign game weeks based on the order of matches
    for team in teams:
        # Get the matches for the current team (both home and away), sorted by date
        team_matches = matches_df[(matches_df['Home_Team'] == team) | (matches_df['Away_Team'] == team)].sort_values('Date')
        
        # Assign game weeks in sequential order for this team
        team_matches['Game_Week'] = range(1, len(team_matches) + 1)
        
        # Merge the game weeks back into the main dataframe
        matches_df.update(team_matches)
    
    return matches_df

# Calculate standings by iterating through each game week
def calculate_points_and_standings(matches_df):
    standings = []  # Store standings per game week
    teams_stats = {}  # To track points, wins, losses, draws, goals for/against, goal difference
    
    # Sort matches by game week
    matches_df = matches_df.sort_values('Game_Week')
    
    # Process matches week by week
    for game_week in sorted(matches_df['Game_Week'].unique()):
        week_matches = matches_df[matches_df['Game_Week'] == game_week]
        
        # Update team stats based on match results for the current week
        for idx, match in week_matches.iterrows():
            home_team = match['Home_Team']
            away_team = match['Away_Team']
            home_score = match['Home_Score']
            away_score = match['Away_Score']
            
            # Initialize team stats if not already present
            if home_team not in teams_stats:
                teams_stats[home_team] = {'points': 0, 'wins': 0, 'draws': 0, 'losses': 0,
                                          'goals_for': 0, 'goals_against': 0, 'goal_diff': 0}
            if away_team not in teams_stats:
                teams_stats[away_team] = {'points': 0, 'wins': 0, 'draws': 0, 'losses': 0,
                                          'goals_for': 0, 'goals_against': 0, 'goal_diff': 0}
            
            # Calculate the result for the home team
            if home_score > away_score:
                teams_stats[home_team]['points'] += 3
                teams_stats[home_team]['wins'] += 1
                teams_stats[away_team]['losses'] += 1
            elif home_score < away_score:
                teams_stats[away_team]['points'] += 3
                teams_stats[away_team]['wins'] += 1
                teams_stats[home_team]['losses'] += 1
            else:
                teams_stats[home_team]['points'] += 1
                teams_stats[away_team]['points'] += 1
                teams_stats[home_team]['draws'] += 1
                teams_stats[away_team]['draws'] += 1
            
            # Update goals and goal difference
            teams_stats[home_team]['goals_for'] += home_score
            teams_stats[home_team]['goals_against'] += away_score
            teams_stats[away_team]['goals_for'] += away_score
            teams_stats[away_team]['goals_against'] += home_score
            teams_stats[home_team]['goal_diff'] = teams_stats[home_team]['goals_for'] - teams_stats[home_team]['goals_against']
            teams_stats[away_team]['goal_diff'] = teams_stats[away_team]['goals_for'] - teams_stats[away_team]['goals_against']
        
        # After updating team stats for this game week, sort teams by tie-breaking rules
        sorted_teams = sorted(teams_stats.items(), key=lambda x: (x[1]['points'], x[1]['goal_diff'], x[1]['goals_for']), reverse=True)
        
        # Save the standings for this week
        for position, (team, stats) in enumerate(sorted_teams, 1):
            standings.append({
                'Team': team,
                'Game_Week': game_week,
                'Position': position,
                'Points': stats['points'],
                'Wins': stats['wins'],
                'Draws': stats['draws'],
                'Losses': stats['losses'],
                'Goals_For': stats['goals_for'],
                'Goals_Against': stats['goals_against'],
                'Goal_Diff': stats['goal_diff']
            })
    
    standings_df = pd.DataFrame(standings)
    return standings_df

# Main process
if __name__ == '__main__':
    # Load the match data
    matches_df = load_data('data/football_matches.csv')

    # Assign game weeks based on team match order
    matches_df = assign_game_weeks(matches_df)

    # Calculate standings per week
    standings_df = calculate_points_and_standings(matches_df)

    # Save standings to a CSV file
    standings_df.to_csv('data/standings_per_week.csv', index=False)
