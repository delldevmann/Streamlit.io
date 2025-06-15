# Auto-install required libraries
import subprocess
import sys

def install_package(package):
    """Install a package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        return False

# Required packages
required_packages = ['streamlit', 'pandas']

# Check and install packages
for package in required_packages:
    try:
        __import__(package)
    except ImportError:
        print(f"Installing {package}...")
        if install_package(package):
            print(f"✅ {package} installed successfully")
        else:
            print(f"❌ Failed to install {package}")

# Now import all required libraries
import streamlit as st
import pandas as pd
import random
from datetime import datetime, timedelta
import time

# Page configuration
st.set_page_config(
    page_title="Sports Scores Dashboard",
    page_icon="⚽",
    layout="wide"
)

# Initialize session state for dynamic scores
if 'game_data' not in st.session_state:
    st.session_state.game_data = {}
if 'last_update' not in st.session_state:
    st.session_state.last_update = datetime.now()

# Title and description
st.title("🏆 Sports Scores Dashboard")
st.markdown("Live sports scores simulator - No API required!")

# Sidebar for options
st.sidebar.header("Settings")

# Sports data structure
TEAMS = {
    "NFL": [
        "Chiefs", "Bills", "Cowboys", "Patriots", "Packers", "49ers", 
        "Steelers", "Ravens", "Seahawks", "Saints", "Rams", "Broncos"
    ],
    "NBA": [
        "Lakers", "Warriors", "Celtics", "Heat", "Nets", "Bucks",
        "Clippers", "Suns", "76ers", "Nuggets", "Mavericks", "Bulls"
    ],
    "MLB": [
        "Yankees", "Dodgers", "Red Sox", "Astros", "Braves", "Cardinals",
        "Giants", "Cubs", "Mets", "Phillies", "Padres", "Blue Jays"
    ],
    "NHL": [
        "Rangers", "Bruins", "Lightning", "Avalanche", "Oilers", "Panthers",
        "Maple Leafs", "Penguins", "Kings", "Capitals", "Stars", "Devils"
    ],
    "Premier League": [
        "Manchester City", "Arsenal", "Liverpool", "Chelsea", "Manchester United", "Tottenham",
        "Newcastle", "Brighton", "Aston Villa", "West Ham", "Crystal Palace", "Fulham"
    ],
    "La Liga": [
        "Real Madrid", "Barcelona", "Atletico Madrid", "Real Sociedad", "Sevilla", "Villarreal",
        "Real Betis", "Valencia", "Athletic Bilbao", "Osasuna", "Girona", "Las Palmas"
    ]
}

SCORE_RANGES = {
    "NFL": (14, 35),
    "NBA": (95, 130),
    "MLB": (2, 12),
    "NHL": (1, 7),
    "Premier League": (0, 4),
    "La Liga": (0, 4)
}

# Sports selection
selected_sport = st.sidebar.selectbox("Select Sport/League", list(TEAMS.keys()))

# Time range selection
time_range = st.sidebar.selectbox(
    "Time Range",
    ["Live Games", "Recent Games", "Today's Games"]
)

# Auto-update settings
auto_update = st.sidebar.checkbox("Auto-update Live Scores", value=True)
update_interval = st.sidebar.slider("Update Interval (seconds)", 5, 30, 10)

# Manual refresh
if st.sidebar.button("🔄 Refresh Scores"):
    st.session_state.last_update = datetime.now() - timedelta(seconds=update_interval)

def generate_game_data(sport, num_games=8):
    """Generate realistic game data"""
    teams = TEAMS[sport]
    score_range = SCORE_RANGES[sport]
    games = []
    
    now = datetime.now()
    
    for i in range(num_games):
        # Random team matchup
        home_team = random.choice(teams)
        away_team = random.choice([t for t in teams if t != home_team])
        
        game_id = f"{sport}_{i}"
        
        # Generate game time based on time range
        if time_range == "Live Games":
            # Games happening now
            start_time = now - timedelta(minutes=random.randint(15, 90))
            is_live = True
            is_completed = False
        elif time_range == "Recent Games":
            # Games from last few days
            start_time = now - timedelta(days=random.randint(1, 3), hours=random.randint(0, 23))
            is_live = False
            is_completed = True
        else:  # Today's Games
            # Mix of completed, live, and upcoming today
            hours_offset = random.randint(-12, 12)
            start_time = now.replace(hour=max(0, min(23, 12 + hours_offset)), minute=0)
            if hours_offset < -2:
                is_completed = True
                is_live = False
            elif hours_offset < 2:
                is_live = True
                is_completed = False
            else:
                is_live = False
                is_completed = False
        
        # Generate scores
        if is_completed or is_live:
            home_score = random.randint(*score_range)
            away_score = random.randint(*score_range)
            
            # For live games, add some randomness to scores over time
            if is_live and game_id in st.session_state.game_data:
                old_game = st.session_state.game_data[game_id]
                # Small chance to update score
                if random.random() < 0.3:
                    home_score = max(old_game['home_score'], old_game['home_score'] + random.randint(0, 1))
                    away_score = max(old_game['away_score'], old_game['away_score'] + random.randint(0, 1))
                else:
                    home_score = old_game['home_score']
                    away_score = old_game['away_score']
        else:
            home_score = None
            away_score = None
        
        # Game status
        if is_completed:
            status = "Final"
            period = "Final"
        elif is_live:
            periods = {
                "NFL": ["Q1", "Q2", "Q3", "Q4", "OT"],
                "NBA": ["Q1", "Q2", "Q3", "Q4", "OT"],
                "MLB": [f"T{i}" if i <= 9 else f"B{i-9}" for i in range(1, 19)],
                "NHL": ["1st", "2nd", "3rd", "OT", "SO"],
                "Premier League": ["1st Half", "2nd Half", "ET"],
                "La Liga": ["1st Half", "2nd Half", "ET"]
            }
            period = random.choice(periods[sport][:4])  # Most common periods
            status = f"Live - {period}"
        else:
            status = start_time.strftime("%I:%M %p")
            period = "Upcoming"
        
        game = {
            'id': game_id,
            'home_team': home_team,
            'away_team': away_team,
            'home_score': home_score,
            'away_score': away_score,
            'start_time': start_time,
            'status': status,
            'period': period,
            'is_live': is_live,
            'is_completed': is_completed
        }
        
        games.append(game)
        st.session_state.game_data[game_id] = game
    
    return games

def display_game_card(game):
    """Display a game in a card format"""
    # Determine card styling based on game status
    if game['is_live']:
        border_color = "#ff4444"  # Red for live
        status_emoji = "🔴"
    elif game['is_completed']:
        border_color = "#44ff44"  # Green for completed
        status_emoji = "✅"
    else:
        border_color = "#4444ff"  # Blue for upcoming
        status_emoji = "⏰"
    
    # Create the card container
    with st.container():
        st.markdown(f"""
        <div style="
            border: 2px solid {border_color}; 
            border-radius: 10px; 
            padding: 15px; 
            margin: 10px 0;
            background-color: #f8f9fa;
        ">
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([3, 2, 3])
        
        with col1:
            st.markdown(f"### {game['away_team']}")
            if game['away_score'] is not None:
                st.markdown(f"**Score: {game['away_score']}**")
        
        with col2:
            st.markdown(f"<h2 style='text-align: center;'>VS</h2>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align: center;'>{status_emoji} {game['status']}</p>", unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"### {game['home_team']}")
            if game['home_score'] is not None:
                st.markdown(f"**Score: {game['home_score']}**")
        
        # Game time
        time_str = game['start_time'].strftime("%m/%d %I:%M %p")
        st.markdown(f"<p style='text-align: center; color: #666; font-size: 0.9em;'>Game Time: {time_str}</p>", 
                   unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

# Auto-update logic
current_time = datetime.now()
if auto_update and (current_time - st.session_state.last_update).seconds >= update_interval:
    st.session_state.last_update = current_time
    st.rerun()

# Main content
st.subheader(f"{selected_sport} - {time_range}")

# Generate and display games
games = generate_game_data(selected_sport)

# Filter games based on selection
if time_range == "Live Games":
    filtered_games = [g for g in games if g['is_live']]
elif time_range == "Recent Games":
    filtered_games = [g for g in games if g['is_completed']]
else:  # Today's Games
    filtered_games = games

# Sort games by start time
filtered_games.sort(key=lambda x: x['start_time'], reverse=True)

if filtered_games:
    # Display games
    for game in filtered_games:
        display_game_card(game)
    
    # Display summary statistics
    st.markdown("---")
    st.subheader("📊 Game Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_games = len(filtered_games)
        st.metric("Total Games", total_games)
    
    with col2:
        live_games = len([g for g in filtered_games if g['is_live']])
        st.metric("🔴 Live Games", live_games)
    
    with col3:
        completed_games = len([g for g in filtered_games if g['is_completed']])
        st.metric("✅ Completed", completed_games)
    
    with col4:
        upcoming_games = len([g for g in filtered_games if not g['is_live'] and not g['is_completed']])
        st.metric("⏰ Upcoming", upcoming_games)
    
    # Show high-scoring games
    if time_range in ["Recent Games", "Live Games"]:
        high_scoring = [g for g in filtered_games if g['home_score'] and g['away_score'] and 
                       (g['home_score'] + g['away_score']) > (sum(SCORE_RANGES[selected_sport])/2 * 1.5)]
        
        if high_scoring:
            st.subheader("🔥 High-Scoring Games")
            for game in high_scoring[:3]:
                total_score = game['home_score'] + game['away_score']
                st.write(f"**{game['away_team']} {game['away_score']} - {game['home_score']} {game['home_team']}** (Total: {total_score})")

else:
    st.warning(f"No {time_range.lower()} available for {selected_sport}")

# Last update info
if auto_update:
    st.markdown(f"*Last updated: {st.session_state.last_update.strftime('%I:%M:%S %p')} - Auto-updating every {update_interval} seconds*")
else:
    st.markdown(f"*Last updated: {st.session_state.last_update.strftime('%I:%M:%S %p')} - Auto-update disabled*")

# Instructions
with st.sidebar.expander("ℹ️ How to Use"):
    st.markdown("""
    **This app simulates live sports scores!**
    
    🔴 **Live Games**: Games happening now with updating scores
    
    ✅ **Recent Games**: Completed games from the last few days
    
    ⏰ **Today's Games**: Mix of completed, live, and upcoming games for today
    
    **Features:**
    - Scores update automatically for live games
    - Realistic score ranges for each sport  
    - Color-coded game status
    - Summary statistics
    - High-scoring game highlights
    """)
