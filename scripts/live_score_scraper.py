#!/usr/bin/env python3
"""
Padel News Live Score Scraper v2.0
===================================
Activates automatically when match is live.
Fetches live scores from official Premier Padel source.

Source: https://premierpadel.com/es/tournaments-results/{tournament}/live
Runs: Every 2 minutes when match is in progress
"""

import requests
import json
import re
import os
from datetime import datetime
from pathlib import Path

# Paths
PADEL_DIR = Path("/Users/cristian/Sites/padel_news")
PAGES = {
    "index": PADEL_DIR / "index.html",
    "resultados": PADEL_DIR / "resultados.html",
    "actualidad": PADEL_DIR / "actualidad.html"
}
LOG_FILE = Path("/Users/cristian/.openclaw/workspace/live_score.log")
STATE_FILE = Path("/Users/cristian/.openclaw/workspace/tournament_state.json")

PREMIER_PADEL_LIVE_URL = "https://premierpadel.com/es/tournaments-results/brussels-p2"

def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")
    print(line)

def load_state():
    try:
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    except:
        return None

def is_live_score_enabled():
    """Check if live score should be active."""
    state = load_state()
    if not state:
        return False
    return state.get('live_score_active', False)

def enable_live_score():
    """Enable live score mode."""
    state = load_state()
    if state:
        state['live_score_active'] = True
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f, indent=2)
        log("Live score ENABLED")

def disable_live_score():
    """Disable live score mode."""
    state = load_state()
    if state:
        state['live_score_active'] = False
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f, indent=2)
        log("Live score DISABLED")

def fetch_live_score():
    """Fetch live score from official source."""
    try:
        # Try official live endpoint
        url = f"{PREMIER_PADEL_LIVE_URL}/live"
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        r = requests.get(url, headers=headers, timeout=20)
        if r.status_code == 200:
            return parse_live_data(r.text)
        
        # Fallback: scrape main page for live indicator
        r = requests.get(PREMIER_PADEL_LIVE_URL, headers=headers, timeout=20)
        if r.status_code == 200:
            return scrape_live_from_page(r.text)
            
    except Exception as e:
        log(f"Error fetching live score: {e}")
    return None

def parse_live_data(html):
    """Parse live score data from response."""
    # Look for score patterns
    score_pattern = r'(\d{1,2}-\d{1,2}(?:,\s*\d{1,2}-\d{1,2})*)'
    teams_pattern = r'([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)\s*/\s*([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)'
    
    data = {
        'teams': [],
        'score': '',
        'set_info': '',
        'is_live': False
    }
    
    # Check if live indicator exists
    if 'LIVE' in html or 'En Vivo' in html or 'DIRECTO' in html:
        data['is_live'] = True
    
    # Extract score
    score_match = re.search(score_pattern, html)
    if score_match:
        data['score'] = score_match.group(1)
    
    # Extract teams
    teams = re.findall(teams_pattern, html)
    if len(teams) >= 2:
        data['teams'] = [f"{t[0]} / {t[1]}" for t in teams[:2]]
    
    return data

def scrape_live_from_page(html):
    """Scrape live data from main page."""
    data = {
        'teams': ['Tapia / Coello', 'Stupaczuk / Yanguas'],
        'score': '',
        'set_info': '',
        'is_live': False
    }
    
    # Check for live indicators
    if 'LIVE' in html.upper() or 'EN VIVO' in html.upper():
        data['is_live'] = True
    
    # Look for set scores
    set_pattern = r'Set\s*(\d)[:\s]*(\d{1,2})'
    sets = re.findall(set_pattern, html, re.IGNORECASE)
    if sets:
        data['set_info'] = ' • '.join([f"Set {s[0]}: {s[1]}" for s in sets])
    
    # Look for game score
    game_pattern = r'Game[:\s]*(\d{1,2})'
    game = re.search(game_pattern, html, re.IGNORECASE)
    if game:
        data['game_score'] = game.group(1)
    
    return data

def format_live_banner(data):
    """Format live score banner text."""
    if not data or not data.get('is_live'):
        return "🔴 EN VIVO - Brussels P2 2026"
    
    teams = data.get('teams', [])
    score = data.get('score', '')
    set_info = data.get('set_info', '')
    
    teams_str = ' vs '.join(teams) if teams else 'Match'
    score_str = f" | {score}" if score else ""
    set_str = f" | {set_info}" if set_info else ""
    
    return f"🔴 EN VIVO - Brussels P2 | {teams_str}{score_str}{set_str}"

def update_live_banner(page_path, banner_text):
    """Update or add live score banner in page."""
    try:
        with open(page_path, 'r') as f:
            content = f.read()
        
        # Check if live-score-banner exists
        if 'live-score-banner' in content:
            # Update existing
            pattern = r'<span class="live-score-text">[^<]*</span>'
            content = re.sub(pattern, f'<span class="live-score-text">{banner_text}</span>', content)
        else:
            # Add new banner after header
            banner_html = f'''
            <div class="live-score-banner">
                <span class="live-score-text">{banner_text}</span>
            </div>
            '''
            content = content.replace('</header>', f'</header>{banner_html}')
        
        with open(page_path, 'w') as f:
            f.write(content)
        
        return True
    except Exception as e:
        log(f"Error updating banner in {page_path}: {e}")
        return False

def remove_live_banners():
    """Remove all live score banners."""
    for page_name, page_path in PAGES.items():
        try:
            with open(page_path, 'r') as f:
                content = f.read()
            
            # Remove live-score-banner
            content = re.sub(r'\s*<div class="live-score-banner">.*?</div>', '', content, flags=re.DOTALL)
            
            with open(page_path, 'w') as f:
                f.write(content)
            
            log(f"Removed live banner from {page_name}")
        except Exception as e:
            log(f"Error removing banner from {page_name}: {e}")

def main():
    log("=== Live Score Scraper Started ===")
    
    # Check if live score is enabled
    if not is_live_score_enabled():
        log("Live score not enabled - checking if should activate...")
        
        # Check official source for live match
        data = fetch_live_score()
        
        if data and data.get('is_live'):
            log("Match is LIVE - activating live score")
            enable_live_score()
        else:
            log("No live match detected")
            return
    
    # Live score is enabled - fetch current data
    data = fetch_live_score()
    
    if data and data.get('is_live'):
        banner_text = format_live_banner(data)
        log(f"Live: {banner_text}")
        
        # Update all pages
        for page_name, page_path in PAGES.items():
            update_live_banner(str(page_path), banner_text)
        
        # Check if match ended
        if is_match_finished(data):
            log("Match FINISHED - deactivating live score")
            disable_live_score()
            remove_live_banners()
            
            # Update state to tournament finished
            state = load_state()
            if state:
                state['status'] = 'finished'
                state['final_result'] = data
                with open(STATE_FILE, 'w') as f:
                    json.dump(state, f, indent=2)
    else:
        log("Match ended - deactivating")
        disable_live_score()
        remove_live_banners()
    
    log("=== Live Score Scraper Completed ===")

def is_match_finished(data):
    """Check if match has finished (no live indicator)."""
    return data and not data.get('is_live')

if __name__ == "__main__":
    main()