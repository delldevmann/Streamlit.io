# streamlined_app.py
# ESPN-Style Streamlit Scoreboard (Refactored)

import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta
import random
import re

# ----------------------------
# Session State Initialization
# ----------------------------
for key, default in {
    "scores_cache": {},
    "last_fetch": {},
    "selected_sport": "MLB"
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ----------------------------
# Page Config
# ----------------------------
st.set_page_config(
    page_title="ESPN Scoreboard",
    page_icon="\ud83c\udfc8",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ----------------------------
# ESPN Header
# ----------------------------
st.markdown("""
<style>
#MainMenu, footer, header {visibility: hidden;}
.espn-header {
    background: linear-gradient(90deg, #c41e3a 0%, #2d3748 100%);
    padding: 15px 20px;
    margin: -1rem -1rem 2rem -1rem;
    color: white;
}
.espn-title { font-size: 28px; font-weight: bold; color: white; }
.espn-subtitle { font-size: 14px; color: #cccccc; }
</style>
<div class="espn-header">
    <div class="espn-title">\ud83d\udcca ESPN Scoreboard</div>
    <div class="espn-subtitle">Live scores and results</div>
</div>
""", unsafe_allow_html=True)

# ----------------------------
# Sport Tabs
# ----------------------------
sports_options = {
    "NFL": "nfl",
    "NBA": "nba",
    "MLB": "mlb",
    "NHL": "nhl",
    "NCAAF": "college-football",
    "NCAAB": "mens-college-basketball"
}
tabs = st.columns(len(sports_options))
for i, sport in enumerate(sports_options):
    if tabs[i].button(sport):
        st.session_state.selected_sport = sport
selected_sport = st.session_state.selected_sport
sport_key = sports_options[selected_sport]

st.markdown("<br><strong>\ud83d\uddd3\ufe0f Today's Games</strong>", unsafe_allow_html=True)

# ----------------------------
# ESPN Data Fetcher
# ----------------------------
def get_espn_scores(sport_key):
    url = f"https://www.espn.com/{sport_key}/scoreboard"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        soup = BeautifulSoup(requests.get(url, headers=headers).content, 'html.parser')
        script = next((s.string for s in soup.find_all('script') if s.string and 'scoreboard' in s.string.lower()), None)
        if not script: return []
        json_data = extract_json_from_script(script, 'window.espn.scoreboardData')
        if json_data and 'events' in json_data:
            return parse_espn_json(json_data['events'])
    except Exception as e:
        st.error(f"Error fetching scores: {e}")
    return generate_sample_data(sport_key)

def extract_json_from_script(script_content, marker):
    try:
        match = re.search(rf"{marker}\s*=\s*({{.*?}});", script_content, re.DOTALL)
        return json.loads(match.group(1)) if match else None
    except json.JSONDecodeError:
        return None

def parse_espn_json(events):
    results = []
    for ev in events:
        comp = ev.get('competitions', [{}])[0]
        teams = comp.get('competitors', [])
        if len(teams) < 2: continue
        home = next((t for t in teams if t['homeAway'] == 'home'), {})
        away = next((t for t in teams if t['homeAway'] == 'away'), {})
        results.append({
            'home_team': home.get('team', {}).get('displayName', 'TBD'),
            'away_team': away.get('team', {}).get('displayName', 'TBD'),
            'home_score': int(home.get('score', 0)),
            'away_score': int(away.get('score', 0)),
            'home_record': home.get('records', [{}])[0].get('summary', ''),
            'away_record': away.get('records', [{}])[0].get('summary', ''),
            'status': comp.get('status', {}).get('type', {}).get('description', 'Unknown'),
            'clock': comp.get('status', {}).get('displayClock', ''),
            'completed': comp.get('status', {}).get('type', {}).get('completed', False)
        })
    return results

def generate_sample_data(sport_key):
    # For brevity, reuse your function or fallback sample here
    return [{
        'home_team': 'Team A', 'away_team': 'Team B', 'home_score': 3, 'away_score': 4,
        'home_record': '10-5', 'away_record': '8-7', 'status': 'Final',
        'clock': '', 'completed': True
    }]

# ----------------------------
# Game Card Renderer
# ----------------------------
def display_game_card(g):
    with st.container():
        st.markdown(f"**{g['away_team']}** ({g['away_record']}) {g['away_score']}")
        st.markdown(f"**{g['home_team']}** ({g['home_record']}) {g['home_score']}")
        status_line = f"\ud83d\udd34 {g['status']} • {g['clock']}" if not g['completed'] else f"\u2705 {g['status']}"
        st.markdown(status_line)
        st.markdown("---")

# ----------------------------
# Sidebar Settings
# ----------------------------
with st.sidebar:
    st.header("Settings")
    auto_refresh = st.checkbox("Auto-refresh", value=True)
    refresh_interval = st.slider("Refresh interval (min)", 1, 10, 3)
    if st.button("Manual Refresh"):
        st.session_state.last_fetch[sport_key] = None

# ----------------------------
# Main App Flow
# ----------------------------
if st.session_state.last_fetch.get(sport_key) is None or \
   (datetime.utcnow() - st.session_state.last_fetch.get(sport_key, datetime.min)) > timedelta(minutes=3):
    with st.spinner("Fetching scores..."):
        games = get_espn_scores(sport_key)
        st.session_state.scores_cache[sport_key] = games
        st.session_state.last_fetch[sport_key] = datetime.utcnow()
else:
    games = st.session_state.scores_cache.get(sport_key, [])

# Display Cards
if games:
    for game in games:
        display_game_card(game)
    st.success(f"Loaded {len(games)} games for {selected_sport}.")
else:
    st.warning("No games available.")

# Auto-refresh
if auto_refresh:
    st.experimental_rerun()
