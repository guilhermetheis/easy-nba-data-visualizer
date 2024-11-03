import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from nba_api.stats.static import players
from nba_api.stats.endpoints import playercareerstats
from nba_api.stats.library.parameters import SeasonAll
import io

# Helper function to convert the Matplotlib figure to bytes for download
def fig_to_bytes(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    return buf.getvalue()


# Streamlit App Title and Description
st.title("NBA Player PPG Over Seasons")
st.write("Select an NBA player to view their Points Per Game (PPG) over their career.")

# Select Player
all_players = players.get_players()
player_names = [player['full_name'] for player in all_players]
selected_player = st.selectbox("Choose a player", player_names)

# Fetch and Display Player Stats
if selected_player:
    # Find the player's ID from their name
    player_id = next(player['id'] for player in all_players if player['full_name'] == selected_player)

    # Retrieve player's career stats
    career = playercareerstats.PlayerCareerStats(player_id=player_id).get_data_frames()[0]

    # Calculate Points Per Game (PPG) as Points / Games Played for each season
    career['PPG'] = career['PTS'] / career['GP']

    # Plot PPG over the seasons
    fig, ax = plt.subplots()
    ax.plot(career['SEASON_ID'], career['PPG'], marker='o', color='b', linestyle='-')
    ax.set_xlabel("Season")
    ax.set_ylabel("Points Per Game (PPG)")
    ax.set_title(f"{selected_player} - PPG Over Seasons")
    plt.xticks(rotation=45)  # Rotate season labels for readability

    # Display plot in Streamlit
    st.pyplot(fig)

    # Download button to save the plot as a PNG
    st.download_button(
        label="Download Plot as PNG",
        data=fig_to_bytes(fig),
        file_name=f"{selected_player}_PPG_over_seasons.png",
        mime="image/png"
    )