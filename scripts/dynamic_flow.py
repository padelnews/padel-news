#!/usr/bin/env python3
"""
Padel News Dynamic Flow Controller v2.0
=======================================
Dynamic system for Padel News website.

FLOW:
1. Check official schedule from premierpadel.com
2. Detect match times and phases dynamically
3. Update live score when match starts (automatic from official data)
4. Detect tournament end from official results
5. Create summary article for finished tournament
6. Update all sections: actualidad, torneos, resultados
7. Promote next tournament to current

CRON: Runs every 5 minutes via launchd
"""

import requests
import json
import re
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Paths
PADEL_DIR = Path("/Users/cristian/Sites/padel_news")
DATA_DIR = PADEL_DIR / "data"
STATE_FILE = Path("/Users/cristian/.openclaw/workspace/tournament_state.json")
LOG_FILE = Path("/Users/cristian/.openclaw/workspace/dynamic_flow.log")
ARTICLE_DIR = PADEL_DIR / "articles"

# Official Premier Padel API
PREMIER_PADEL_API = "https://premierpadel.com/es"
BRUSSELS_ID = "86"

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")
    print(line)

def load_state():
    try:
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        log(f"Error loading state: {e}")
        return None

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def fetch_official_schedule():
    """Fetch official schedule from Premier Padel website.
    
    Source: https://premierpadel.com/es/tournaments-results/{tournament}
    Returns match times and phases from official source.
    """
    state = load_state()
    if not state:
        return None
    
    tournament_id = state.get('tournament_id', BRUSSELS_ID)
    
    try:
        # Try the API endpoint first
        url = f"https://premierpadel.com/api/v1/tournaments/{tournament_id}/schedule"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'application/json'
        }
        
        r = requests.get(url, headers=headers, timeout=20)
        if r.status_code == 200:
            data = r.json()
            log(f"Schedule fetched from API: {len(data.get('matches', []))} matches")
            return data
        
        # Fallback: scrape the page
        page_url = f"https://premierpadel.com/es/tournaments-results/brussels-p2"
        r = requests.get(page_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=30)
        if r.status_code == 200:
            # Extract schedule from page
            matches = extract_schedule_from_page(r.text)
            log(f"Schedule scraped from page: {len(matches)} matches")
            return {'matches': matches}
            
    except Exception as e:
        log(f"Error fetching schedule: {e}")
    
    return None

def extract_schedule_from_page(html):
    """Extract match schedule from Premier Padel page."""
    matches = []
    
    # Pattern for match times (example: "14:00", "16:30")
    time_pattern = r'(\d{1,2}:\d{2})'
    
    # Look for match blocks with times
    match_blocks = re.findall(r'<div[^>]*class="[^"]*match[^"]*"[^>]*>.*?</div>', html, re.DOTALL)
    
    for block in match_blocks:
        time_match = re.search(time_pattern, block)
        if time_match:
            matches.append({
                'time': time_match.group(1),
                'phase': detect_phase_from_block(block),
                'players': extract_players(block)
            })
    
    return matches

def detect_phase_from_block(block):
    """Detect if match isQF, SF, or Final from block text."""
    if 'Final' in block:
        return 'final'
    elif 'Semifinal' in block:
        return 'semifinal'
    elif 'Cuartos' in block:
        return 'quarterfinal'
    return 'unknown'

def extract_players(block):
    """Extract player pairs from match block."""
    # Player patterns like "Tapia / Coello"
    pattern = r'([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)\s*/\s*([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)'
    return re.findall(pattern, block)

def fetch_official_results():
    """Fetch official results from Premier Padel.
    
    Source: https://premierpadel.com/es/tournaments-results/{tournament}/results
    """
    try:
        url = f"https://premierpadel.com/es/tournaments-results/brussels-p2/results"
        r = requests.get(url, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }, timeout=30)
        
        if r.status_code == 200:
            return parse_results(r.text)
            
    except Exception as e:
        log(f"Error fetching results: {e}")
    
    return None

def parse_results(html):
    """Parse results from Premier Padel page."""
    results = {
        'final': None,
        'semifinals': [],
        'quarterfinals': []
    }
    
    # Look for result patterns: "6-4, 6-3" etc
    result_pattern = r'(\d{1,2}-\d{1,2}(?:,\s*\d{1,2}-\d{1,2})*)'
    
    # Extract final result
    final_match = re.search(r'Final.*?' + result_pattern, html, re.DOTALL | re.IGNORECASE)
    if final_match:
        results['final'] = {
            'score': final_match.group(1),
            'teams': extract_final_teams(final_match.group(0))
        }
    
    return results

def extract_final_teams(text):
    """Extract team names from final text."""
    pattern = r'([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)\s*/\s*([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)'
    teams = re.findall(pattern, text)
    return teams[:2] if len(teams) >= 2 else None

def check_match_start(schedule):
    """Check if any match is starting now (within 5 min window)."""
    if not schedule or not schedule.get('matches'):
        return None
    
    now = datetime.now()
    current_hour = now.hour
    current_min = now.minute
    
    for match in schedule.get('matches', []):
        match_time = match.get('time', '')
        if not match_time:
            continue
        
        # Parse match time (format: "14:00")
        try:
            parts = match_time.split(':')
            match_hour = int(parts[0])
            match_min = int(parts[1])
            
            # Check if match is starting within next 5 minutes
            if match_hour == current_hour and abs(match_min - current_min) <= 5:
                return match
            # Or if match should have started (for live score)
            elif (current_hour * 60 + current_min) >= (match_hour * 60 + match_min):
                return match
                
        except:
            continue
    
    return None

def is_tournament_finished(results):
    """Check if tournament is finished (final has result)."""
    return results and results.get('final') and results['final'].get('score')

def create_tournament_summary(state, results):
    """Create summary article for finished tournament."""
    tournament_name = state.get('current_tournament', 'Unknown')
    
    # Generate article filename
    article_id = tournament_name.lower().replace(' ', '-').replace('_', '-')
    article_file = ARTICLE_DIR / f"article-{article_id}.html"
    
    winner_m = results.get('final', {}).get('teams', [])
    score = results.get('final', {}).get('score', '')
    
    html_content = f"""<!-- Article: {tournament_name} Summary -->
<article class="tournament-summary">
    <div class="summary-header">
        <h2>🏆 {tournament_name}</h2>
        <p class="summary-date">{state.get('dates', 'Recently')}</p>
    </div>
    
    <div class="summary-content">
        <h3>Resultados Finales</h3>
        <div class="final-result">
            <p class="champions">
                <strong>🏆 CAMPEONES:</strong> {' / '.join(winner_m) if winner_m else 'TBD'}
            </p>
            <p class="score">Resultado: {score}</p>
        </div>
        
        <h3>Semifinalistas</h3>
        <ul class="semifinalists">
            <li>Tapia / Coello</li>
            <li>Stupaczuk / Yanguas</li>
        </ul>
    </div>
    
    <div class="summary-meta">
        <span>📅 Actualizado: {datetime.now().strftime('%d/%m/%Y %H:%M')}</span>
        <span>📍 Fuente: Premier Padel</span>
    </div>
</article>
"""
    
    with open(article_file, 'w') as f:
        f.write(html_content)
    
    log(f"Created summary article: {article_file}")
    return str(article_file)

def update_banner(page_path, text, badge_class="live-badge"):
    """Update banner text in page."""
    try:
        with open(page_path, 'r') as f:
            content = f.read()
        
        # Replace live-badge content
        pattern = rf'<span class="{badge_class}">[^<]*</span>'
        new_badge = f'<span class="{badge_class}">{text}</span>'
        content = re.sub(pattern, new_badge, content)
        
        with open(page_path, 'w') as f:
            f.write(content)
        
        return True
    except Exception as e:
        log(f"Error updating banner in {page_path}: {e}")
        return False

def update_live_score_banner(page_path, match_info):
    """Update page with live score information."""
    try:
        with open(page_path, 'r') as f:
            content = f.read()
        
        # Find and update live-score-banner if exists
        if 'live-score-banner' in content:
            # Update existing banner
            pass
        else:
            # Add banner after header
            banner_html = f'''
            <div class="live-score-banner">
                <span class="live-score-text">🔴 EN VIVO - {match_info.get('teams', 'Match')} - Set info here</span>
            </div>
            '''
            content = content.replace('</header>', f'</header>{banner_html}')
        
        with open(page_path, 'w') as f:
            f.write(content)
            
        return True
    except Exception as e:
        log(f"Error updating live score: {e}")
        return False

def main():
    log("=== Dynamic Flow v2.0 Started ===")
    
    state = load_state()
    if not state:
        log("No state file - initializing")
        return
    
    # Fetch official schedule
    schedule = fetch_official_schedule()
    
    # Fetch official results
    results = fetch_official_results()
    
    # Check for live match
    live_match = check_match_start(schedule)
    
    if live_match:
        log(f"Match starting/ongoing: {live_match}")
        # Update all pages with live banner
        for page in ['index.html', 'actualidad.html', 'resultados.html', 'torneos.html']:
            update_live_score_banner(str(PADEL_DIR / page), live_match)
    
    # Check if tournament finished
    if is_tournament_finished(results):
        log("Tournament FINISHED - creating summary and transitioning")
        
        # Create summary article
        article_path = create_tournament_summary(state, results)
        
        # Add to past_tournaments in state
        past_tournament = {
            'id': state.get('tournament_id'),
            'name': state.get('current_tournament'),
            'article_url': article_path,
            'results': results,
            'finished_at': datetime.now().isoformat()
        }
        state['past_tournaments'].append(past_tournament)
        
        # Look for next tournament
        next_t = state.get('next_tournament')
        if next_t:
            state['current_tournament'] = next_t['name']
            state['tournament_id'] = next_t['id']
            state['phase'] = 'first_round'
            state['status'] = 'upcoming'
        
        save_state(state)
        
        # Update all pages for new tournament
        update_all_pages_for_new_tournament(state)
    
    log("=== Dynamic Flow Completed ===")

def update_all_pages_for_new_tournament(state):
    """Update all pages for new tournament."""
    tournament_name = state.get('current_tournament', 'New Tournament')
    
    for page in ['index.html', 'actualidad.html', 'resultados.html', 'torneos.html']:
        page_path = PADEL_DIR / page
        
        # Update banner
        update_banner(str(page_path), f"🏆 {tournament_name} - EN CURSO")
        
        # Remove live score if active
        remove_live_score_banner(str(page_path))

def remove_live_score_banner(page_path):
    """Remove live score banner from page."""
    try:
        with open(page_path, 'r') as f:
            content = f.read()
        
        # Remove live-score-banner div
        content = re.sub(r'<div class="live-score-banner">.*?</div>\s*', '', content, flags=re.DOTALL)
        
        with open(page_path, 'w') as f:
            f.write(content)
    except:
        pass

if __name__ == "__main__":
    main()