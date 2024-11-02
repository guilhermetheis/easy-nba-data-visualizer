import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from nba_api.stats.static import players
from nba_api.stats.endpoints import playercareerstats

# Title and description
st.title("NBA Player Stats Viewer")
st.write("Select players and statistics to generate plots!")

# Select player
all_players = players.get_players()
player_names = [player['full_name'] for player in all_players]
selected_player = st.selectbox("Choose a player", player_names)

# Fetch and display player stats
if selected_player:
    player_id = next(player['id'] for player in all_players if player['full_name'] == selected_player)
    career = playercareerstats.PlayerCareerStats(player_id=player_id).get_data_frames()[0]
    stat_option = st.selectbox("Select Stat", career.columns[5:])  # Example stats columns

    # Plotting
    fig, ax = plt.subplots()
    ax.plot(career['SEASON_ID'], career[stat_option])
    ax.set_title(f"{selected_player} - {stat_option} Over Seasons")
    st.pyplot(fig)
