#!/usr/bin/env python3
"""
Padel News - Live Score Updater
================================
Updates match results every 10 minutes during live tournaments.

Flow:
1. Check if tournament is live
2. Fetch latest results from Premier Padel (or update mock data)
3. Update draw JSON file
4. Regenerate results.html
5. Commit and push to GitHub

CRON: Every 10 minutes via launchd
"""

import json
import subprocess
from datetime import datetime
from pathlib import Path
import random

PADEL_DIR = Path("/Users/cristian/Sites/padel_news")
STATE_FILE = PADEL_DIR / "scripts" / "tournament_state.json"
DRAW_FILE = PADEL_DIR / "data" / "asuncion_p1_draw.json"
LOG_FILE = PADEL_DIR / "scripts" / "livescore_updater.log"


def log(msg: str):
    """Log with timestamp."""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")
    print(line)


def load_json(filepath: Path) -> dict:
    """Load JSON file."""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except Exception as e:
        log(f"ERROR loading {filepath}: {e}")
        return {}


def save_json(filepath: Path, data: dict):
    """Save JSON file."""
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    log(f"Saved {filepath}")


def simulate_match_progress(draw_data: dict) -> dict:
    """
    Simulate match progress for demo purposes.
    In production, this would fetch from Premier Padel API.
    
    Updates:
    - Live matches: update scores randomly
    - Scheduled matches: may become live
    - Finished matches: stay finished
    """
    log("Simulating match progress...")
    
    rounds = draw_data.get('rounds', {})
    
    # Process Round of 16 matches
    r16_matches = rounds.get('round_of_16', [])
    
    for match in r16_matches:
        status = match.get('status')
        
        if status == 'live':
            # Update score randomly (simulate progress)
            current_score = match.get('score', '')
            
            # 30% chance to finish the match
            if random.random() < 0.3:
                match['status'] = 'finished'
                match['score'] = f"6-{random.choice([2,3,4])}, 6-{random.choice([2,3,4])}"
                match['winner'] = 'team1' if random.random() > 0.3 else 'team2'
                log(f"  Match finished: {match['score']}")
            else:
                # Update ongoing score
                set1 = f"6-{random.choice([2,3,4])}"
                set2_games = random.randint(2, 5)
                match['score'] = f"{set1}, {set2_games}-{random.randint(0, set2_games-1)}"
                log(f"  Match updated: {match['score']}")
        
        elif status == 'scheduled':
            # 20% chance to become live
            if random.random() < 0.2:
                match['status'] = 'live'
                match['score'] = f"{random.choice([0,1,2])}-{random.choice([0,1,2])}"
                log(f"  Match started: {match['team1']['players'][0]} vs {match['team2']['players'][0]}")
    
    # If all R16 finished, start quarters
    r16_finished = all(m.get('status') == 'finished' for m in r16_matches)
    if r16_finished and not rounds.get('quarters'):
        log("  Generating Quarter-finals draw...")
        # Create quarter-finals from R16 winners
        quarters = []
        for i in range(4):
            winner1 = r16_matches[i*2].get('winner', 'team1')
            winner2 = r16_matches[i*2+1].get('winner', 'team1')
            
            team1_players = r16_matches[i*2][winner1]['players']
            team2_players = r16_matches[i*2+1][winner2]['players']
            
            quarters.append({
                'match_id': f'q_{i+1}',
                'team1': {'players': team1_players, 'country': 'TBD', 'seed': None},
                'team2': {'players': team2_players, 'country': 'TBD', 'seed': None},
                'score': '',
                'status': 'scheduled',
                'scheduled_time': f'{16 + i*2}:00',
                'winner': None
            })
        
        rounds['quarters'] = quarters
    
    draw_data['rounds'] = rounds
    draw_data['last_updated'] = datetime.now().isoformat()
    
    return draw_data


def regenerate_pages():
    """Run website generator to update HTML."""
    log("Regenerating website pages...")
    
    try:
        result = subprocess.run(
            ['python3', 'scripts/website_generator.py'],
            cwd=str(PADEL_DIR),
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            log("✅ Pages regenerated successfully")
            return True
        else:
            log(f"❌ Generation failed: {result.stderr}")
            return False
            
    except Exception as e:
        log(f"❌ Generation error: {e}")
        return False


def commit_and_push():
    """Commit and push changes to GitHub."""
    log("Committing and pushing changes...")
    
    try:
        # Check for changes
        result = subprocess.run(
            ['git', 'diff', '--name-only'],
            cwd=str(PADEL_DIR),
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if not result.stdout.strip():
            log("No changes to commit")
            return True
        
        # Add changes
        subprocess.run(['git', 'add', 'data/asuncion_p1_draw.json', 'resultados.html'], 
                      cwd=str(PADEL_DIR), timeout=30, check=True)
        
        # Commit
        timestamp = datetime.now().strftime("%H:%M")
        subprocess.run(
            ['git', 'commit', '-m', f'🔴 Live score update {timestamp}'],
            cwd=str(PADEL_DIR),
            timeout=30,
            check=True
        )
        
        # Push
        result = subprocess.run(
            ['git', 'push', 'origin', 'main'],
            cwd=str(PADEL_DIR),
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            log("✅ Changes pushed to GitHub")
            return True
        else:
            log(f"⚠️ Push failed, trying pull+push...")
            subprocess.run(['git', 'pull', '--no-rebase', '-X', 'ours'], 
                         cwd=str(PADEL_DIR), timeout=60, check=True)
            subprocess.run(['git', 'push', 'origin', 'main'], 
                         cwd=str(PADEL_DIR), timeout=120, check=True)
            log("✅ Pull+push successful")
            return True
            
    except Exception as e:
        log(f"❌ Git error: {e}")
        return False


def main():
    log("=" * 60)
    log("LIVESCORE UPDATER STARTED")
    log("=" * 60)
    
    # Load state
    state = load_json(STATE_FILE)
    current = state.get('current_tournament', {})
    
    # Check if tournament is live
    if current.get('status') != 'live':
        log(f"Tournament status: {current.get('status')} - skipping update")
        log("Will only update when status is 'live'")
        return
    
    # Load draw data
    draw_data = load_json(DRAW_FILE)
    if not draw_data:
        log("❌ No draw data found")
        return
    
    log(f"Current tournament: {current.get('name')}")
    log(f"Current round: {current.get('current_round')}")
    
    # Update match progress (simulate for now)
    draw_data = simulate_match_progress(draw_data)
    
    # Save updated draw
    save_json(DRAW_FILE, draw_data)
    
    # Regenerate pages
    if regenerate_pages():
        # Commit and push
        commit_and_push()
    
    log("=" * 60)
    log("LIVESCORE UPDATER COMPLETED")
    log("=" * 60)


if __name__ == "__main__":
    main()
