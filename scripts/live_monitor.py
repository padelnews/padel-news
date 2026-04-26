#!/usr/bin/env python3
"""
Live Match Monitor - FIXED VERSION
Extracts correct data from premierpadel match center
"""
import asyncio
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright

PADEL_DIR = Path("/Users/cristian/Sites/padel_news")
LOG_FILE = Path("/Users/cristian/.openclaw/workspace/dynamic_flow.log")

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def update_website(team1, set1_t1, set2_t1, set3_t1, game1,
                  team2, set1_t2, set2_t2, set3_t2, game2):
    try:
        with open(PADEL_DIR / "index.html", 'r') as f:
            content = f.read()
        
        scoreboard = f'''<span class="live-badge">
<table style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); border-radius: 10px; padding: 8px 12px; display: inline-table; vertical-align: middle; margin: 5px 0; border: 2px solid #f39c12;">
<tr style="color: white; font-family: Arial, sans-serif; font-size: 13px;">
<td style="padding: 6px 15px; border-right: 1px solid #555;">{team1}</td>
<td style="padding: 6px 12px; text-align: center; background: #c0392b; color: white; font-weight: bold; border-right: 1px solid #888;">{set1_t1}</td>
<td style="padding: 6px 12px; text-align: center; background: #c0392b; color: white; font-weight: bold; border-right: 1px solid #888;">{set2_t1}</td>
<td style="padding: 6px 12px; text-align: center; background: #f39c12; color: #1a1a2e; font-weight: bold;">{set3_t1}</td>
</tr>
<tr style="color: white; font-family: Arial, sans-serif; font-size: 13px;">
<td style="padding: 6px 15px; border-right: 1px solid #555;">{team2}</td>
<td style="padding: 6px 12px; text-align: center; background: #c0392b; color: white; font-weight: bold; border-right: 1px solid #888;">{set1_t2}</td>
<td style="padding: 6px 12px; text-align: center; background: #c0392b; color: white; font-weight: bold; border-right: 1px solid #888;">{set2_t2}</td>
<td style="padding: 6px 12px; text-align: center; background: #f39c12; color: #1a1a2e; font-weight: bold;">{set3_t2}</td>
</tr>
</table>
</span>'''
        
        import re
        h_start = content.find('<header>')
        h_end = content.find('</header>') + 9
        header = content[h_start:h_end]
        
        clean = re.sub(r'<span class="live-badge".*?</span>', '', header, flags=re.DOTALL)
        tagline_end = clean.find('</p>')
        before = clean[:tagline_end + 4]
        after = clean[tagline_end + 4:]
        new_header = before + '\n            ' + scoreboard + after
        
        new_content = content[:h_start] + new_header + content[h_end:]
        
        with open(PADEL_DIR / "index.html", 'w') as f:
            f.write(new_content)
        
        log(f"Updated: {team1} {set1_t1}-{set2_t1}-{set3_t1} ({game1}) vs {team2} {set1_t2}-{set2_t2}-{set3_t2} ({game2})")
        
    except Exception as e:
        log(f"Error: {e}")

async def check_match():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            await page.goto("https://premierpadel.com/es/matchcenter/6365", timeout=30000)
            await asyncio.sleep(15)
            
            body = await page.inner_text("body")
            
            if "TAPIA" in body and "LEBRON" in body:
                tapia_pos = body.find("TAPIA")
                lebron_pos = body.find("LEBRON")
                
                # Get section from TAPIA to LEBRON
                section = body[tapia_pos:lebron_pos+200]
                lines = section.split('\n')
                
                # Get ALL digit lines
                all_digits = []
                for line in lines:
                    stripped = line.strip()
                    if stripped.isdigit() or stripped == 'Ad':
                        all_digits.append(stripped)
                
                log(f"All digits: {all_digits}")
                
                # Pattern from match center:
                # TAPIA: game, set1, set2, set3
                # LEBRON: game, set1, set2, set3
                
                if len(all_digits) >= 8:
                    # First 4 digits = TAPIA [game, set1, set2, set3]
                    # Next 4 digits = LEBRON [game, set1, set2, set3]
                    
                    tapia_game = all_digits[0]
                    tapia_set1 = all_digits[1]
                    tapia_set2 = all_digits[2]
                    tapia_set3 = all_digits[3]
                    
                    lebron_game = all_digits[4]
                    lebron_set1 = all_digits[5]
                    lebron_set2 = all_digits[6]
                    lebron_set3 = all_digits[7]
                    
                    update_website(
                        "TAPIA / COELLO", tapia_set1, tapia_set2, tapia_set3, tapia_game,
                        "LEBRON / AUGSBURGER", lebron_set1, lebron_set2, lebron_set3, lebron_game
                    )
                else:
                    log(f"Not enough digits: {all_digits}")
                    
        except Exception as e:
            log(f"Error: {e}")
        
        await browser.close()

if __name__ == "__main__":
    log("=== LIVE MONITOR STARTED ===")
    asyncio.run(check_match())
    log("=== COMPLETE ===")