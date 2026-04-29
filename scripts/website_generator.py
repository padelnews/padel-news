#!/usr/bin/env python3
"""
Padel News Website Generator v2.0
================================
Generates ALL website pages from tournament_state.json

This is the ONLY way pages should be modified.
No direct HTML edits - everything comes from the state.

Usage:
    python3 website_generator.py              # Generate all pages
    python3 website_generator.py --dry-run    # Preview without writing
    python3 website_generator.py --verify     # Verify after generation
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# Configuration
PADEL_DIR = Path("/Users/cristian/Sites/padel_news")
STATE_FILE = PADEL_DIR / "scripts" / "tournament_state.json"
LOG_FILE = PADEL_DIR / "scripts" / "generation.log"

# HTML Templates
TEMPLATE_HEADER = '''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="description" content="{description}">
    <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🎾</text></svg>">
    <link href="https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&family=Orbitron:wght@700;900&display=swap" rel="stylesheet">
    <style>
        :root {{
            --primary: #00d4ff;
            --accent: #bf00ff;
            --bg-dark: #0a0a0f;
            --glass-bg: rgba(26, 26, 46, 0.8);
            --glass-border: rgba(0, 212, 255, 0.3);
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Rajdhani', sans-serif; background: var(--bg-dark); color: #fff; line-height: 1.6; }}
        header {{ background: linear-gradient(135deg, #0a0a0f, #1a1a2e); padding: 2rem 1rem; border-bottom: 2px solid var(--primary); text-align: center; }}
        header h1 {{ font-family: 'Orbitron', sans-serif; font-size: 2.5rem; background: linear-gradient(90deg, var(--primary), var(--accent)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0.5rem; }}
        header p {{ opacity: 0.8; margin-bottom: 1rem; }}
        .live-badge {{ display: inline-block; background: linear-gradient(135deg, var(--primary), var(--accent)); color: #000; padding: 0.5rem 1.5rem; border-radius: 20px; font-weight: 700; }}
        nav {{ background: rgba(0,0,0,0.5); padding: 1rem; text-align: center; }}
        nav ul {{ list-style: none; display: flex; justify-content: center; gap: 2rem; flex-wrap: wrap; padding: 0; }}
        nav a {{ color: #fff; text-decoration: none; padding: 0.5rem 1rem; border-radius: 8px; }}
        nav a:hover, nav a.active {{ background: var(--primary); color: #000; }}
        main {{ max-width: 1200px; margin: 0 auto; padding: 2rem; }}
        .section-title {{ font-family: 'Orbitron', sans-serif; font-size: 1.5rem; color: var(--primary); margin-bottom: 1.5rem; text-align: center; }}
        .hero {{ background: linear-gradient(135deg, rgba(0, 212, 255, 0.1), rgba(191, 0, 255, 0.1)); padding: 3rem; border-radius: 20px; margin-bottom: 3rem; border: 1px solid var(--glass-border); }}
        .hero h2 {{ font-family: 'Orbitron', sans-serif; font-size: 2rem; margin-bottom: 1rem; }}
        .hero p {{ font-size: 1.2rem; opacity: 0.9; margin-bottom: 1.5rem; }}
        .btn {{ display: inline-block; color: var(--primary); text-decoration: none; margin-top: 1rem; }}
        .btn-primary {{ background: linear-gradient(135deg, var(--primary), var(--accent)); color: #000; padding: 0.8rem 2rem; border-radius: 8px; text-decoration: none; font-weight: 700; }}
        .results-table {{ width: 100%; border-collapse: collapse; background: var(--glass-bg); border-radius: 12px; overflow: hidden; }}
        .results-table th {{ background: rgba(0, 212, 255, 0.2); padding: 1rem; text-align: left; font-weight: 600; }}
        .results-table td {{ padding: 0.8rem 1rem; border-bottom: 1px solid rgba(255,255,255,0.1); }}
        .winner {{ color: var(--primary); font-weight: 600; }}
        .tournament-badge {{ display: inline-block; padding: 0.3rem 0.8rem; border-radius: 12px; font-size: 0.85rem; }}
        .score {{ font-weight: 600; }}
        .calendar-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1.5rem; }}
        .tournament-card {{ background: var(--glass-bg); border: 1px solid var(--glass-border); border-radius: 12px; padding: 1.5rem; }}
        .tournament-card h4 {{ color: var(--primary); margin-bottom: 0.5rem; }}
        .status-badge {{ display: inline-block; padding: 0.3rem 0.8rem; border-radius: 12px; font-size: 0.85rem; font-weight: 700; }}
        .status-upcoming {{ background: rgba(0, 255, 136, 0.3); color: #00ff88; }}
        .news-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 2rem; }}
        .news-card {{ background: var(--glass-bg); border: 1px solid var(--glass-border); border-radius: 12px; overflow: hidden; transition: transform 0.3s ease; }}
        .news-card:hover {{ transform: translateY(-5px); border-color: var(--primary); }}
        .news-card-image {{ height: 180px; background: linear-gradient(135deg, rgba(0, 212, 255, 0.2), rgba(191, 0, 255, 0.2)); display: flex; align-items: center; justify-content: center; font-size: 3rem; }}
        .news-card-content {{ padding: 1.5rem; }}
        .news-card-category {{ display: inline-block; background: rgba(0, 212, 255, 0.2); color: var(--primary); padding: 0.3rem 0.8rem; border-radius: 12px; font-size: 0.85rem; margin-bottom: 1rem; }}
        .news-card h3 {{ font-size: 1.2rem; margin-bottom: 0.8rem; line-height: 1.3; }}
        .news-card h3 a {{ color: #fff; text-decoration: none; }}
        .news-card h3 a:hover {{ color: var(--primary); }}
        .news-card p {{ color: #aaa; font-size: 0.95rem; margin-bottom: 1rem; }}
        .news-card-meta {{ display: flex; gap: 1rem; font-size: 0.85rem; color: #888; margin-bottom: 1rem; flex-wrap: wrap; }}
        .news-card-meta span {{ display: flex; align-items: center; gap: 0.3rem; }}
        footer {{ text-align: center; padding: 2rem; color: #666; }}
        @media (max-width: 768px) {{ .section-title {{ font-size: 1.2rem; }} }}
    </style>
</head>
<body>
    <header>
        <h1>🎾 Padel News Pro</h1>
        <p>Tu portal profesional del Premier Padel Tour 2026</p>
        <span class="live-badge">{banner}</span>
    </header>
    <nav>
        <ul>
            <li><a href="index.html">Inicio</a></li>
            <li><a href="actualidad.html">Actualidad</a></li>
            <li><a href="resultados.html">Resultados</a></li>
            <li><a href="torneos.html">Torneos</a></li>
            <li><a href="chollos.html">Chollos 🏷️</a></li>
        </ul>
    </nav>
    <main>
'''

TEMPLATE_FOOTER = '''
    </main>
    <footer>
        <p>© 2026 Padel News Pro | Actualizado: {timestamp}</p>
    </footer>
</body>
</html>'''


def log(msg: str, verbose: bool = True):
    """Log message to file and optionally console."""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")
    if verbose or "--verbose" in sys.argv:
        print(line)


def load_state() -> Dict:
    """Load tournament state from JSON file."""
    try:
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        log(f"ERROR loading state: {e}")
        return {}


def save_state(state: Dict) -> bool:
    """Save state to JSON file."""
    try:
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        log(f"ERROR saving state: {e}")
        return False


def flag(emoji: str, text: str) -> str:
    """Generate flag emoji + text."""
    return f"{emoji} {text}"


def get_current_banner(state: Dict) -> str:
    """Generate banner text based on current state."""
    current = state.get("current_tournament", {})
    status = current.get("status", "unknown")
    
    if status == "live":
        return f"🔴 EN VIVO - {current.get('name', 'Torneo')}"
    elif status == "upcoming":
        return f"🎾 PRÓXIMO - {current.get('name', 'Torneo')} ({current.get('dates', '')})"
    elif status == "finished":
        winner = state.get("past_tournaments", [{}])[0].get("winner_male", [])
        return f"✅ FINALIZADO - {current.get('name', 'Torneo')} | {'/'.join(winner)} 🏆"
    else:
        return "🏆 Padel News Pro 2026"


def generate_index(state: Dict) -> str:
    """Generate index.html from state."""
    log("Generating index.html...")
    
    current = state.get("current_tournament", {})
    past = state.get("past_tournaments", [])[:6]  # Last 6 tournaments
    upcoming = state.get("upcoming_tournaments", [])[:4]  # Next 4 tournaments
    
    # Build results table rows
    results_rows = ""
    for t in past:
        winner = t.get("winner_male", [])
        finalists = t.get("finalists_male", [])
        flag_map = {"Lebrón": "🇪🇸", "Augsburger": "🇦🇷", "Tapia": "🇪🇸", "Coello": "🇦🇷", 
                   "Galán": "🇪🇸", "Chingotto": "🇦🇷", "Stupaczuk": "🇦🇷", "Yanguas": "🇪🇸"}
        w_flags = "".join([flag_map.get(p, "🏳️") for p in winner])
        f_flags = "".join([flag_map.get(p, "🏳️") for p in finalists])
        
        # Location flag
        loc_flags = {"Bruselas": "🇧🇪", "El Gouna": "🇪🇬", "Miami": "🇺🇸", "Cancún": "🇲🇽", 
                    "Gijón": "🇪🇸", "Riad": "🇸🇦"}
        loc = t.get("location", "")
        loc_flag = loc_flags.get(loc.split(",")[0].strip(), "🏳️")
        
        results_rows += f'''
                        <tr>
                            <td><span class="tournament-badge">{loc_flag} {t.get('name', '')}</span></td>
                            <td class="winner">{w_flags} {' / '.join(winner)}</td>
                            <td><span class="score">{t.get('final_score', '')}</span></td>
                            <td>{f_flags} {' / '.join(finalists)}</td>
                        </tr>'''
    
    # Build upcoming tournaments cards
    upcoming_cards = ""
    for t in upcoming[:3]:
        loc = t.get("location", "")
        loc_flag = {"Asunción": "🇵🇾", "Buenos Aires": "🇦🇷", "Roma": "🇮🇹"}.get(loc.split(",")[0].strip(), "🏳️")
        status_class = "status-upcoming" if t.get("status") == "upcoming" else "status-ongoing"
        status_text = "PRÓXIMO" if t.get("status") == "upcoming" else "EN CURSO"
        prize = t.get("prize_money", "€200,000")
        
        upcoming_cards += f'''
                <div class="tournament-card upcoming">
                    <div class="tournament-header">
                        <span class="status-badge {status_class}">{status_text}</span>
                        <h4>{loc_flag} {t.get('name', '')}</h4>
                    </div>
                    <p class="tournament-date">{t.get('dates', '')}</p>
                    <p class="tournament-location">{t.get('location', '')}</p>
                    <p class="tournament-prize">💰 {prize}</p>
                </div>'''
    
    banner = get_current_banner(state)
    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    html = f'''{TEMPLATE_HEADER.format(
        title="Padel News Pro | Premier Padel Tour 2026",
        description="Tu portal profesional del Premier Padel Tour 2026. Noticias, resultados y rankings.",
        banner=banner
    )}

        <!-- Hero Section -->
        <section class="hero" style="background: linear-gradient(135deg, rgba(0, 212, 255, 0.1), rgba(191, 0, 255, 0.1)); padding: 3rem; border-radius: 20px; margin-bottom: 3rem; border: 1px solid var(--glass-border);">
            <div class="hero-content">
                <h2 style="font-family: 'Orbitron', sans-serif; font-size: 2rem; margin-bottom: 1rem;">
                    {current.get('name', 'Próximo Torneo')} - {'EN CURSO' if current.get('status') == 'live' else current.get('status', '').upper()}
                </h2>
                <p style="font-size: 1.2rem; opacity: 0.9; margin-bottom: 1.5rem;">
                    {f"Sigue en directo los mejores partidos de pádel profesional. {current.get('dates', '')} - {current.get('location', '')}" if current.get('status') == 'live' else f"Información y resultados del {current.get('name', 'torneo')}."}
                </p>
                <a href="resultados.html" class="btn btn-primary" style="background: linear-gradient(135deg, var(--primary), var(--accent)); color: #000; padding: 0.8rem 2rem; border-radius: 8px; text-decoration: none; font-weight: 700;">Ver Resultados</a>
            </div>
        </section>

        <!-- Results Section -->
        <section style="margin-bottom: 3rem;">
            <h2 class="section-title">🏆 Resultados Recientes</h2>
            <div class="table-scroll-wrapper">
                <table class="results-table">
                    <thead>
                        <tr>
                            <th>Torneo</th>
                            <th>Campeones</th>
                            <th>Resultado</th>
                            <th>Finalistas</th>
                        </tr>
                    </thead>
                    <tbody>
                        {results_rows}
                    </tbody>
                </table>
            </div>
            <a href="resultados.html" class="btn" style="margin-top: 1rem; display: inline-block; color: var(--primary);">Ver Todos los Resultados →</a>
        </section>

        <!-- Upcoming Tournaments -->
        <section style="margin-bottom: 3rem;">
            <h2 class="section-title">📅 Próximos Torneos</h2>
            <div class="calendar-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1.5rem;">
                {upcoming_cards}
            </div>
            <a href="torneos.html" class="btn" style="margin-top: 1rem; display: inline-block; color: var(--primary);">Ver Calendario Completo →</a>
        </section>
{TEMPLATE_FOOTER.format(timestamp=timestamp)}'''
    
    return html


def generate_resultados(state: Dict) -> str:
    """Generate resultados.html from state."""
    log("Generating resultados.html...")
    
    past = state.get("past_tournaments", [])
    current = state.get("current_tournament", {})
    upcoming = state.get("upcoming_tournaments", [])
    
    # Build sections for each tournament
    tournament_sections = ""
    
    # Upcoming first
    if upcoming:
        t = upcoming[0]
        tournament_sections += f'''
        <!-- PRÓXIMO TORNEO -->
        <section style="margin-bottom: 3rem;">
            <div style="background: linear-gradient(135deg, rgba(0, 255, 136, 0.15), rgba(0, 212, 255, 0.15)); border: 1px solid rgba(0, 255, 136, 0.3); padding: 2.5rem; border-radius: 20px; margin-bottom: 2rem;">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
                    <div>
                        <span class="badge" style="background: rgba(0, 255, 136, 0.2); color: #00ff88;">🎾 PRÓXIMO</span>
                        <h3 style="font-size: 1.8rem; margin: 0.5rem 0;">{t.get('name', '')}</h3>
                        <p style="opacity: 0.9;">📅 {t.get('dates', '')} • {t.get('location', '')}</p>
                    </div>
                    <div style="text-align: right;">
                        <p style="font-size: 0.9rem; opacity: 0.8;">Estado</p>
                        <p style="font-size: 1.3rem; font-weight: 700;">⏳ PENDIENTE</p>
                    </div>
                </div>
            </div>
        </section>'''
    
    # Past tournaments
    for t in past:
        winner_m = t.get("winner_male", [])
        finalists_m = t.get("finalists_male", [])
        semis = t.get("semifinals_male", [])
        loc = t.get("location", "")
        loc_flag = {"Bruselas": "🇧🇪", "El Gouna": "🇪🇬", "Miami": "🇺🇸", "Cancún": "🇲🇽", 
                   "Gijón": "🇪🇸", "Riad": "🇸🇦"}.get(loc.split(",")[0].strip(), "🏳️")
        
        # Build semifinals rows
        semis_rows = ""
        for s in semis:
            teams = s.get("teams", [])
            if len(teams) >= 4:
                semis_rows += f'''
                        <tr>
                            <td>Semifinal</td>
                            <td class="winner">{' / '.join(teams[:2])}</td>
                            <td>{s.get('score', '')}</td>
                            <td>{' / '.join(teams[2:])}</td>
                        </tr>'''
        
        tournament_sections += f'''
        <!-- {t.get('name', '')} -->
        <section style="margin-bottom: 3rem;">
            <div style="background: rgba(26, 26, 46, 0.8); border: 1px solid var(--glass-border); padding: 2rem; border-radius: 16px; margin-bottom: 1.5rem;">
                <span class="badge" style="background: rgba(100,100,100,0.3); color: #ccc;">✅ Finalizado</span>
                <h3 style="font-size: 1.5rem; margin: 0.5rem 0; color: var(--primary);">{loc_flag} {t.get('name', '')}</h3>
                <p style="opacity: 0.8;">📅 {t.get('dates', '')} • {t.get('location', '')}</p>
            </div>
            
            <div style="background: linear-gradient(135deg, rgba(191, 0, 255, 0.3), rgba(0, 212, 255, 0.3)); border: 2px solid var(--accent); border-radius: 16px; padding: 2rem; text-align: center; margin: 1.5rem 0;">
                <h3 style="color: white; margin-bottom: 1rem;">🏆 CAMPEONES</h3>
                <p style="font-size: 1.8rem; font-weight: 700; color: var(--primary);">{' / '.join(winner_m)}</p>
                <p style="font-size: 1.5rem; color: white; margin: 0.5rem 0;">{t.get('final_score', '')}</p>
                <p style="color: #888;">vs {' / '.join(finalists_m)}</p>
            </div>
            
            <h4 style="color: var(--primary); margin: 2rem 0 1rem;">📊 Cuadro</h4>
            <div class="table-scroll-wrapper">
                <table class="results-table">
                    <thead>
                        <tr><th>Ronda</th><th>Pareja 1</th><th>Resultado</th><th>Pareja 2</th></tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><strong>Final</strong></td>
                            <td class="winner">{' / '.join(winner_m)}</td>
                            <td>{t.get('final_score', '')}</td>
                            <td>{' / '.join(finalists_m)}</td>
                        </tr>
                        {semis_rows}
                    </tbody>
                </table>
            </div>
        </section>'''
    
    banner = get_current_banner(state)
    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    html = f'''{TEMPLATE_HEADER.format(
        title="Resultados Premier Padel 2026 | Padel News Pro",
        description="Todos los resultados del Premier Padel Tour 2026.",
        banner=banner
    )}

        <h2 class="section-title">🏆 Resultados Qatar Airways Premier Padel Tour 2026</h2>
        
        {tournament_sections}
{TEMPLATE_FOOTER.format(timestamp=timestamp)}'''
    
    return html


def generate_torneos(state: Dict) -> str:
    """Generate torneos.html from state."""
    log("Generating torneos.html...")
    
    past = state.get("past_tournaments", [])
    upcoming = state.get("upcoming_tournaments", [])
    
    # Build calendar rows
    all_tournaments = []
    
    # Add upcoming first
    for t in upcoming:
        all_tournaments.append({
            "name": t.get("name", ""),
            "location": t.get("location", ""),
            "dates": t.get("dates", ""),
            "status": "upcoming",
            "is_next": True
        })
    
    # Add past
    for t in past:
        all_tournaments.append({
            "name": t.get("name", ""),
            "location": t.get("location", ""),
            "dates": t.get("dates", ""),
            "status": "finished",
            "winner": "/".join(t.get("winner_male", []))
        })
    
    # Sort: upcoming first (by date), then past (by date desc)
    # For now just upcoming then past
    
    calendar_rows = ""
    for t in upcoming:
        loc = t.get("location", "")
        loc_flag = {"Asunción": "🇵🇾", "Buenos Aires": "🇦🇷", "Roma": "🇮🇹"}.get(loc.split(",")[0].strip(), "🏳️")
        calendar_rows += f'''
                        <tr>
                            <td><strong>{t.get('dates', '')}</strong></td>
                            <td>{t.get('name', '')}</td>
                            <td>{loc_flag} {loc}</td>
                            <td><span class="badge" style="background: rgba(0, 255, 136, 0.2); color: #00ff88;">🎾 PRÓXIMO</span></td>
                        </tr>'''
    
    for t in past[:6]:
        loc = t.get("location", "")
        loc_flag = {"Bruselas": "🇧🇪", "El Gouna": "🇪🇬", "Miami": "🇺🇸", "Cancún": "🇲🇽", 
                   "Gijón": "🇪🇸", "Riad": "🇸🇦"}.get(loc.split(",")[0].strip(), "🏳️")
        calendar_rows += f'''
                        <tr>
                            <td><strong>{t.get('dates', '')}</strong></td>
                            <td><strong>{t.get('name', '')}</strong></td>
                            <td>{loc_flag} {loc}</td>
                            <td><span class="badge" style="background: rgba(100,100,100,0.3);">✅ Finalizado</span></td>
                        </tr>'''
    
    # Build next tournament card
    next_t = upcoming[0] if upcoming else {}
    next_card = ""
    if next_t:
        loc = next_t.get("location", "")
        loc_flag = {"Asunción": "🇵🇾", "Buenos Aires": "🇦🇷", "Roma": "🇮🇹"}.get(loc.split(",")[0].strip(), "🏳️")
        next_card = f'''
                <div class="tournament-card" style="background: linear-gradient(135deg, rgba(0, 255, 136, 0.2), rgba(0, 212, 255, 0.2)); border: 2px solid var(--primary);">
                    <div class="tournament-header">
                        <span class="status-badge status-upcoming">🎾 PRÓXIMO</span>
                        <h4>{loc_flag} {next_t.get('name', '')}</h4>
                    </div>
                    <p class="tournament-date">{next_t.get('dates', '')}</p>
                    <p class="tournament-location">{next_t.get('location', '')}</p>
                    <p class="tournament-prize">💰 {next_t.get('prize_money', '€264,534')}</p>
                </div>'''
    
    banner = get_current_banner(state)
    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    html = f'''{TEMPLATE_HEADER.format(
        title="Torneos y Calendario Premier Padel 2026 | Padel News Pro",
        description="Calendario completo del Premier Padel Tour 2026.",
        banner=banner
    )}

        <h2 class="section-title">📋 Calendario Oficial Qatar Airways Premier Padel Tour 2026</h2>
        
        <!-- Next Tournament -->
        <section style="margin-bottom: 3rem;">
            <h3 style="color: var(--primary); margin-bottom: 1.5rem;">🎾 Siguiente Torneo</h3>
            <div class="calendar-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1.5rem;">
                {next_card}
            </div>
        </section>

        <!-- Calendar Table -->
        <section style="margin-bottom: 3rem;">
            <h3 style="color: var(--primary); margin-bottom: 1.5rem;">📅 Calendario Completo</h3>
            <div class="table-scroll-wrapper">
                <table class="results-table">
                    <thead>
                        <tr>
                            <th>Fecha</th>
                            <th>Torneo</th>
                            <th>Ubicación</th>
                            <th>Estado</th>
                        </tr>
                    </thead>
                    <tbody>
                        {calendar_rows}
                    </tbody>
                </table>
            </div>
        </section>
{TEMPLATE_FOOTER.format(timestamp=timestamp)}'''
    
    return html


def generate_actualidad(state: Dict) -> str:
    """Generate actualidad.html from state."""
    log("Generating actualidad.html...")
    
    past = state.get("past_tournaments", [])
    current = state.get("current_tournament", {})
    upcoming = state.get("upcoming_tournaments", [])
    
    # Build all past tournaments as news cards
    past_cards = ""
    for t in past[:4]:  # Max 4 past tournaments
        winner_m = t.get("winner_male", [])
        article_url = t.get("article_url", "index.html")
        loc = t.get("location", "")
        loc_split = loc.split(",")[0].strip() if loc else ""
        loc_flag = {"Bruselas": "🇧🇪", "El Gouna": "🇪🇬", "Miami": "🇺🇸", "Cancún": "🇲🇽", 
                   "Gijón": "🇪🇸", "Riad": "🇸🇦"}.get(loc_split, "🏳️")
        
        past_cards += f'''
            <article class="news-card">
                <div class="news-card-image">{loc_flag}</div>
                <div class="news-card-content">
                    <span class="news-card-category">🏆 CAMPEONES</span>
                    <h3><a href="{article_url}">{t.get('name', '')}: {' y '.join(winner_m)} se proclaman campeones</a></h3>
                    <p>La pareja {' y '.join(winner_m)} victories en {t.get('name', '')} con un marcador de {t.get('final_score', '')}.</p>
                    <div class="news-card-meta">
                        <span>📅 {t.get('dates', '')}</span>
                        <span>📍 {t.get('location', '')}</span>
                    </div>
                    <a href="{article_url}" class="btn">Leer más →</a>
                </div>
            </article>'''
    
    # Build upcoming tournament card
    upcoming_card = ""
    if upcoming:
        next_t = upcoming[0]
        loc_split = next_t.get("location", "").split(",")[0].strip() if next_t.get("location") else ""
        loc_flag = {"Asunción": "🇵🇾", "Buenos Aires": "🇦🇷", "Roma": "🇮🇹"}.get(loc_split, "🏳️")
        upcoming_card = f'''
            <article class="news-card">
                <div class="news-card-image">{loc_flag}</div>
                <div class="news-card-content">
                    <span class="news-card-category">📅 PRÓXIMO</span>
                    <h3><a href="torneos.html">{next_t.get('name', '')}: El siguiente torneo del Premier Padel</a></h3>
                    <p>El próximo torneo se celebrará del {next_t.get('dates', '')} en {next_t.get('location', '')}.</p>
                    <div class="news-card-meta">
                        <span>📅 {next_t.get('dates', '')}</span>
                        <span>📍 {next_t.get('location', '')}</span>
                    </div>
                    <a href="torneos.html" class="btn">Ver torneo →</a>
                </div>
            </article>'''
    
    banner = get_current_banner(state)
    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    html = f'''{TEMPLATE_HEADER.format(
        title="Actualidad Padel 2026 | Padel News Pro",
        description="Noticias y actualidad del Premier Padel Tour 2026.",
        banner=banner
    )}

        <h2 class="section-title">📰 Últimas Noticias</h2>
        
        <div class="news-grid">
            {past_cards}
            {upcoming_card}
        </div>
{TEMPLATE_FOOTER.format(timestamp=timestamp)}'''
    
    return html


def verify_html(html: str, page_name: str) -> List[str]:
    """Verify HTML for common issues. Returns list of errors."""
    errors = []
    
    # Check basic structure
    if "<html" not in html:
        errors.append(f"{page_name}: Missing <html> tag")
    if "</html>" not in html:
        errors.append(f"{page_name}: Missing </html> closing tag")
    if "<body" not in html:
        errors.append(f"{page_name}: Missing <body> tag")
    if "</body>" not in html:
        errors.append(f"{page_name}: Missing </body> closing tag")
    
    # Check for unclosed tags - use regex to be more precise
    import re
    
    # Count actual td elements (not attributes)
    td_open = len(re.findall(r'<td[\s>\-]', html))
    td_close = len(re.findall(r'</td>', html))
    if td_open != td_close:
        errors.append(f"{page_name}: td elements mismatch ({td_open} open, {td_close} close)")
    
    tr_open = len(re.findall(r'<tr[\s>]', html))
    tr_close = len(re.findall(r'</tr>', html))
    if tr_open != tr_close:
        errors.append(f"{page_name}: tr elements mismatch ({tr_open} open, {tr_close} close)")
    
    th_open = len(re.findall(r'<th[\s>]', html))
    th_close = len(re.findall(r'</th>', html))
    if th_open != th_close:
        errors.append(f"{page_name}: th elements mismatch ({th_open} open, {th_close} close)")
    
    return errors
    
    return errors


def main():
    dry_run = "--dry-run" in sys.argv
    verify_only = "--verify" in sys.argv
    
    log(f"=== Website Generator v2.0 Started ===")
    log(f"Dry run: {dry_run}, Verify: {verify_only}")
    
    state = load_state()
    if not state:
        log("ERROR: Cannot load state file")
        sys.exit(1)
    
    # Generate all pages
    pages = {
        "index.html": generate_index(state),
        "resultados.html": generate_resultados(state),
        "torneos.html": generate_torneos(state),
        "actualidad.html": generate_actualidad(state),
    }
    
    if verify_only:
        # Just verify existing pages
        all_errors = []
        for page_name in pages.keys():
            page_path = PADEL_DIR / page_name
            if page_path.exists():
                with open(page_path, 'r') as f:
                    content = f.read()
                errors = verify_html(content, page_name)
                all_errors.extend(errors)
        
        if all_errors:
            log("VERIFICATION FAILED:")
            for e in all_errors:
                log(f"  - {e}")
            sys.exit(1)
        else:
            log("VERIFICATION PASSED - No errors found")
        return
    
    # Write pages
    all_errors = []
    for page_name, html in pages.items():
        page_path = PADEL_DIR / page_name
        
        # Verify before writing
        errors = verify_html(html, page_name)
        if errors:
            all_errors.extend(errors)
            continue
        
        if not dry_run:
            with open(page_path, 'w') as f:
                f.write(html)
            log(f"Generated: {page_name}")
        else:
            log(f"Dry run - would generate: {page_name}")
    
    if all_errors:
        log("ERRORS FOUND - Not writing files:")
        for e in all_errors:
            log(f"  - {e}")
        sys.exit(1)
    
    # Update generation timestamp in state
    state["last_generation"] = datetime.now().isoformat()
    state["generation_count"] = state.get("generation_count", 0) + 1
    if not dry_run:
        save_state(state)
    
    log(f"=== Generation Complete ({state['generation_count']} times) ===")


if __name__ == "__main__":
    main()
