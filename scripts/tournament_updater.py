#!/usr/bin/env python3
"""
Padel Tournament Auto-Updater v5.0
Simple, reliable phase detection
Detects phase transitions: semifinal → final → next tournament
"""

import requests
import json
import re
from datetime import datetime

STATE_FILE = "/Users/cristian/.openclaw/workspace/tournament_state.json"
LOG_FILE = "/Users/cristian/.openclaw/workspace/tournament_updater.log"
RESULTADOS_HTML = "/Users/cristian/Sites/padel_news/resultados.html"
INDEX_HTML = "/Users/cristian/Sites/padel_news/index.html"
ACTUALIDAD_HTML = "/Users/cristian/Sites/padel_news/actualidad.html"

TOURNAMENT_ID = "86"

def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{ts}] {msg}\n")
    print(f"[{ts}] {msg}")

def load_state():
    try:
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    except:
        return {"phase": "semifinal", "last_check": None}

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def fetch_tournament():
    try:
        r = requests.get(
            f"https://en.fantasypadeltour.com/games/{TOURNAMENT_ID}",
            headers={'User-Agent': 'Mozilla/5.0'},
            timeout=20
        )
        return r.text if r.status_code == 200 else None
    except:
        return None

def check_sports_news():
    """Check Marca for tournament final result"""
    try:
        r = requests.get(
            "https://www.marca.com/padel/",
            headers={'User-Agent': 'Mozilla/5.0'},
            timeout=15
        )
        text = r.text.lower()
        
        # Look for signs tournament has ended
        if 'brussels' in text:
            # Check for final result patterns
            if re.search(r'(tapia.*coello|coello.*tapia).*(final|gana|victoria)', text):
                return "Tapia/Coello"
            elif re.search(r'(galan.*chingotto|chingotto.*galan).*(final|gana|victoria)', text):
                return "Galan/Chingotto"
            elif re.search(r'brussels.*final.*\d+-\d+', text):
                return "OTHER"
        return None
    except:
        return None

def detect_phase(html, state):
    """Detect current phase based on page content"""
    
    # Current known phase from previous checks
    current_phase = state.get("phase", "semifinal")
    
    # Check if semifinal matches have scores (meaning semifinals done → final)
    if current_phase == "semifinal":
        # Look for semifinal score patterns
        if html:
            # Count how many semifinals show scores
            semi_scores = len(re.findall(r'(Semifinal|SEMI).*?\d+-\d+', html, re.I))
            if semi_scores >= 2:
                # Semifinals done, we're in final
                return "final"
        return "semifinal"
    
    elif current_phase == "final":
        # Check if final has a winner
        winner = check_sports_news()
        if winner:
            log(f"Tournament winner detected: {winner}")
            return "FINISHED"
        return "final"
    
    return current_phase

def update_page_badge(page_path, badge_text):
    """Update live badge on any page"""
    try:
        with open(page_path, 'r') as f:
            content = f.read()
        
        content = re.sub(
            r'<span class="live-badge">[^<]*</span>',
            f'<span class="live-badge">{badge_text}</span>',
            content
        )
        
        with open(page_path, 'w') as f:
            f.write(content)
    except Exception as e:
        log(f"Error updating {page_path}: {e}")

def main():
    log("=== Tournament Updater v5 ===")
    
    state = load_state()
    html = fetch_tournament()
    
    if html:
        phase = detect_phase(html, state)
        log(f"Current phase: {phase}")
        
        if phase == "FINISHED":
            log("🎉 Tournament finished!")
            state["phase"] = "FINISHED"
            state["finished"] = True
            save_state(state)
            
            # Alert for next tournament setup
            with open("/Users/cristian/.openclaw/workspace/TOURNAMENT_FINISHED_ALERT.txt", "w") as f:
                f.write(f"{datetime.now().isoformat()}: Brussels P2 finished - setup next tournament\n")
        else:
            # Update all pages with current phase
            badge = f"🔴 BRUSSELS P2 - {phase.upper()}"
            if phase == "final":
                badge = "🏆 BRUSSELS P2 FINAL"
            
            update_page_badge(RESULTADOS_HTML, badge)
            update_page_badge(INDEX_HTML, badge)
            update_page_badge(ACTUALIDAD_HTML, f"🔴 BRUSSELS P2 EN JUEGO")
            
            state["phase"] = phase
            save_state(state)
    else:
        log("Could not fetch tournament data")
    
    log("=== Done ===")

if __name__ == "__main__":
    main()