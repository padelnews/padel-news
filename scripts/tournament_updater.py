#!/usr/bin/env python3
"""
Padel Tournament Auto-Updater v4.2
Real results scraping with smart phase detection
"""

import requests
import json
import re
from datetime import datetime

DATA_DIR = "/Users/cristian/Sites/padel_news/data"
STATE_FILE = "/Users/cristian/.openclaw/workspace/tournament_state.json"
LOG_FILE = "/Users/cristian/.openclaw/workspace/tournament_updater.log"
RESULTADOS_HTML = "/Users/cristian/Sites/padel_news/resultados.html"
INDEX_HTML = "/Users/cristian/Sites/padel_news/index.html"
ACTUALIDAD_HTML = "/Users/cristian/Sites/padel_news/actualidad.html"

TOURNAMENT_ID = "86"  # Brussels P2

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
        return {"current_tournament_id": TOURNAMENT_ID, "phase": "semifinal", "finished": False}

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def get_headers():
    return {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept': 'text/html',
        'Accept-Language': 'es,en;q=0.9',
    }

def fetch_tournament():
    url = f"https://en.fantasypadeltour.com/games/{TOURNAMENT_ID}"
    r = requests.get(url, headers=get_headers(), timeout=20)
    return r.text if r.status_code == 200 else None

def detect_phase_smart(html):
    """Smart phase detection - count scores in match blocks only"""
    
    # Count match results (pairs of set scores)
    # Format: "6-4, 6-3" or "7-6(4), 6-2"
    match_results = len(re.findall(r'(\d-\d)[,\s]+(\d-\d)', html))
    
    log(f"Match results found: {match_results}")
    
    # Brussels P2 structure:
    # R32 (8 matches) + R16 (8 matches) + QF (4 matches) + SF (2 matches) + F (1 match) = 23 max
    
    if match_results >= 21:  # Through semifinals + potential final
        # Check if final has actual winner
        if '🏆 FINAL' in html or re.search(r'ganador|winner|champion', html, re.I):
            return "final", True
        else:
            return "semifinal", False
    elif match_results >= 17:  # Through QF
        return "quarter", False
    elif match_results >= 9:   # Through R16  
        return "r16", False
    else:
        return "r32", False

def update_results_page(phase):
    """Update the results page with correct phase"""
    try:
        with open(RESULTADOS_HTML, 'r') as f:
            content = f.read()
        
        phase_labels = {
            "r32": "Dieciseisavos",
            "r16": "Octavos de Final", 
            "quarter": "Cuartos de Final",
            "semifinal": "Semifinales",
            "final": "FINAL"
        }
        
        badge_text = f"🔴 BRUSSELS P2 - {phase_labels.get(phase, phase)}"
        if phase == "final":
            badge_text = "🏆 BRUSSELS P2 FINAL"
        
        content = re.sub(
            r'<span class="live-badge">[^<]*</span>',
            f'<span class="live-badge">{badge_text}</span>',
            content
        )
        
        content = re.sub(
            r'<p style="font-size: 1\.3rem; font-weight: 700;">[^<]*</p>',
            f'<p style="font-size: 1.3rem; font-weight: 700;">{phase_labels.get(phase, phase)}</p>',
            content
        )
        
        with open(RESULTADOS_HTML, 'w') as f:
            f.write(content)
        
        log(f"Updated resultados.html - {phase_labels.get(phase, phase)}")
    except Exception as e:
        log(f"Error updating results: {e}")

def update_index_banner(tournament_name, phase):
    """Update main index banner"""
    try:
        with open(INDEX_HTML, 'r') as f:
            content = f.read()
        
        badge_text = f"🔴 {tournament_name} - {phase.upper()}"
        content = re.sub(r'<span class="live-badge">[^<]*</span>', f'<span class="live-badge">{badge_text}</span>', content)
        
        with open(INDEX_HTML, 'w') as f:
            f.write(content)
        
        log(f"Updated index.html banner")
    except Exception as e:
        log(f"Error updating index: {e}")

def update_actualidad_banner(tournament_name, phase):
    """Update actualidad page banner"""
    try:
        with open(ACTUALIDAD_HTML, 'r') as f:
            content = f.read()
        
        badge_text = f"🔴 {tournament_name} EN JUEGO"
        content = re.sub(r'<span class="live-badge">[^<]*</span>', f'<span class="live-badge">{badge_text}</span>', content)
        
        with open(ACTUALIDAD_HTML, 'w') as f:
            f.write(content)
        
        log(f"Updated actualidad.html banner")
    except Exception as e:
        log(f"Error updating actualidad: {e}")

def check_for_tournament_end():
    """Check sports news to see if tournament really ended"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get("https://www.marca.com/padel/", headers=headers, timeout=15)
        text = r.text.lower()
        
        if 'brussels' in text or 'bruselas' in text:
            patterns = ['tapia.*coello.*ganador', 'coello.*tapia.*título', 'brussels.*final']
            for p in patterns:
                if re.search(p, text):
                    return True
        return False
    except:
        return False

def main():
    log("=== Tournament Updater v4.2 ===")
    
    state = load_state()
    html = fetch_tournament()
    
    if html:
        phase, finished = detect_phase_smart(html)
        
        # If phase says final but we can't verify, check sports news
        if phase == "final" and not finished:
            if check_for_tournament_end():
                finished = True
            else:
                phase = "semifinal"
                finished = False
        
        log(f"Detected: phase={phase}, finished={finished}")
        
        update_results_page(phase)
        update_index_banner("Brussels P2", phase)
        update_actualidad_banner("Brussels P2", phase)
        
        state["phase"] = phase
        state["finished"] = finished
        state["last_update"] = datetime.now().isoformat()
        save_state(state)
        
        if finished:
            log("🎉 Tournament finished! Needs next setup.")
            with open("/Users/cristian/.openclaw/workspace/TOURNAMENT_ENDED.txt", "w") as f:
                f.write(f"{datetime.now().isoformat()}: Tournament ended\n")
    else:
        log("Failed to fetch tournament data")
    
    log("=== Done ===")

if __name__ == "__main__":
    main()