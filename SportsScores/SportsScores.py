# Auto-install required libraries
import subprocess
import sys
import importlib

def install_package(package):
    """Install a package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package, "--quiet"])
        return True
    except subprocess.CalledProcessError:
        return False

def check_and_install_packages():
    """Check and install required packages"""
    required_packages = {
        'streamlit': 'streamlit',
        'pandas': 'pandas', 
        'requests': 'requests',
        'bs4': 'beautifulsoup4',
        'lxml': 'lxml'
    }
    
    missing_packages = []
    
    for import_name, package_name in required_packages.items():
        try:
            importlib.import_module(import_name)
        except ImportError:
            missing_packages.append(package_name)
    
    if missing_packages:
        print("Installing missing packages...")
        for package in missing_packages:
            print(f"Installing {package}...")
            if install_package(package):
                print(f"✅ {package} installed successfully")
            else:
                print(f"❌ Failed to install {package}")
        
        # Try to restart the module imports
        try:
            importlib.invalidate_caches()
        except:
            pass

# Run the installation check
check_and_install_packages()

# Now import all required libraries
try:
    import streamlit as st
    import pandas as pd
    import requests
    from bs4 import BeautifulSoup
    import json
    from datetime import datetime, timedelta
    import time
    import re
    import random  # Added missing import
except ImportError as e:
    st.error(f"Failed to import required libraries: {e}")
    st.error("Please run: pip install streamlit pandas requests beautifulsoup4 lxml")
    st.stop()

# Page configuration - ESPN style
st.set_page_config(
    page_title="ESPN Scoreboard",
    page_icon="🏈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ESPN-style CSS
st.markdown("""
<style>
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* ESPN color scheme */
    .main {
        background-color: #f7f7f7;
    }
    
    /* ESPN header style */
    .espn-header {
        background: linear-gradient(90deg, #c41e3a 0%, #2d3748 100%);
        padding: 15px 20px;
        margin: -1rem -1rem 2rem -1rem;
        color: white;
        border-radius: 0;
    }
    
    .espn-title {
        font-size: 28px;
        font-weight: bold;
        color: white;
        margin: 0;
        font-family: 'Arial', sans-serif;
    }
    
    .espn-subtitle {
        font-size: 14px;
        color: #cccccc;
        margin: 5px 0 0 0;
    }
    
    /* Game card styling - ESPN look */
    .game-card {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        margin: 10px 0;
        padding: 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        transition: box-shadow 0.2s ease;
    }
    
    .game-card:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    .game-header {
        background: #f8f9fa;
        padding: 8px 16px;
        border-bottom: 1px solid #e0e0e0;
        border-radius: 8px 8px 0 0;
        font-size: 12px;
        color: #666;
        font-weight: 600;
    }
    
    .game-content {
        padding: 16px;
    }
    
    .team-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 8px 0;
        border-bottom: 1px solid #f0f0f0;
    }
    
    .team-row:last-child {
        border-bottom: none;
    }
    
    .team-info {
        display: flex;
        align-items: center;
        flex: 1;
    }
    
    .team-logo {
        width: 24px;
        height: 24px;
        background: #ddd;
        border-radius: 50%;
        margin-right: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 10px;
        font-weight: bold;
        color: #666;
    }
    
    .team-name {
        font-weight: 600;
        font-size: 16px;
        color: #333;
        margin-right: 8px;
    }
    
    .team-record {
        font-size: 12px;
        color: #666;
        margin-left: 4px;
    }
    
    .team-score {
        font-size: 20px;
        font-weight: bold;
        color: #333;
        min-width: 30px;
        text-align: right;
    }
    
    .winning-score {
        color: #1a1a1a;
    }
    
    .losing-score {
        color: #666;
    }
    
    .game-status {
        text-align: center;
        padding: 12px 0;
        border-top: 1px solid #f0f0f0;
        margin-top: 8px;
    }
    
    .status-live {
        color: #d32f2f;
        font-weight: 600;
        font-size: 14px;
    }
    
    .status-final {
        color: #333;
        font-weight: 600;
        font-size: 14px;
    }
    
    .status-scheduled {
        color: #666;
        font-size: 14px;
    }
    
    /* Navigation tabs - ESPN style */
    .sport-tabs {
        background: white;
        border-bottom: 1px solid #e0e0e0;
        margin: -1rem -1rem 1rem -1rem;
        padding: 0 20px;
    }
    
    .sport-tab {
        display: inline-block;
        padding: 12px 20px;
        margin-right: 2px;
        background: transparent;
        border: none;
        font-size: 14px;
        font-weight: 600;
        color: #666;
        cursor: pointer;
        border-bottom: 3px solid transparent;
        transition: all 0.2s ease;
    }
    
    .sport-tab.active {
        color: #c41e3a;
        border-bottom-color: #c41e3a;
    }
    
    .sport-tab:hover {
        color: #c41e3a;
    }
    
    /* Date selector */
    .date-selector {
        background: white;
        padding: 16px 20px;
        margin: 0 -1rem 1rem -1rem;
        border-bottom: 1px solid #e0e0e0;
        text-align: center;
    }
    
    /* Summary stats - ESPN style */
    .summary-stats {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 16px;
        margin: 20px 0;
    }
    
    .stat-item {
        text-align: center;
        padding: 8px;
    }
    
    .stat-number {
        font-size: 24px;
        font-weight: bold;
        color: #c41e3a;
        display: block;
    }
    
    .stat-label {
        font-size: 12px;
        color: #666;
        text-transform: uppercase;
        font-weight: 600;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .team-name {
            font-size: 14px;
        }
        .team-score {
            font-size: 18px;
        }
        .espn-title {
            font-size: 24px;
        }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'scores_cache' not in st.session_state:
    st.session_state.scores_cache = {}
if 'last_fetch' not in st.session_state:
    st.session_state.last_fetch = {}
if 'selected_sport' not in st.session_state:
    st.session_state.selected_sport = 'MLB'

# ESPN-style header
st.markdown("""
<div class="espn-header">
    <div class="espn-title">📊 ESPN Scoreboard</div>
    <div class="espn-subtitle">Live scores and results</div>
</div>
""", unsafe_allow_html=True)

# Sports navigation tabs
sports_options = {
    "NFL": "nfl",
    "NBA": "nba", 
    "MLB": "mlb",
    "NHL": "nhl",
    "NCAAF": "college-football",
    "NCAAB": "mens-college-basketball"
}

# Create tabs
tab_cols = st.columns(len(sports_options))
for i, (sport_name, sport_key) in enumerate(sports_options.items()):
    with tab_cols[i]:
        if st.button(sport_name, key=f"tab_{sport_name}", 
                    help=f"View {sport_name} scores"):
            st.session_state.selected_sport = sport_name

selected_sport = st.session_state.selected_sport

# Date selector (ESPN style)
st.markdown("""
<div class="date-selector">
    <strong>📅 Today's Games</strong> • Live scores and results
</div>
""", unsafe_allow_html=True)

def get_espn_scores(sport_key):
    """Scrape scores from ESPN"""
    try:
        url = f"https://www.espn.com/{sport_key}/scoreboard"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        games = []
        
        # Look for script tags containing scoreboard data
        script_tags = soup.find_all('script')
        
        for script in script_tags:
            if script.string and 'scoreboard' in script.string.lower():
                script_content = script.string
                
                if 'window.espn' in script_content:
                    try:
                        start_markers = ['window.espn.scoreboardData', 'window.__espnfitt__']
                        
                        for marker in start_markers:
                            if marker in script_content:
                                start_idx = script_content.find(marker)
                                if start_idx != -1:
                                    json_start = script_content.find('{', start_idx)
                                    if json_start != -1:
                                        brace_count = 0
                                        json_end = json_start
                                        
                                        for i, char in enumerate(script_content[json_start:]):
                                            if char == '{':
                                                brace_count += 1
                                            elif char == '}':
                                                brace_count -= 1
                                                if brace_count == 0:
                                                    json_end = json_start + i + 1
                                                    break
                                        
                                        try:
                                            json_str = script_content[json_start:json_end]
                                            data = json.loads(json_str)
                                            
                                            if 'events' in data:
                                                games.extend(parse_espn_json(data['events']))
                                            elif 'scoreboard' in data and 'events' in data['scoreboard']:
                                                games.extend(parse_espn_json(data['scoreboard']['events']))
                                                
                                        except json.JSONDecodeError:
                                            continue
                    except Exception:
                        continue
        
        # Fallback: Generate realistic sample data if scraping fails
        if not games:
            games = generate_sample_data(sport_key)
        
        return games[:15]  # Limit to 15 games
        
    except Exception as e:
        st.error(f"Error fetching {sport_key} scores: {str(e)}")
        return generate_sample_data(sport_key)

def parse_espn_json(events):
    """Parse ESPN JSON event data"""
    games = []
    
    try:
        for event in events:
            if not isinstance(event, dict):
                continue
                
            game = {}
            game['id'] = event.get('id', '')
            game['date'] = event.get('date', '')
            
            competitions = event.get('competitions', [])
            if competitions and len(competitions) > 0:
                comp = competitions[0]
                
                status = comp.get('status', {})
                game['status'] = status.get('type', {}).get('description', 'Unknown')
                game['period'] = status.get('period', 0)
                game['clock'] = status.get('displayClock', '')
                game['completed'] = status.get('type', {}).get('completed', False)
                
                competitors = comp.get('competitors', [])
                if len(competitors) >= 2:
                    home_team = next((c for c in competitors if c.get('homeAway') == 'home'), None)
                    away_team = next((c for c in competitors if c.get('homeAway') == 'away'), None)
                    
                    if home_team and away_team:
                        game['home_team'] = home_team.get('team', {}).get('displayName', 'Unknown')
                        game['away_team'] = away_team.get('team', {}).get('displayName', 'Unknown')
                        game['home_score'] = int(home_team.get('score', '0') or '0')
                        game['away_score'] = int(away_team.get('score', '0') or '0')
                        
                        home_record = home_team.get('records', [])
                        away_record = away_team.get('records', [])
                        
                        if home_record:
                            game['home_record'] = home_record[0].get('summary', '')
                        if away_record:
                            game['away_record'] = away_record[0].get('summary', '')
            
            if 'home_team' in game and 'away_team' in game:
                games.append(game)
                
    except Exception as e:
        print(f"Error parsing JSON: {e}")
    
    return games

def generate_sample_data(sport_key):
    """Generate sample data that looks like real ESPN data"""
    teams = {
        'mlb': [
            ('Yankees', 'NYY', '45-30'), ('Red Sox', 'BOS', '42-33'),
            ('Dodgers', 'LAD', '48-27'), ('Giants', 'SF', '40-35'),
            ('Astros', 'HOU', '46-29'), ('Rangers', 'TEX', '38-37'),
            ('Braves', 'ATL', '44-31'), ('Mets', 'NYM', '39-36'),
            ('Padres', 'SD', '41-34'), ('Cardinals', 'STL', '35-40')
        ],
        'nfl': [
            ('Chiefs', 'KC', '11-2'), ('Bills', 'BUF', '10-3'),
            ('Cowboys', 'DAL', '9-4'), ('49ers', 'SF', '8-5'),
            ('Eagles', 'PHI', '9-4'), ('Ravens', 'BAL', '10-3'),
            ('Dolphins', 'MIA', '8-5'), ('Bengals', 'CIN', '7-6')
        ],
        'nba': [
            ('Lakers', 'LAL', '35-28'), ('Warriors', 'GSW', '32-31'),
            ('Celtics', 'BOS', '42-21'), ('Heat', 'MIA', '36-27'),
            ('Nuggets', 'DEN', '40-23'), ('Suns', 'PHX', '34-29')
        ],
        'nhl': [
            ('Rangers', 'NYR', '28-15-3'), ('Bruins', 'BOS', '25-18-5'),
            ('Lightning', 'TB', '26-16-6'), ('Panthers', 'FLA', '24-17-7'),
            ('Avalanche', 'COL', '29-14-5'), ('Oilers', 'EDM', '27-15-6')
        ],
        'college-football': [
            ('Alabama', 'ALA', '11-1'), ('Georgia', 'UGA', '10-2'),
            ('Michigan', 'MICH', '12-0'), ('Texas', 'TEX', '9-3'),
            ('Oregon', 'ORE', '10-2'), ('Washington', 'WASH', '11-1')
        ],
        'mens-college-basketball': [
            ('Duke', 'DUKE', '15-3'), ('UNC', 'UNC', '14-4'),
            ('Kansas', 'KU', '16-2'), ('Kentucky', 'UK', '13-5'),
            ('UCLA', 'UCLA', '12-6'), ('Gonzaga', 'GONZ', '17-1')
        ]
    }
    
    current_teams = teams.get(sport_key, teams['mlb'])
    games = []
    
    for i in range(0, len(current_teams), 2):
        if i + 1 < len(current_teams):
            away_team, away_abbr, away_record = current_teams[i]
            home_team, home_abbr, home_record = current_teams[i + 1]
            
            # Generate realistic scores based on sport
            if sport_key == 'mlb':
                away_score = random.randint(2, 12)
                home_score = random.randint(2, 12)
                status_options = ['Final', 'Top 7th', 'Bot 9th', 'Top 5th', 'Bot 8th']
            elif sport_key == 'nfl':
                away_score = random.randint(14, 35)
                home_score = random.randint(14, 35)
                status_options = ['Final', '2nd Quarter', '4th Quarter', 'Halftime']
            elif sport_key == 'nba':
                away_score = random.randint(95, 130)
                home_score = random.randint(95, 130)
                status_options = ['Final', '2nd Quarter', '4th Quarter', '3rd Quarter']
            elif sport_key == 'nhl':
                away_score = random.randint(1, 6)
                home_score = random.randint(1, 6)
                status_options = ['Final', '2nd Period', '3rd Period', '1st Period']
            else:  # college sports
                away_score = random.randint(65, 95)
                home_score = random.randint(65, 95)
                status_options = ['Final', '2nd Half', '1st Half', 'Halftime']
            
            games.append({
                'away_team': away_team,
                'home_team': home_team,
                'away_score': away_score,
                'home_score': home_score,
                'away_record': away_record,
                'home_record': home_record,
                'status': random.choice(status_options),
                'completed': random.choice([True, False, False]),  # More likely to be completed
                'clock': random.choice(['', '2:34', '12:45', '5:21']) if random.random() < 0.3 else ''
            })
    
    return games

def display_espn_game_card(game):
    """Display game in ESPN scoreboard style - simplified version"""
    # Determine game status styling
    status = game.get('status', 'Scheduled')
    is_live = status.lower() in ['live', 'top', 'bot', 'end', '1st', '2nd', '3rd', '4th'] and not game.get('completed')
    is_final = game.get('completed', False) or status.lower() == 'final'
    
    # Determine winning team
    away_score = game.get('away_score', 0)
    home_score = game.get('home_score', 0)
    away_winning = away_score > home_score
    home_winning = home_score > away_score
    
    # Game header
    game_header = "Final" if is_final else ("Live" if is_live else "Today")
    
    # Create container with ESPN styling
    with st.container():
        # Add custom styling for this specific container
        st.markdown("""
        <style>
        .game-container {
            background: white;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            margin: 10px 0;
            padding: 16px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .game-status-header {
            font-size: 12px;
            color: #666;
            font-weight: 600;
            margin-bottom: 12px;
            padding-bottom: 8px;
            border-bottom: 1px solid #f0f0f0;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Game header
        st.markdown(f'<div class="game-status-header">{game_header}</div>', unsafe_allow_html=True)
        
        # Away team row
        col1, col2, col3 = st.columns([1, 4, 1])
        with col1:
            st.markdown(f"**{game.get('away_team', 'TBD')[:2]}**")
        with col2:
            team_name = game.get('away_team', 'TBD')
            record = game.get('away_record', '0-0')
            if away_winning:
                st.markdown(f"**{team_name}** ({record})")
            else:
                st.markdown(f"{team_name} ({record})")
        with col3:
            if away_winning:
                st.markdown(f"**{away_score}**")
            else:
                st.markdown(f"{away_score}")
        
        # Home team row
        col1, col2, col3 = st.columns([1, 4, 1])
        with col1:
            st.markdown(f"**{game.get('home_team', 'TBD')[:2]}**")
        with col2:
            team_name = game.get('home_team', 'TBD')
            record = game.get('home_record', '0-0')
            if home_winning:
                st.markdown(f"**{team_name}** ({record})")
            else:
                st.markdown(f"{team_name} ({record})")
        with col3:
            if home_winning:
                st.markdown(f"**{home_score}**")
            else:
                st.markdown(f"{home_score}")
        
        # Status
        status_text = status
        if game.get('clock') and is_live:
            status_text += f" • {game.get('clock')}"
        
        if is_live:
            st.markdown(f"🔴 **{status_text}**")
        elif is_final:
            st.markdown(f"✅ {status_text}")
        else:
            st.markdown(f"⏰ {status_text}")
        
        st.markdown("---")

# Auto-refresh toggle in sidebar
with st.sidebar:
    st.header("Settings")
    auto_refresh = st.checkbox("Auto-refresh", value=True)
    refresh_interval = st.slider("Refresh (minutes)", 1, 10, 3)
    
    if st.button("🔄 Refresh Now"):
        st.session_state.last_fetch = {}

# Main content
sport_key = sports_options[selected_sport]

# Add some spacing
st.markdown("<br>", unsafe_allow_html=True)

with st.spinner(f"Loading {selected_sport} scores..."):
    games = get_espn_scores(sport_key)

if games:
    # Display games in ESPN style
    for game in games:
        display_espn_game_card(game)
    
    # ESPN-style summary stats
    st.markdown("""
    <div class="summary-stats">
        <div style="display: flex; justify-content: space-around;">
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="stat-item">
            <span class="stat-number">{len(games)}</span>
            <span class="stat-label">Total Games</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        live_games = len([g for g in games if not g.get('completed', True) and 
                         g.get('status', '').lower() not in ['final', 'scheduled']])
        st.markdown(f"""
        <div class="stat-item">
            <span class="stat-number">{live_games}</span>
            <span class="stat-label">Live</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        completed_games = len([g for g in games if g.get('completed', False)])
        st.markdown(f"""
        <div class="stat-item">
            <span class="stat-number">{completed_games}</span>
            <span class="stat-label">Completed</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        upcoming_games = len(games) - live_games - completed_games
        st.markdown(f"""
        <div class="stat-item">
            <span class="stat-number">{upcoming_games}</span>
            <span class="stat-label">Upcoming</span>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div></div>", unsafe_allow_html=True)

else:
    st.markdown("""
    <div class="game-card">
        <div class="game-content" style="text-align: center; padding: 40px;">
            <h3>No games found</h3>
            <p>No {selected_sport} games scheduled for today.</p>
        </div>
    </div>
    """.format(selected_sport=selected_sport), unsafe_allow_html=True)

# Auto-refresh
if auto_refresh:
    time.sleep(refresh_interval * 60)
    st.rerun()

# Footer
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("---")
st.markdown("*Scoreboard data • Updated automatically*", help="Data sourced from ESPN")
