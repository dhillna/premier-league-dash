import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
import numpy as np
import os

# Load the standings data
standings_df = pd.read_csv('data/standings_per_week.csv')

# Calculate averages and standard deviations per game week
average_points = standings_df.groupby('Game_Week')['Points'].mean()
std_dev_points = standings_df.groupby('Game_Week')['Points'].std()
average_goals_for = standings_df.groupby('Game_Week')['Goals_For'].mean()
std_dev_goals_for = standings_df.groupby('Game_Week')['Goals_For'].std()
average_goals_against = standings_df.groupby('Game_Week')['Goals_Against'].mean()
std_dev_goals_against = standings_df.groupby('Game_Week')['Goals_Against'].std()

# Standard deviation of goal difference (average is always zero)
std_dev_goal_diff = standings_df.groupby('Game_Week')['Goal_Diff'].std()

# Define color scheme
team_color = 'navy' # Main team color
average_color = 'crimson' # Average line color 
std_dev_color = 'rgba(192, 192, 192, 0.3)'  # Standard deviation fill color (gray with transparency)

# Load a Bootstrap template
load_figure_template('simplex')

# Initialize the Dash app with a Bootstrap theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX])

# Get the list of unique teams for the dropdown, sorted alphabetically
teams = sorted(standings_df['Team'].unique())

# Layout of the app using Bootstrap components
app.layout = dbc.Container([
    # Header section with Premier League logo
    dbc.Card(
        dbc.CardBody([
            dbc.Row([
                dbc.Col(
                    html.Img(
                        src='https://upload.wikimedia.org/wikipedia/en/f/f2/Premier_League_Logo.svg', 
                        height='100px'
                    ), 
                    width=3
                ),
                dbc.Col(
                    html.H1("23/24 Season - Club Performance Dashboard"), 
                    width=9,
                    style={'alignSelf': 'center'}  # Vertically centers the text column relative to the logo
                ),
            ], 
            align='center'  # Aligns the items in the row along the cross-axis (vertically)
            )
        ]),
        className="mb-4",
        style={"backgroundColor": "white", "boxShadow": "0 4px 8px rgba(0, 0, 0, 0.1)"}
    ),

    # Club crest and team dropdown
    dbc.Row([
        dbc.Col(
            html.Img(id='club-crest', height='100px'),  # Placeholder for club crest
            width=2
        ),
        dbc.Col(
            dcc.Dropdown(
                id='team-dropdown',
                options=[{'label': team, 'value': team} for team in teams],
                value=teams[0],  # Default value
                clearable=False
            ), width=3
        )
    ], align='center'),

    # Row for charts with added vertical space
    dbc.Row([
        dbc.Col(dcc.Graph(id='cumulative-points-chart'), width=6),
        dbc.Col(dcc.Graph(id='cumulative-goals-scored-chart'), width=6)
    ], style={'marginTop': '20px'}),  # Adds vertical space above the charts

    dbc.Row([
        dbc.Col(dcc.Graph(id='cumulative-goals-conceded-chart'), width=6),
        dbc.Col(dcc.Graph(id='cumulative-goal-diff-chart'), width=6)
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id='standings-line-chart'), width=12)  # League position chart moved to bottom
    ]),
    dbc.Row([
        dbc.Col(html.Div(id='final-summary-table'), width=12)
    ])
], fluid=True)

# Callback for club crest image
@app.callback(
    Output('club-crest', 'src'),
    [Input('team-dropdown', 'value')]
)
def update_club_crest(selected_team):
    formatted_team_name = selected_team.replace(' ', '_') + '_crest.png'
    return app.get_asset_url(formatted_team_name)

# Callback for cumulative points chart with average and shaded std deviation
@app.callback(
    Output('cumulative-points-chart', 'figure'),
    [Input('team-dropdown', 'value')]
)
def update_cumulative_points_chart(selected_team):
    team_data = standings_df[standings_df['Team'] == selected_team]
    fig = go.Figure()

    # Average points line
    fig.add_trace(go.Scatter(x=average_points.index, y=average_points, mode='lines', name='Average', line=dict(color=average_color)))

    # Shaded standard deviation region
    fig.add_trace(go.Scatter(
        x=average_points.index.tolist() + average_points.index.tolist()[::-1],
        y=(average_points + std_dev_points).tolist() + (average_points - std_dev_points).tolist()[::-1],
        fill='toself',
        fillcolor=std_dev_color,
        line=dict(color='rgba(255,255,255,0)'),
        name="± 1 S.D.",
        showlegend=True
    ))

    # Team's points
    fig.add_trace(go.Scatter(x=team_data['Game_Week'], y=team_data['Points'], mode='lines+markers', name='Points', line=dict(color=team_color)))

    fig.update_layout(title=f"{selected_team} - Cumulative Points", xaxis_title='Game Week', yaxis_title='Points')
    return fig

# Callback for cumulative goals scored chart with average and shaded std deviation
@app.callback(
    Output('cumulative-goals-scored-chart', 'figure'),
    [Input('team-dropdown', 'value')]
)
def update_cumulative_goals_scored_chart(selected_team):
    team_data = standings_df[standings_df['Team'] == selected_team]
    fig = go.Figure()

    # Average goals for line
    fig.add_trace(go.Scatter(x=average_goals_for.index, y=average_goals_for, mode='lines', name='Average', line=dict(color=average_color)))

    # Shaded standard deviation region
    fig.add_trace(go.Scatter(
        x=average_goals_for.index.tolist() + average_goals_for.index.tolist()[::-1],
        y=(average_goals_for + std_dev_goals_for).tolist() + (average_goals_for - std_dev_goals_for).tolist()[::-1],
        fill='toself',
        fillcolor=std_dev_color,
        line=dict(color='rgba(255,255,255,0)'),
        name="± 1 S.D.",
        showlegend=True
    ))

    # Team's goals for
    fig.add_trace(go.Scatter(x=team_data['Game_Week'], y=team_data['Goals_For'], mode='lines+markers', name='Goals For', line=dict(color=team_color)))

    fig.update_layout(title=f"{selected_team} - Cumulative Goals Scored", xaxis_title='Game Week', yaxis_title='Goals Scored')
    return fig

# Callback for cumulative goals conceded chart with average and shaded std deviation
@app.callback(
    Output('cumulative-goals-conceded-chart', 'figure'),
    [Input('team-dropdown', 'value')]
)
def update_cumulative_goals_conceded_chart(selected_team):
    team_data = standings_df[standings_df['Team'] == selected_team]
    fig = go.Figure()

    # Average goals against line
    fig.add_trace(go.Scatter(x=average_goals_against.index, y=average_goals_against, mode='lines', name='Average', line=dict(color=average_color)))

    # Shaded standard deviation region
    fig.add_trace(go.Scatter(
        x=average_goals_against.index.tolist() + average_goals_against.index.tolist()[::-1],
        y=(average_goals_against + std_dev_goals_against).tolist() + (average_goals_against - std_dev_goals_against).tolist()[::-1],
        fill='toself',
        fillcolor=std_dev_color,
        line=dict(color='rgba(255,255,255,0)'),
        name="± 1 S.D.",
        showlegend=True
    ))

    # Team's goals against
    fig.add_trace(go.Scatter(x=team_data['Game_Week'], y=team_data['Goals_Against'], mode='lines+markers', name='Goals Against', line=dict(color=team_color)))

    fig.update_layout(title=f"{selected_team} - Cumulative Goals Conceded", xaxis_title='Game Week', yaxis_title='Goals Conceded')
    return fig

# Callback for cumulative goal difference chart with shaded std deviation
@app.callback(
    Output('cumulative-goal-diff-chart', 'figure'),
    [Input('team-dropdown', 'value')]
)
def update_cumulative_goal_diff_chart(selected_team):
    team_data = standings_df[standings_df['Team'] == selected_team]
    fig = go.Figure()

    # Shaded standard deviation region (no average, mean is 0)
    fig.add_trace(go.Scatter(
        x=std_dev_goal_diff.index.tolist() + std_dev_goal_diff.index.tolist()[::-1],
        y=(std_dev_goal_diff).tolist() + (-std_dev_goal_diff).tolist()[::-1],
        fill='toself',
        fillcolor=std_dev_color,
        line=dict(color='rgba(255,255,255,0)'),
        name="± 1 S.D.",
        showlegend=True
    ))

     # Team's goal difference
    fig.add_trace(go.Scatter(x=team_data['Game_Week'], y=team_data['Goal_Diff'], mode='lines+markers', name='Goal Difference', line=dict(color=team_color)))

    # Add a horizontal line at zero
    fig.add_hline(y=0, line_dash="dot")

    fig.update_layout(
        title=f"{selected_team} - Cumulative Goal Difference",
        xaxis_title='Game Week',
        yaxis_title='Goal Difference'
    )
    return fig

# Callback for updating the league position chart
@app.callback(
    Output('standings-line-chart', 'figure'),
    [Input('team-dropdown', 'value')]
)
def update_standings_chart(selected_team):
    team_data = standings_df[standings_df['Team'] == selected_team]
    fig = go.Figure(
        go.Scatter(x=team_data['Game_Week'], y=team_data['Position'], mode='lines+markers', line=dict(color=team_color))
    )
    fig.update_layout(title=f"{selected_team} - League Position per Game Week",
                      xaxis_title='Game Week',
                      yaxis_title='League Position',
                      yaxis=dict(range=[20.5, 0.5],  # Adjusted to give headroom above 1
                                 autorange=False,
                                 nticks=20,
                                 tickmode='linear'))  # Fixed y-axis range from 1 to 20
    return fig

# Callback for final summary table
@app.callback(
    Output('final-summary-table', 'children'),
    [Input('team-dropdown', 'value')]
)
def update_final_summary_table(selected_team):
    # Filter the data for the final game week (38) for the selected team
    final_week_data = standings_df[(standings_df['Team'] == selected_team) & (standings_df['Game_Week'] == 38)].iloc[0]
    
    # Add the final standing (position in game week 38)
    final_position = final_week_data['Position']
    
    return html.Div([
        html.H3("End of Season Summary"),  # Added header for the summary
        html.Ul([
            html.Li(f"Team: {final_week_data['Team']}"),
            html.Li(f"Final League Position: {final_position}"),  # Display final standing
            html.Li(f"Points: {final_week_data['Points']}"),
            html.Li(f"Wins: {final_week_data['Wins']}"),
            html.Li(f"Draws: {final_week_data['Draws']}"),
            html.Li(f"Losses: {final_week_data['Losses']}"),
            html.Li(f"Goals For: {final_week_data['Goals_For']}"),
            html.Li(f"Goals Against: {final_week_data['Goals_Against']}"),
            html.Li(f"Goal Difference: {final_week_data['Goal_Diff']}")
        ], style={'list-style-type': 'none', 'padding': '20px'})
    ])

server = app.server  # Add this line if not already there

if __name__ == '__main__':
    # Use port from environment variable if available (for Render), otherwise use 8050
    port = int(os.environ.get('PORT', 8050))
    app.run_server(debug=False, host='0.0.0.0', port=port)