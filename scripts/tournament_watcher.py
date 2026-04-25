#!/usr/bin/env python3
"""
Tournament Auto-Watcher - Checks for new results every 10 minutes
Detects tournament phase changes and alerts when finished
"""

import requests
import json
import os
import re
from datetime import datetime

DATA_DIR = "/Users/cristian/Sites/padel_news/data"
RESULTADOS_HTML = "/Users/cristian/Sites/padel_news/resultados.html"
LOG_FILE = "/Users/cristian/.openclaw/workspace/tournament_watcher.log"
STATE_FILE = "/Users/cristian/.openclaw/workspace/tournament_state.json"

def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {msg}\n")
    print(f"[{timestamp}] {msg}")

def load_state():
    """Load previous tournament state"""
    try:
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    except:
        return {"last_tournament": None, "last_phase": None, "alert_sent": False}

def save_state(state):
    """Save current tournament state"""
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def fetch_premierpadel_results():
    """Fetch from Premier Padel official"""
    sources = [
        "https://premierpadel.com/en/tournaments-live/brussels-p2/results",
    ]
    
    for url in sources:
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}
            r = requests.get(url, headers=headers, timeout=20)
            if r.status_code == 200:
                return r.text
        except Exception as e:
            log(f"Error fetching {url}: {e}")
    return None

def check_tournament_status():
    """Check if there's a new finished tournament"""
    state = load_state()
    
    # Check sports news for finished tournaments
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get("https://www.marca.com/padel/", headers=headers, timeout=15)
        text = r.text.lower()
        
        # Check for any tournament being discussed
        tournaments_mentioned = []
        
        # Look for Brussels final being discussed
        if 'brussels' in text or 'bruselas' in text:
            if 'final' in text and ('tapia' in text or 'coello' in text or 'galan' in text):
                if state.get("last_tournament") != "brussels_p2":
                    log("Brussels P2 detected as current active tournament")
                    state["last_tournament"] = "brussels_p2"
                    state["last_phase"] = "final"
                    save_state(state)
                    return "brussels_p2_final"
        
        # Check for new tournament
        if 'newgiza' in text:
            return "newgiza_p2"
        elif 'miami' in text and 'p1' in text:
            return "miami_p1"
            
    except Exception as e:
        log(f"Error checking status: {e}")
    
    return None

def detect_current_phase(html):
    """Detect current phase of tournament from HTML"""
    if not html:
        return None
        
    text = html.lower()
    
    if 'final' in text and ('champion' in text or 'ganador' in text or 'título' in text):
        return "final"
    elif 'semifinal' in text or 'semi-final' in text:
        return "semifinal"
    elif 'quarter' in text or 'cuartos' in text:
        return "cuartos"
    elif 'round' in text or 'r16' in text:
        return "r16"
    
    return None

def main():
    log("=== Tournament Watcher Check ===")
    
    state = load_state()
    
    # Check for finished tournaments or phase changes
    result = check_tournament_status()
    
    if result:
        log(f"Tournament status: {result}")
        
        # Alert if tournament just finished
        if isinstance(result, str) and "_final" in result:
            tournament_name = result.replace("_final", "").upper()
            log(f"🎉 ALERT: {tournament_name} FINAL COMPLETE!")
            log("Action needed: Update results.html with final results and move to next tournament")
            
            # Save alert - will be picked up by agent on next heartbeat
            with open("/Users/cristian/.openclaw/workspace/PENDING_TOURNAMENT_ALERT.txt", "w") as f:
                f.write(f"{datetime.now().isoformat()}: {tournament_name} finished - needs results update\n")
    
    else:
        current = state.get("last_tournament", "Unknown")
        phase = state.get("last_phase", "Unknown")
        log(f"Current: {current} - Phase: {phase}")
    
    log("=== Check complete ===")

if __name__ == "__main__":
    main()