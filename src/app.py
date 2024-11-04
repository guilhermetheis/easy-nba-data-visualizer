import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from nba_api.stats.endpoints import playergamelogs
from nba_api.stats.static import players
import io

# Helper function to convert the Matplotlib figure to bytes for download
def fig_to_bytes(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    return buf.getvalue()

# Define a function to get NBA seasons from nba_api
def get_nba_seasons():
    # Define the current season endpoint range
    start_season = 1946  # NBA's first season
    current_season = 2024  # Update this for the current NBA season
    
    seasons = [f'{year}-{str(year + 1)[-2:]}' for year in range(start_season, current_season + 1)]
    return seasons[::-1]  # Reversed to show the latest season first

# Streamlit App Title and Description
st.title('Player PPG Evolution per Month and Individual Game Performance')
st.write('Select an NBA player to view their PPG evolution and game performance.')

# Select Player
all_players = players.get_players()
seasons = get_nba_seasons()
player_names = [player['full_name'] for player in all_players]
selected_player = st.selectbox('Choose a player', player_names)
selected_season = st.selectbox('Select NBA Season', seasons)

# Fetch and Display Player Stats
if selected_player and selected_season:
    # Find the player's ID from their name
    player_id = next(player['id'] for player in all_players if player['full_name'] == selected_player)

    # Retrieve player's game logs for the selected season
    game_logs = playergamelogs.PlayerGameLogs(
        season_nullable=selected_season,
        player_id_nullable=player_id,
        season_type_nullable='Regular Season'
    )

    # Convert game logs to DataFrame
    game_logs_df = game_logs.get_data_frames()[0]

    # Check if there is any data available
    if game_logs_df.empty:
        st.write(f"No data available for {selected_player} in the {selected_season} season.")
    else:
        # Prepare and clean up the data
        game_logs_df['GAME_DATE'] = pd.to_datetime(game_logs_df['GAME_DATE'])
        game_logs_df = game_logs_df[['GAME_DATE', 'PTS']]  # Only keep date and points columns
        game_logs_df = game_logs_df.sort_values(by='GAME_DATE').reset_index(drop=True)

        # Calculate cumulative game numbers and PPG
        game_logs_df['Game_Number'] = range(1, len(game_logs_df) + 1)
        game_logs_df['Month'] = game_logs_df['GAME_DATE'].dt.strftime("%b '%y")
        game_logs_df['PPG'] = game_logs_df['PTS'].cumsum() / (game_logs_df.index + 1)

        # Plot Points (PTS) as a bar plot and PPG as a line plot
        fig, ax = plt.subplots()

        # Bar plot for Points (PTS)
        ax.bar(game_logs_df['GAME_DATE'], game_logs_df['PTS'], color='lightblue', label='PTS')

        # Line plot for PPG
        ax.plot(game_logs_df['GAME_DATE'], game_logs_df['PPG'], color='red', marker='o', label='PPG')

        # Set labels and title
        ax.set_xlabel('Month')
        ax.set_ylabel('Points')
        ax.set_title(f'{selected_player} - PTS and PPG ({selected_season} Season)')

        # Set dynamic X-axis tick labels for each unique month in the data
        month_labels = game_logs_df['GAME_DATE'].dt.strftime('%b').unique()
        month_positions = game_logs_df['GAME_DATE'].dt.to_period('M').drop_duplicates().dt.to_timestamp()
        ax.set_xticks(month_positions)
        ax.set_xticklabels(month_labels, rotation=45)

        # Add legend
        ax.legend()

        # Display plot in Streamlit
        st.pyplot(fig)

        # Download button to save the plot as a PNG
        st.download_button(
            label='Download Plot as PNG',
            data=fig_to_bytes(fig),
            file_name=f'{selected_player}_{selected_season}_PTS_and_PPG.png',
            mime='image/png'
        )
