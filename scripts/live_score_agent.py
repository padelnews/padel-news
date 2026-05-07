#!/usr/bin/env python3
"""
Padel News - Live Score Agent
=============================
Scrapes official Premier Padel results and draws.
Updates tournament data every 10 minutes during live tournaments.

Sources:
- https://www.premierpadel.com/ (official)
- https://padel.live/ (alternative)
"""

import json
import requests
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup
import re

PADEL_DIR = Path("/Users/cristian/Sites/padel_news")
STATE_FILE = PADEL_DIR / "scripts" / "tournament_state.json"
LOG_FILE = PADEL_DIR / "scripts" / "live_score_agent.log"


def log(msg: str):
    """Log with timestamp."""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")
    print(line)


def load_state() -> dict:
    """Load tournament state."""
    try:
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        log(f"ERROR loading state: {e}")
        return {}


def save_state(state: dict):
    """Save tournament state."""
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
    log("State saved")


def fetch_premier_padel_draw(tournament_id: str) -> dict:
    """
    Fetch draw/results from Premier Padel official site.
    
    Returns dict with:
    - rounds: list of rounds with matches
    - updated: timestamp
    """
    log(f"Fetching draw for tournament: {tournament_id}")
    
    # Official Premier Padel API endpoint (reverse-engineered)
    # This is the API that powers their website
    api_url = f"https://www.premierpadel.com/api/tournaments/{tournament_id}/draw"
    
    try:
        # Try official API first
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'application/json',
        }
        
        response = requests.get(api_url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            log(f"✅ Fetched from official API: {len(data.get('matches', []))} matches")
            return parse_premier_padel_api(data)
        else:
            log(f"⚠️ API returned {response.status_code}, trying fallback...")
            
    except Exception as e:
        log(f"⚠️ API fetch failed: {e}")
    
    # Fallback: scrape HTML
    return scrape_premier_padel_html(tournament_id)


def parse_premier_padel_api(data: dict) -> dict:
    """Parse Premier Padel API response."""
    rounds = []
    
    # Map round names
    round_map = {
        "Round of 32": "round_of_32",
        "Round of 16": "round_of_16",
        "Quarter-finals": "quarters",
        "Semi-finals": "semis",
        "Final": "final"
    }
    
    matches_by_round = {}
    
    for match in data.get('matches', []):
        round_name = match.get('round', 'Unknown')
        round_key = round_map.get(round_name, round_name.lower().replace(' ', '_'))
        
        if round_key not in matches_by_round:
            matches_by_round[round_key] = []
        
        # Extract teams and scores
        team1 = match.get('team1', {})
        team2 = match.get('team2', {})
        score = match.get('score', '')
        status = match.get('status', 'scheduled')  # scheduled, live, finished
        
        match_data = {
            'round': round_name,
            'team1': {
                'players': team1.get('players', []),
                'country': team1.get('country', ''),
                'seed': team1.get('seed')
            },
            'team2': {
                'players': team2.get('players', []),
                'country': team2.get('country', ''),
                'seed': team2.get('seed')
            },
            'score': score,
            'status': status,
            'court': match.get('court', ''),
            'time': match.get('time', '')
        }
        
        matches_by_round[round_key].append(match_data)
    
    return {
        'rounds': matches_by_round,
        'updated': datetime.now().isoformat(),
        'source': 'premier_padel_api'
    }


def scrape_premier_padel_html(tournament_id: str) -> dict:
    """Fallback: scrape Premier Padel HTML page."""
    log(f"Scraping HTML for tournament: {tournament_id}")
    
    url = f"https://www.premierpadel.com/tournaments/{tournament_id}/draw"
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Parse the draw table/bracket
        # This is a simplified scraper - real implementation would need
        # to handle the actual HTML structure
        matches = []
        
        # Look for match elements (this is pseudo-code, needs real selectors)
        match_elements = soup.select('.match-card, .draw-match')
        
        for match_el in match_elements:
            # Extract teams, score, round, etc.
            # Implementation depends on actual HTML structure
            pass
        
        log(f"⚠️ HTML scraping not fully implemented - returning empty")
        return {'rounds': {}, 'updated': datetime.now().isoformat(), 'source': 'html_scrape_empty'}
        
    except Exception as e:
        log(f"❌ HTML scrape failed: {e}")
        return {'rounds': {}, 'updated': datetime.now().isoformat(), 'source': 'error'}


def map_tournament_id(current_tournament: dict) -> str:
    """Map our tournament name to Premier Padel tournament ID."""
    name = current_tournament.get('name', '').lower()
    location = current_tournament.get('location', '').lower()
    
    # Map known tournaments to Premier Padel IDs
    tournament_map = {
        'asunción': 'asuncion-2026',
        'asuncion': 'asuncion-2026',
        'buenos aires': 'buenos-aires-2026',
        'brussels': 'brussels-2026',
        'bruselas': 'brussels-2026',
        'newgiza': 'newgiza-2026',
        'el gouna': 'el-gouna-2026',
        'paris': 'paris-2026',
        'roma': 'rome-2026',
        'rome': 'rome-2026',
    }
    
    for key, tournament_id in tournament_map.items():
        if key in name or key in location:
            log(f"Mapped '{name}' to tournament ID: {tournament_id}")
            return tournament_id
    
    # Default: try to construct from name
    safe_name = re.sub(r'[^a-z0-9]', '-', name.replace('p1', '').replace('p2', '').strip())
    tournament_id = f"{safe_name}-2026"
    log(f"Constructed tournament ID: {tournament_id}")
    return tournament_id


def update_state_with_results(state: dict, draw_data: dict) -> dict:
    """Update tournament state with fetched results."""
    current = state.get('current_tournament', {})
    
    # Add draw data to state
    state['current_draw'] = draw_data
    
    # Update current round based on what's live/finished
    rounds = draw_data.get('rounds', {})
    
    # Determine current round (highest round with live/scheduled matches)
    round_order = ['round_of_32', 'round_of_16', 'quarters', 'semis', 'final']
    
    for round_key in reversed(round_order):
        round_matches = rounds.get(round_key, [])
        if round_matches:
            # Check if any matches are live or scheduled
            has_live = any(m.get('status') == 'live' for m in round_matches)
            has_scheduled = any(m.get('status') == 'scheduled' for m in round_matches)
            
            if has_live or has_scheduled:
                current['current_round'] = round_key.replace('_', ' ').title()
                break
    
    state['current_tournament'] = current
    state['last_results_update'] = datetime.now().isoformat()
    
    return state


def main():
    log("=" * 60)
    log("LIVE SCORE AGENT STARTED")
    log("=" * 60)
    
    # Load current state
    state = load_state()
    current = state.get('current_tournament', {})
    
    # Check if tournament is live
    if current.get('status') != 'live':
        log(f"Tournament status is '{current.get('status')}', skipping live score fetch")
        log("Will only fetch for 'live' status tournaments")
        return
    
    # Map tournament to Premier Padel ID
    tournament_id = map_tournament_id(current)
    
    # Fetch draw/results
    draw_data = fetch_premier_padel_draw(tournament_id)
    
    if draw_data.get('rounds'):
        # Update state with results
        state = update_state_with_results(state, draw_data)
        save_state(state)
        
        # Log summary
        total_matches = sum(len(matches) for matches in draw_data.get('rounds', {}).values())
        log(f"✅ Updated state with {total_matches} matches across {len(draw_data.get('rounds', {}))} rounds")
        
        # Print round summary
        for round_name, matches in draw_data.get('rounds', {}).items():
            live_count = sum(1 for m in matches if m.get('status') == 'live')
            finished_count = sum(1 for m in matches if m.get('status') == 'finished')
            scheduled_count = sum(1 for m in matches if m.get('status') == 'scheduled')
            log(f"  {round_name}: {len(matches)} matches ({live_count} live, {finished_count} finished, {scheduled_count} scheduled)")
    else:
        log("⚠️ No draw data received - tournament may not have started or API unavailable")
    
    log("=" * 60)
    log("LIVE SCORE AGENT COMPLETED")
    log("=" * 60)


if __name__ == "__main__":
    main()
