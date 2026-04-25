#!/usr/bin/env python3
"""
Padel News Dynamic Flow Controller v1.0
=======================================
This script orchestrates the entire dynamic website based on tournament state.

FLOW:
1. Check current tournament status (from PadelAPI or scraping)
2. Update RESULTS page with current matches
3. Update INDEX page banner with current tournament/phase
4. Update ACTUALIDAD page - reorder news by current tournament
5. If tournament ends → promote to past, start new tournament
6. Alert agent via heartbeat for human decisions

CRON: Runs every 10 minutes via launchd
"""

import requests
import json
import re
import os
from datetime import datetime
from pathlib import Path

# Paths
DATA_DIR = Path("/Users/cristian/Sites/padel_news/data")
STATE_FILE = Path("/Users/cristian/.openclaw/workspace/tournament_state.json")
LOG_FILE = Path("/Users/cristian/.openclaw/workspace/dynamic_flow.log")
ALERT_FILE = Path("/Users/cristian/.openclaw/workspace/PENDING_DECISIONS.txt")

# Pages to update
PAGES = {
    "resultados": "/Users/cristian/Sites/padel_news/resultados.html",
    "index": "/Users/cristian/Sites/padel_news/index.html",
    "actualidad": "/Users/cristian/Sites/padel_news/actualidad.html",
    "torneos": "/Users/cristian/Sites/padel_news/torneos.html",
}

# Current tournament config
CURRENT_TOURNAMENT = {
    "id": "86",  # Brussels P2
    "name": "Brussels P2 2026",
    "location": "Bruselas, Bélgica",
    "dates": "20-26 Abril 2026",
}

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
        return {
            "current_tournament": CURRENT_TOURNAMENT["name"],
            "tournament_id": CURRENT_TOURNAMENT["id"],
            "phase": "semifinal",
            "status": "in_progress",  # in_progress, finished
            "matches": {},
            "last_update": None,
            "past_tournaments": []
        }

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def fetch_tournament_data(tournament_id):
    """Fetch tournament data from FantasyPadelTour"""
    try:
        url = f"https://en.fantasypadeltour.com/games/{tournament_id}"
        r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=20)
        if r.status_code == 200:
            return r.text
    except Exception as e:
        log(f"Fetch error: {e}")
    return None

def parse_match_score(text, start_idx):
    """Extract a match score from HTML text starting at given index"""
    # Look for patterns like "6-4, 6-3" or "7-6(4), 6-2"
    pattern = r'(\d+-\d+(?:\(\d+\))?)'
    matches = re.findall(pattern, text[start_idx:start_idx+200])
    return matches[:3] if matches else []

def detect_current_phase(html, state):
    """Detect current tournament phase based on results"""
    current_phase = state.get("phase", "semifinal")
    
    # Check if semifinal 1 is complete (Lebron/Augsburger vs Galan/Chingotto)
    sf1_done = bool(re.search(r'Lebrón.*?6-4.*?6-4.*?(Chingotto|Galán)', html, re.DOTALL | re.IGNORECASE))
    
    # Check if semifinal 2 is complete (Tapia/Coello vs Stupaczuk/Yanguas)  
    sf2_done = bool(re.search(r'Tapia.*?\d+-\d+.*?Stupaczuk|Yanguas.*?\d+-\d+.*?Coello', html, re.DOTALL))
    
    if current_phase == "semifinal":
        if sf1_done and sf2_done:
            return "final"  # Both semifinals done, time for final
        elif sf1_done:
            return "semifinal_sf1done"  # SF1 done, waiting for SF2
        else:
            return "semifinal"  # Still waiting for SF1
    
    elif current_phase == "final":
        # Check if final is complete - look for winner announcement in news
        winner = check_for_tournament_end()
        if winner and winner != "NEXT_TOURNAMENT":
            state["winner"] = winner
            return "FINISHED"
        return "final"
    
    elif current_phase == "FINISHED":
        return "FINISHED"
    
    return current_phase

def check_for_tournament_end():
    """Check if tournament has ended by looking at sports news"""
    try:
        r = requests.get(
            "https://www.marca.com/padel/",
            headers={'User-Agent': 'Mozilla/5.0'},
            timeout=15
        )
        text = r.text.lower()
        
        if 'brussels' in text or 'bruselas' in text:
            # Look for winner announcement
            patterns = [
                r'(tapia.*coello|coello.*tapia).*(gana|victoria|campeón)',
                r'tapia.*coello.*\d+-\d+.*\d+-\d+',  # Score published
                r'brussels.*(gana|victoria)',
            ]
            for p in patterns:
                if re.search(p, text):
                    return "Tapia/Coello"
        
        # Alternative: check for next tournament announcement
        if 'next tournament' in text or 'próximo torneo' in text:
            return "NEXT_TOURNAMENT"
            
        return None
    except:
        return None

def update_results_page(state):
    """Update main results page with current tournament data"""
    log("Updating results page...")
    
    page_path = PAGES["resultados"]
    with open(page_path, 'r') as f:
        content = f.read()
    
    phase = state.get("phase", "semifinal")
    
    # Update badge
    badge_text = f"🔴 {CURRENT_TOURNAMENT['name']} - {phase.upper()}"
    if phase == "final":
        badge_text = f"🏆 {CURRENT_TOURNAMENT['name']} FINAL"
    elif phase == "FINISHED":
        badge_text = f"🏆 {CURRENT_TOURNAMENT['name']} TERMINADO"
    
    content = re.sub(
        r'<span class="live-badge">[^<]*</span>',
        f'<span class="live-badge">{badge_text}</span>',
        content
    )
    
    # Update status
    status_text = {
        "semifinal": "Semifinales",
        "final": "Final",
        "FINISHED": "Finalizado"
    }.get(phase, phase)
    
    content = re.sub(
        r'<p style="font-size: 1\.3rem; font-weight: 700;">[^<]*</p>',
        f'<p style="font-size: 1.3rem; font-weight: 700;">{status_text}</p>',
        content
    )
    
    with open(page_path, 'w') as f:
        f.write(content)
    
    log(f"Results page updated - Phase: {phase}")

def update_index_banner(state):
    """Update index page with current tournament"""
    log("Updating index banner...")
    
    page_path = PAGES["index"]
    with open(page_path, 'r') as f:
        content = f.read()
    
    phase = state.get("phase", "semifinal")
    
    badge_text = f"🔴 {CURRENT_TOURNAMENT['name']} - {phase.upper()}"
    if phase == "final":
        badge_text = f"🏆 {CURRENT_TOURNAMENT['name']} FINAL"
    elif phase == "FINISHED":
        badge_text = f"🏆 {CURRENT_TOURNAMENT['name']} TERMINADO"
    
    content = re.sub(
        r'<span class="live-badge">[^<]*</span>',
        f'<span class="live-badge">{badge_text}</span>',
        content
    )
    
    with open(page_path, 'w') as f:
        f.write(content)
    
    log("Index banner updated")

def update_actualidad_order(state):
    """Update actualidad page - reorder news based on current tournament"""
    log("Updating actualidad page...")
    
    page_path = PAGES["actualidad"]
    with open(page_path, 'r') as f:
        content = f.read()
    
    phase = state.get("phase", "semifinal")
    
    # Update badge
    badge_text = f"🔴 {CURRENT_TOURNAMENT['name']} EN JUEGO"
    if phase == "FINISHED":
        badge_text = f"🏆 {CURRENT_TOURNAMENT['name']} TERMINADO"
    
    content = re.sub(
        r'<span class="live-badge">[^<]*</span>',
        f'<span class="live-badge">{badge_text}</span>',
        content
    )
    
    with open(page_path, 'w') as f:
        f.write(content)
    
    log("Actualidad page updated")

def update_torneos_page(state):
    """Update torneos page - show current and past tournaments"""
    log("Updating torneos page...")
    
    page_path = PAGES["torneos"]
    with open(page_path, 'r') as f:
        content = f.read()
    
    phase = state.get("phase", "semifinal")
    
    badge_text = f"🔴 {CURRENT_TOURNAMENT['name']} - {phase.upper()}"
    if phase == "FINISHED":
        badge_text = f"🏆 {CURRENT_TOURNAMENT['name']} TERMINADO"
    
    content = re.sub(
        r'<span class="live-badge">[^<]*</span>',
        f'<span class="live-badge">{badge_text}</span>',
        content
    )
    
    with open(page_path, 'w') as f:
        f.write(content)
    
    log("Torneos page updated")

def promote_tournament_to_past(state):
    """Move finished tournament to past tournaments"""
    log("Promoting tournament to past...")
    
    past = state.get("past_tournaments", [])
    past.insert(0, {
        "name": CURRENT_TOURNAMENT["name"],
        "id": CURRENT_TOURNAMENT["id"],
        "finished_date": datetime.now().isoformat(),
        "winner": state.get("winner", "TBD"),
    })
    state["past_tournaments"] = past[:5]  # Keep last 5
    
    return state

def create_agent_alert(state, action_needed):
    """Create alert file for agent heartbeat to pick up"""
    log(f"Creating agent alert: {action_needed}")
    
    alerts = []
    if os.path.exists(ALERT_FILE):
        with open(ALERT_FILE, 'r') as f:
            alerts = [l.strip() for l in f.readlines() if l.strip()]
    
    alert_line = f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] {action_needed}"
    alerts.append(alert_line)
    
    with open(ALERT_FILE, 'w') as f:
        f.write("\n".join(alerts))

def main():
    log("=== DYNAMIC FLOW CONTROLLER ===")
    log(f"Checking: {CURRENT_TOURNAMENT['name']}")
    
    state = load_state()
    html = fetch_tournament_data(CURRENT_TOURNAMENT["id"])
    
    if html:
        new_phase = detect_current_phase(html, state)
        log(f"Detected phase: {new_phase}")
        
        # Handle phase transitions
        if new_phase == "FINISHED":
            log("🎉 TOURNAMENT FINISHED!")
            
            state["phase"] = "FINISHED"
            state["status"] = "finished"
            state["winner"] = check_for_tournament_end() or "TBD"
            save_state(state)
            
            # Update all pages to show finished
            update_results_page(state)
            update_index_banner(state)
            update_actualidad_order(state)
            update_torneos_page(state)
            
            # Alert agent: needs human decision for next tournament
            create_agent_alert(state, f"TOURNAMENT FINISHED: {CURRENT_TOURNAMENT['name']} - Winner: {state['winner']}. Need to setup next tournament in resultados.html")
            
        elif new_phase != state.get("phase"):
            log(f"Phase changed: {state.get('phase')} → {new_phase}")
            state["phase"] = new_phase
            save_state(state)
            
            # Update all pages
            update_results_page(state)
            update_index_banner(state)
            update_actualidad_order(state)
            update_torneos_page(state)
            
            create_agent_alert(state, f"Phase update: {CURRENT_TOURNAMENT['name']} now in {new_phase}")
        
        else:
            log("No phase change detected")
            # Still update timestamps
            state["last_update"] = datetime.now().isoformat()
            save_state(state)
    
    else:
        log("Could not fetch tournament data")
    
    log("=== FLOW COMPLETE ===")

if __name__ == "__main__":
    main()