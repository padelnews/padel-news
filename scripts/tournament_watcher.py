#!/usr/bin/env python3
"""
Padel News Tournament Watcher v2.0
===================================
Master orchestrator that:
1. Checks official Premier Padel for match times
2. Detects when matches start (enables live score)
3. Detects when tournament ends (triggers transition)
4. Manages state transitions

Runs: Every 5 minutes via launchd
"""

import requests
import json
import re
from datetime import datetime, timedelta
from pathlib import Path

# Paths
PADEL_DIR = Path("/Users/cristian/Sites/padel_news")
STATE_FILE = Path("/Users/cristian/.openclaw/workspace/tournament_state.json")
LOG_FILE = Path("/Users/cristian/.openclaw/workspace/tournament_watcher.log")
ARTICLE_DIR = PADEL_DIR / "articles"

PREMIER_PADEL_BASE = "https://premierpadel.com/es"

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
    except:
        return None

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def fetch_tournament_page(tournament_slug):
    """Fetch tournament page from Premier Padel."""
    url = f"{PREMIER_PADEL_BASE}/tournaments-results/{tournament_slug}"
    try:
        r = requests.get(url, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }, timeout=30)
        if r.status_code == 200:
            return r.text
    except Exception as e:
        log(f"Error fetching tournament page: {e}")
    return None

def extract_match_schedule(html):
    """Extract match schedule from tournament page."""
    matches = []
    
    # Look for schedule section
    schedule_section = re.search(r'(?:Schedule|Programa|Horario)(.*?)(?:</section>|</div>)', html, re.DOTALL | re.IGNORECASE)
    if not schedule_section:
        return matches
    
    text = schedule_section.group(1)
    
    # Extract time slots with phase info
    time_pattern = r'(\d{1,2}:\d{2})'
    phase_patterns = [
        (r'Final', 'final'),
        (r'Semifinal', 'semifinal'),
        (r'Quarter|Before| Round of |Cuartos', 'quarterfinal'),
        (r'First Round|Primera| Round of 32|Octavos', 'first_round')
    ]
    
    times = re.findall(time_pattern, text)
    for time in times:
        matches.append({'time': time, 'phase': 'unknown'})
    
    # Detect phase from context
    for match in matches:
        for pattern, phase in phase_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                match['phase'] = phase
                break
    
    return matches

def extract_results(html):
    """Extract match results from page."""
    results = {
        'matches': []
    }
    
    # Look for result patterns
    result_pattern = r'([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)\s*/\s*([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)[^0-9]*(\d{1,2}-\d{1,2}(?:,\s*\d{1,2}-\d{1,2})*)'
    matches = re.findall(result_pattern, html)
    
    for m in matches:
        results['matches'].append({
            'team1': f"{m[0]} / {m[1]}",
            'team2': None,
            'score': m[2]
        })
    
    return results

def check_match_in_progress(html):
    """Check if there's a match currently in progress."""
    # Look for LIVE indicator
    if re.search(r'(?:LIVE|En Vivo|DIRECTO|🔴)', html, re.IGNORECASE):
        return True
    return False

def get_next_match_time(html):
    """Get the next scheduled match time."""
    # Look for "Starting at" or similar text
    patterns = [
        r'(?:Starting at|Comienza a|Empieza a|Empieza|Starts?)\s*:?\s*(\d{1,2}:\d{2})',
        r'(\d{1,2}:\d{2})\s*(?:hrs?|hours?|h)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, html, re.IGNORECASE)
        if match:
            return match.group(1)
    
    return None

def should_enable_live_score(state, html):
    """Determine if live score should be enabled."""
    # Check state
    if state.get('live_score_active'):
        return True
    
    if state.get('status') == 'finished':
        return False
    
    # Check for live indicator
    if check_match_in_progress(html):
        return True
    
    # Check if next match time has arrived
    next_time = get_next_match_time(html)
    if next_time:
        try:
            hour, min = map(int, next_time.split(':'))
            now = datetime.now()
            match_time = now.replace(hour=hour, minute=min)
            
            # If within 10 minutes of match time
            if abs((now - match_time).total_seconds()) < 600:
                return True
        except:
            pass
    
    return False

def is_tournament_finished(html, state):
    """Check if tournament has finished."""
    # If we see final results with no more matches scheduled
    if 'Final' in html and re.search(r'Winner|Campeón|Ganador', html, re.IGNORECASE):
        # Check if there's an upcoming/next tournament
        if re.search(r'(?:Next|Próximo|Siguiente)\s+(?:Tournament|Torneo)', html, re.IGNORECASE):
            return True
    
    # Check state flag
    if state.get('status') == 'finished':
        return True
    
    return False

def create_summary_article(state, results):
    """Create summary article for finished tournament."""
    tournament_name = state.get('current_tournament', 'Tournament')
    tournament_id = state.get('tournament_id', 'unknown')
    
    # Extract final result
    final = None
    for m in results.get('matches', []):
        if 'final' in m.get('phase', '').lower():
            final = m
            break
    
    # Generate article filename
    article_filename = f"article-{tournament_id.lower().replace(' ', '-')}.html"
    article_path = ARTICLE_DIR / article_filename
    
    winner = final.get('winner', 'TBD') if final else 'TBD'
    score = final.get('score', 'N/A') if final else 'N/A'
    
    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{tournament_name} - Resumen | Padel News</title>
    <link rel="stylesheet" href="../css/style.css">
</head>
<body>
    <header>
        <span class="live-badge">🏆 {tournament_name} - FINALIZADO</span>
    </header>
    
    <main class="container">
        <h1>🏆 {tournament_name}</h1>
        
        <section class="summary-section">
            <h2>Resultados Finales</h2>
            <div class="final-result">
                <p class="champion"><strong>🏆 CAMPEONES:</strong> {winner}</p>
                <p class="score">Resultado: {score}</p>
            </div>
        </section>
        
        <section class="summary-section">
            <h2>Resumen del Torneo</h2>
            <p>Torneo completado exitosamente. Consulta los resultados completos en la página de resultados.</p>
        </section>
        
        <a href="../resultados.html" class="btn btn-primary">Ver Resultados Completos →</a>
    </main>
</body>
</html>
"""
    
    with open(article_path, 'w') as f:
        f.write(html)
    
    log(f"Created summary: {article_path}")
    return str(article_path)

def update_pages_with_final_state(state, results):
    """Update all pages when tournament finishes."""
    tournament_name = state.get('current_tournament')
    article_url = state.get('last_summary_url', '#')
    
    pages = ['index.html', 'actualidad.html', 'resultados.html', 'torneos.html']
    
    for page in pages:
        page_path = PADEL_DIR / page
        try:
            with open(page_path, 'r') as f:
                content = f.read()
            
            # Update banner
            content = re.sub(
                r'<span class="live-badge">[^<]*</span>',
                f'<span class="live-badge">🏆 {tournament_name} - FINALIZADO</span>',
                content
            )
            
            # Remove live score banner if exists
            content = re.sub(r'<div class="live-score-banner">.*?</div>\s*', '', content, flags=re.DOTALL)
            
            with open(page_path, 'w') as f:
                f.write(content)
            
            log(f"Updated {page}")
        except Exception as e:
            log(f"Error updating {page}: {e}")

def transition_to_next_tournament(state, next_tournament):
    """Transition to next tournament."""
    log(f"Transitioning to: {next_tournament.get('name')}")
    
    # Save current to past
    past = {
        'id': state.get('tournament_id'),
        'name': state.get('current_tournament'),
        'dates': state.get('dates', ''),
        'location': state.get('location', ''),
        'status': 'completed'
    }
    state['past_tournaments'] = state.get('past_tournaments', [])
    state['past_tournaments'].append(past)
    
    # Set new current
    state['current_tournament'] = next_tournament.get('name')
    state['tournament_id'] = next_tournament.get('id')
    state['tournament_url'] = next_tournament.get('url', '')
    state['phase'] = 'first_round'
    state['status'] = 'upcoming'
    state['live_score_active'] = False
    state['final_result'] = None
    
    save_state(state)
    
    # Update all pages
    update_pages_for_new_tournament(state)

def update_pages_for_new_tournament(state):
    """Update pages for new tournament."""
    tournament_name = state.get('current_tournament')
    
    pages = ['index.html', 'actualidad.html', 'resultados.html', 'torneos.html']
    
    for page in pages:
        page_path = PADEL_DIR / page
        try:
            with open(page_path, 'r') as f:
                content = f.read()
            
            # Update banner
            content = re.sub(
                r'<span class="live-badge">[^<]*</span>',
                f'<span class="live-badge">🏆 {tournament_name} - PRÓXIMO</span>',
                content
            )
            
            with open(page_path, 'w') as f:
                f.write(content)
        except:
            pass
    
    log(f"Updated pages for new tournament: {tournament_name}")

def add_finished_tournament_to_actualidad(state):
    """Add finished tournament to actualidad page as summary section."""
    if not state.get('past_tournaments'):
        return
    
    last_tournament = state['past_tournaments'][-1]
    
    article_html = f'''
        <article class="news-card" style="margin-bottom: 2rem;">
            <div class="news-card-image">
                <img src="../images/tournament-summary.jpg" alt="{last_tournament.get('name')}">
                <span class="news-card-category">🏆 FINALIZADO</span>
            </div>
            <div class="news-card-content">
                <h3><a href="../{last_tournament.get('article_url', '#')}">{last_tournament.get('name')}</a></h3>
                <p>Consulta el resumen y resultados completos del torneo.</p>
                <div class="news-card-meta">
                    <span class="news-card-date">📅 {last_tournament.get('dates', '')}</span>
                    <span class="news-card-date">📍 {last_tournament.get('location', '')}</span>
                </div>
                <a href="../{last_tournament.get('article_url', 'resultados.html')}" class="btn btn-primary" style="margin-top: 1rem;">Ver Resumen →</a>
            </div>
        </article>
    '''
    
    # Add to actualidad.html before closing main tag
    page_path = PADEL_DIR / "actualidad.html"
    try:
        with open(page_path, 'r') as f:
            content = f.read()
        
        content = content.replace('</main>', f'{article_html}</main>')
        
        with open(page_path, 'w') as f:
            f.write(content)
        
        log("Added finished tournament to actualidad")
    except Exception as e:
        log(f"Error updating actualidad: {e}")

def update_torneos_page(state):
    """Update torneos page to show finished tournament in past section."""
    past_tournaments = state.get('past_tournaments', [])
    if not past_tournaments:
        return
    
    past_section = ""
    for t in past_tournaments:
        past_section += f'''
            <div class="tournament-item past">
                <span class="tournament-name">✅ {t.get('name', 'Tournament')}</span>
                <span class="tournament-dates">{t.get('dates', '')}</span>
                <span class="tournament-status">Finalizado</span>
            </div>
        '''
    
    # Add to torneos.html
    page_path = PADEL_DIR / "torneos.html"
    try:
        with open(page_path, 'r') as f:
            content = f.read()
        
        # Find past tournaments section and add to it
        content = re.sub(r'(<div id="past-tournaments">)(.*?)(</div>)', 
                        f'\\1\\2{past_section}\\3', content, flags=re.DOTALL)
        
        with open(page_path, 'w') as f:
            f.write(content)
        
        log("Updated torneos page with past tournament")
    except Exception as e:
        log(f"Error updating torneos: {e}")

def main():
    log("=== Tournament Watcher v2.0 Started ===")
    
    state = load_state()
    if not state:
        log("No state - initializing")
        state = {
            'current_tournament': 'Brussels P2 2026',
            'tournament_id': 'brussels-p2',
            'status': 'pending_final',
            'live_score_active': False,
            'past_tournaments': []
        }
        save_state(state)
    
    tournament_slug = state.get('tournament_id', 'brussels-p2')
    
    # Fetch current tournament page
    html = fetch_tournament_page(tournament_slug)
    
    if not html:
        log("Could not fetch tournament page")
        return
    
    # Check if should enable live score
    if should_enable_live_score(state, html):
        if not state.get('live_score_active'):
            state['live_score_active'] = True
            save_state(state)
            log("🔴 LIVE SCORE ENABLED")
            
            # Update pages with live banner
            for page in ['index.html', 'actualidad.html', 'resultados.html']:
                page_path = PADEL_DIR / page
                try:
                    with open(page_path, 'r') as f:
                        content = f.read()
                    
                    banner = '<div class="live-score-banner"><span class="live-score-text">🔴 EN DIRECTO - Brussels P2 2026 - Final</span></div>'
                    content = content.replace('</header>', f'</header>{banner}')
                    
                    with open(page_path, 'w') as f:
                        f.write(content)
                except:
                    pass
    else:
        if state.get('live_score_active'):
            state['live_score_active'] = False
            save_state(state)
            log("Live score disabled")
    
    # Check if tournament is finished
    if is_tournament_finished(html, state):
        log("🏆 TOURNAMENT FINISHED")
        
        # Extract results
        results = extract_results(html)
        
        # Create summary article
        article_path = create_summary_article(state, results)
        state['last_summary_url'] = article_path
        
        # Update state
        state['status'] = 'finished'
        save_state(state)
        
        # Update all pages
        update_pages_with_final_state(state, results)
        
        # Add to actualidad
        add_finished_tournament_to_actualidad(state)
        
        # Update torneos page
        update_torneos_page(state)
        
        log("Tournament transition completed")
    
    log("=== Tournament Watcher Completed ===")

if __name__ == "__main__":
    main()