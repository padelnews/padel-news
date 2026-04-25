#!/usr/bin/env python3
"""
Padel News Live Score Scraper v4.0
================================
Scrapes live scores from premierpadel.com during finals.
FREE solution - no API needed.
Runs every 2 minutes during final day via launchd.

Source: https://premierpadel.com/es (OFFICIAL)
"""

import requests
import re
from datetime import datetime
from pathlib import Path

# Paths
PAGES = {
    "resultados": "/Users/cristian/Sites/padel_news/resultados.html",
    "index": "/Users/cristian/Sites/padel_news/index.html",
    "actualidad": "/Users/cristian/Sites/padel_news/actualidad.html",
}
LOG_FILE = Path("/Users/cristian/.openclaw/workspace/live_score.log")

def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")
    print(line)

def fetch_live_data():
    """Fetch live data from premierpadel.com"""
    try:
        url = "https://premierpadel.com/es"
        r = requests.get(url, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }, timeout=30)
        if r.status_code == 200:
            return r.text
    except Exception as e:
        log(f"Fetch error: {e}")
    return None

def parse_match_scores(html):
    """Parse match scores from premierpadel.com HTML"""
    
    # Find block from Coello to Yanguas + 600 chars after
    coello_pos = html.find('Coello')
    yanguas_pos = html.find('Yanguas')
    
    if coello_pos < 0 or yanguas_pos < 0:
        return None
    
    match_block = html[coello_pos:yanguas_pos+600]
    
    # Extract all scores
    all_p = re.findall(r'<p[^>]*>([^<]+)</p>', match_block)
    scores = [p for p in all_p if p.strip().isdigit() or p.strip() == '-']
    
    if len(scores) >= 5:
        # scores[0] = team1 set1, scores[1] = team1 set2
        # scores[3] = team2 set1, scores[4] = team2 set2
        # scores[2] is "-" tiebreak indicator, skip it
        return {
            "team1": "Tapia/Coello",
            "team1_set1": int(scores[0]),
            "team1_set2": int(scores[1]),
            "team2": "Stupaczuk/Yanguas",
            "team2_set1": int(scores[3]),
            "team2_set2": int(scores[4]),
            "all_scores": scores
        }
    
    return None

def format_live_banner(score_data):
    """Format live score for display"""
    if not score_data:
        return "🔴 EN DIRECTO - FINAL Brussels P2<br>Tapia/Coello vs Lebrón/Augsburger<br>Esperando resultados..."
    
    t1 = score_data["team1"]
    t2 = score_data["team2"]
    
    s1 = score_data.get("team1_set1")
    s2 = score_data.get("team1_set2")
    s3 = score_data.get("team2_set1")
    s4 = score_data.get("team2_set2")
    
    sets = []
    if s1 is not None and s3 is not None:
        sets.append(f"Set 1: {s1}-{s3}")
    if s2 is not None and s4 is not None:
        sets.append(f"Set 2: {s2}-{s4}")
    
    score_text = " • ".join(sets) if sets else "En juego"
    
    return f"🔴 EN DIRECTO - FINAL Brussels P2<br>{t1} vs {t2}<br>{score_text}"

def update_pages(banner_text):
    """Update all pages with live score banner"""
    for name, path in PAGES.items():
        try:
            with open(path, 'r') as f:
                content = f.read()
            
            content = re.sub(
                r'<span class="live-badge">[^<]*</span>',
                f'<span class="live-badge">{banner_text}</span>',
                content
            )
            
            with open(path, 'w') as f:
                f.write(content)
            
            log(f"Updated {name}")
        except Exception as e:
            log(f"Error updating {name}: {e}")

def main():
    log("=== LIVE SCORE SCRAPER v4 ===")
    log(f"Checking at {datetime.now().strftime('%H:%M:%S')}")
    
    html = fetch_live_data()
    
    if html:
        score_data = parse_match_scores(html)
        
        if score_data:
            banner = format_live_banner(score_data)
            log(f"Scores: {score_data['all_scores']}")
            log(f"Banner: {banner}")
            update_pages(banner)
        else:
            log("No scores parsed")
    else:
        log("Could not fetch data")
    
    log("=== SCRAPE COMPLETE ===")

if __name__ == "__main__":
    main()