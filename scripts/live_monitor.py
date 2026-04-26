#!/usr/bin/env python3
"""
Live Match Monitor for Padel News v2
====================================
Uses Playwright to check premierpadel.com/tournaments-live every 10 minutes
and update the website when matches are live.
"""

import asyncio
import json
import re
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright

# Paths
PADEL_DIR = Path("/Users/cristian/Sites/padel_news")
STATE_FILE = Path("/Users/cristian/.openclaw/workspace/tournament_state.json")
LOG_FILE = Path("/Users/cristian/.openclaw/workspace/dynamic_flow.log")

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def update_website_live(score_data):
    """Update index.html with live match data"""
    try:
        index_path = PADEL_DIR / "index.html"
        with open(index_path, 'r') as f:
            content = f.read()
        
        # Determine category
        if score_data.get('category') == 'WOMEN F':
            category = "WOMEN FINAL"
        else:
            category = score_data.get('category', 'LIVE')
        
        # Create new banner with live data
        if score_data.get('is_live'):
            new_banner = f'''<span class="live-badge">🔴 EN VIVO {category}: {score_data.get('team1', 'TBD')} {score_data.get('score1', '-')} - {score_data.get('score2', '-')} {score_data.get('team2', 'TBD')}</span>'''
        else:
            new_banner = f'''<span class="live-badge">🏆 {category}: {score_data.get('team1', 'TBD')} vs {score_data.get('team2', 'TBD')}</span>'''
        
        # Replace the live badge
        content = re.sub(r'<span class="live-badge">.*?</span>', new_banner, content, flags=re.DOTALL)
        
        with open(index_path, 'w') as f:
            f.write(content)
        
        log(f"✅ Banner updated: {new_banner}")
        return True
    except Exception as e:
        log(f"❌ Error updating banner: {e}")
        return False

def parse_score(score_str):
    """Parse score like '30-5' to show as '30-5' or 40-30 equivalent"""
    return score_str.replace('-', ' ')

async def check_live_premierpadel():
    """Fetch live data from Premier Padel LIVE page"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        log("🔍 Checking premierpadel.com/tournaments-live for live matches...")
        
        try:
            # Use the LIVE URL - this shows ongoing matches
            await page.goto("https://premierpadel.com/es/tournaments-live/brussels-p2-3", 
                          timeout=30000)
            await asyncio.sleep(8)  # Wait for JS to render
            
            body = await page.locator("body").inner_text()
            lines = body.split('\n')
            
            match_data = {
                'is_live': False,
                'category': '',
                'team1': '',
                'team2': '',
                'score1': '',
                'score2': '',
                'phase': '',
                'time': ''
            }
            
            # Check for LIVE indicators
            if 'EN DIRECTO' in body:
                match_data['is_live'] = True
                log("🔴 MATCH LIVE DETECTED!")
            
            # Look for category (WOMEN F, MEN SF, MEN F, etc)
            for line in lines:
                if 'WOMEN F' in line:
                    match_data['category'] = 'WOMEN F'
                elif 'MEN F' in line:
                    match_data['category'] = 'MEN FINAL'
                elif 'MEN SF' in line or 'SEMI' in line.upper():
                    match_data['category'] = 'MEN SEMI'
            
            # Find match data - look for lines with scores
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                
                # Look for patterns like: "BREA" then "TRIAY" then "30" then "5" etc
                # Or "GONZALEZ" then "JOSEMARIA" then "40" then "4"
                
                # Try to find player pairs
                if len(line) > 3 and not any(c.isdigit() for c in line):
                    # This might be a player name
                    name1 = line
                    # Check next lines for score data
                    j = i + 1
                    scores = []
                    players2 = ""
                    while j < len(lines) and len(scores) < 4:
                        next_line = lines[j].strip()
                        if next_line.replace('-', '').replace(' ', '').isdigit():
                            scores.append(next_line)
                            j += 1
                        elif len(next_line) > 3 and not any(c.isdigit() for c in next_line) and not next_line in ['VER', 'DÓNDE VERLO', 'ESTADÍSTICAS']:
                            players2 = next_line
                            break
                        else:
                            j += 1
                    
                    if len(scores) >= 2 and players2:
                        match_data['team1'] = name1.replace('/', ' / ')
                        match_data['team2'] = players2.replace('/', ' / ')
                        match_data['score1'] = parse_score(scores[0]) if len(scores) > 0 else ""
                        match_data['score2'] = parse_score(scores[1]) if len(scores) > 1 else ""
                        log(f"📊 Match found: {match_data['team1']} {match_data['score1']} - {match_data['score2']} {match_data['team2']}")
                        break
                
                i += 1
            
            await browser.close()
            return match_data
            
        except Exception as e:
            log(f"Error fetching data: {e}")
            await browser.close()
            return None

async def main():
    log("=== LIVE MONITOR v2 STARTED ===")
    
    # Check for live data
    match_data = await check_live_premierpadel()
    
    if match_data and (match_data.get('is_live') or match_data.get('team1')):
        log(f"Match data retrieved: {match_data}")
        
        # Update state
        try:
            with open(STATE_FILE, 'r') as f:
                state = json.load(f)
            state['last_update'] = datetime.now().isoformat()
            state['live_match'] = match_data
            with open(STATE_FILE, 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            log(f"Error saving state: {e}")
        
        # Update website
        update_website_live(match_data)
    else:
        log("⏸️ No live match data found (or match hasn't started yet)")
    
    log("=== LIVE MONITOR COMPLETE ===")

if __name__ == "__main__":
    asyncio.run(main())
