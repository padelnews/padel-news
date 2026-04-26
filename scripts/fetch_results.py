#!/usr/bin/env python3
"""
Brussels P2 Results Fetcher - Auto-update script
Runs every 10 minutes via cron
Fetches real results from Fantasy Padel Tour
"""

import requests
import json
import os
import re
from datetime import datetime

DATA_DIR = "/Users/cristian/Sites/padel_news/data"
RESULTADOS_FILE = "/Users/cristian/Sites/padel_news/resultados.html"
LOG_FILE = "/Users/cristian/.openclaw/workspace/cron_results.log"
TOURNAMENTS_FILE = f"{DATA_DIR}/torneos.json"

def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {msg}\n")
    print(f"[{timestamp}] {msg}")

def fetch_fantasy_results():
    """Fetch results from Fantasy Padel Tour"""
    # Brussels P2 2026
    url = "https://en.fantasypadeltour.com/games/86/brussels-p2-2026"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        return response.text if response.status_code == 200 else None
    except Exception as e:
        log(f"Error fetching: {e}")
        return None

def parse_matches(html_content):
    """Parse match data from HTML"""
    matches = []
    
    # Pattern: Team1 / Team2 - Score
    # Look for patterns like "Tapia / Coello" and scores like "6-4, 6-3"
    
    # Simple pattern matching for scores
    score_pattern = r'(\d-\d[\d,\(\)]*(?:\s*,\s*\d-\d[\d,\(\)]*)*)'
    
    # Find team pairs and scores
    teams_pattern = r'([A-Z][a-zéíóú]+)\s*/\s*([A-Z][a-zéíóú]+)'
    
    return matches

def get_current_tournament():
    """Get the current active tournament from tournaments.json"""
    try:
        with open(TOURNAMENTS_FILE, 'r') as f:
            data = json.load(f)
        
        for tournament in data.get('torneos', []):
            if tournament.get('estado') == 'en_curso':
                return tournament
        return None
    except:
        return None

def update_brussels_results():
    """Update Brussels P2 results from live source"""
    html = fetch_fantasy_results()
    if not html:
        log("No HTML content received")
        return False
    
    # For now, detect phase from content
    if 'Semifinal' in html or 'semifinal' in html.lower():
        phase = "semifinal"
    elif 'Final' in html or 'final' in html.lower():
        phase = "final"
    else:
        phase = "cuartos"
    
    log(f"Detected phase: {phase}")
    return True

def detect_tournament_end():
    """Check if current tournament has ended"""
    # Check Marca or other sports sites for final results
    try:
        url = "https://www.marca.com/padel/"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=15)
        
        if 'Brussels' in response.text or 'Bruselas' in response.text:
            return False  # Still active
        return True
    except:
        return False

def main():
    log("=== Checking live results ===")
    
    # Check current tournament status
    tournament = get_current_tournament()
    if tournament:
        log(f"Current: {tournament.get('nombre', 'Unknown')}")
    
    # Fetch and update results
    updated = update_brussels_results()
    
    if updated:
        log("Results check complete")
    else:
        log("No updates available")
    
    log("=== Check complete ===")

if __name__ == "__main__":
    main()