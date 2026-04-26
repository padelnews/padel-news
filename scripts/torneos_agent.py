#!/usr/bin/env python3
"""
TORNEOS AGENT - Tournament Results Updater
==========================================

MISIÓN:
Actualizar automáticamente la página torneos.html con:
- Último torneo (en curso o terminado) con ganador
- Torneos terminados con sus ganadores
- Se ejecuta cada día a las 08:00 y 20:00

DATOS:
- Lee tournament_state.json
- Usa tournament_progress.json

OUTPUT:
- Actualiza torneos.html
- Commit + Push automático
"""

import json
from pathlib import Path
from datetime import datetime

PADEL_DIR = Path("/Users/cristian/Sites/padel_news")
DATA_DIR = PADEL_DIR / "data"
STATE_FILE = DATA_DIR / "tournament_state.json"
PROGRESS_FILE = DATA_DIR / "tournament_progress.json"
TORNEOS_FILE = PADEL_DIR / "torneos.html"


def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] TORNEOS_AGENT: {msg}")


def load_state():
    with open(STATE_FILE) as f:
        return json.load(f)


def generate_tournament_card(tournament, is_current=False):
    """Generar HTML para un torneo."""
    name = tournament.get("name", "Torneo")
    location = tournament.get("location", "")
    start = tournament.get("start_date", "")[:7] if tournament.get("start_date") else ""
    end = tournament.get("end_date", "")[5:] if tournament.get("end_date") else ""
    champions = tournament.get("champions", [])
    runner_up = tournament.get("runner_up", [])
    score = tournament.get("final_score_detailed", "")
    prize = tournament.get("prize", "")
    
    country_flags = {
        "Paraguay": "🇵🇾", "Argentina": "🇦🇷", "Italy": "🇮🇹", 
        "Spain": "🇪🇸", "Belgium": "🇧🇪", "Egypt": "🇪🇬",
        "Saudi Arabia": "🇸🇦", "Mexico": "🇲🇽", "USA": "🇺🇸",
        "Bélgica": "🇧🇪"
    }
    flag = country_flags.get(location, "🏆")
    
    # Si hay campeones, mostrar sección de ganador
    if champions:
        champ_names = " / ".join(champions)
        ru_names = " / ".join(runner_up) if runner_up else "TBD"
        
        return f'''
        <div style="background: linear-gradient(135deg, rgba(0,212,255,0.15), rgba(191,0,255,0.15)); border-radius: 16px; padding: 1.5rem; margin-bottom: 1rem; border: 1px solid var(--glass-border);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                <div>
                    <span style="background: #ffd700; color: #000; padding: 0.2rem 0.6rem; border-radius: 4px; font-size: 0.75rem; font-weight: 700;">🏆 {name}</span>
                    <span style="margin-left: 0.5rem; color: var(--gray);">{flag} {location}</span>
                </div>
                <span style="color: var(--gray); font-size: 0.85rem;">{start}</span>
            </div>
            <div style="text-align: center; padding: 1rem; background: rgba(0,0,0,0.2); border-radius: 12px;">
                <div style="color: var(--primary); font-size: 0.8rem; margin-bottom: 0.5rem;">CAMPEONES</div>
                <div style="font-size: 1.3rem; font-weight: 700; color: #ffd700;">{champ_names}</div>
                <div style="color: var(--gray); font-size: 0.85rem; margin-top: 0.5rem;">vs {ru_names}</div>
                <div style="margin-top: 0.5rem; font-size: 1.1rem; color: var(--primary);">{score}</div>
            </div>
        </div>'''
    else:
        # Torneo próximo
        return f'''
        <div style="background: var(--glass-bg); padding: 1.2rem; border-radius: 12px; border-left: 3px solid var(--primary);">
            <div style="font-weight: 700; margin-bottom: 0.3rem;">{flag} {name}</div>
            <div style="color: var(--gray); font-size: 0.85rem;">{start} - {end}</div>
            {f'<div style="color: var(--primary); font-size: 0.85rem; margin-top: 0.3rem;">💰 {prize}</div>' if prize else ''}
        </div>'''


def update_torneos(state):
    """Actualizar torneos.html."""
    
    # Obtener datos
    current = state.get("current_tournament", {})
    last = state.get("last_tournament", {})
    
    # Generar HTML para torneo actual/último
    if last:
        current_html = generate_tournament_card(last, is_current=True)
    elif current:
        current_html = generate_tournament_card(current, is_current=True)
    else:
        current_html = "<p>No hay datos del torneo.</p>"
    
    # Lista de torneos terminados (para mostrar más si hay)
    # Por ahora solo mostramos el último
    finished_html = ""
    
    # Leer el archivo actual
    with open(TORNEOS_FILE, 'r') as f:
        html = f.read()
    
    # Reemplazar la sección del torneo actual
    marker_start = '<!-- TORNEO EN CURSO / ÚLTIMO TERMINADO -->'
    marker_end = '<!-- CALENDARIO COMPLETO -->'
    
    parts = html.split(marker_start)
    if len(parts) >= 2:
        parts_end = parts[1].split(marker_end)
        if len(parts_end) >= 2:
            new_html = parts[0] + marker_start + '\n            ' + current_html + '\n        ' + marker_end + parts_end[1]
        else:
            new_html = html
    else:
        new_html = html
    
    # Guardar
    with open(TORNEOS_FILE, 'w') as f:
        f.write(new_html)
    
    log("torneos.html actualizado")


def main():
    force = "--force" in sys.argv if 'sys' in dir() else False
    
    import sys
    force = "--force" in sys.argv
    dry_run = "--dry-run" in sys.argv
    
    log("=== TORNEOS AGENT STARTED ===")
    
    state = load_state()
    
    if dry_run:
        print("=== CURRENT TOURNAMENT DATA ===")
        print(json.dumps(state.get("current_tournament", {}), indent=2))
        print(json.dumps(state.get("last_tournament", {}), indent=2))
        return
    
    update_torneos(state)
    
    # Commit + Push
    import subprocess
    try:
        subprocess.run(["git", "add", "torneos.html"], cwd=PADEL_DIR, check=True)
        subprocess.run(["git", "commit", "-m", "UPDATE: Torneos - último torneo con ganador"], cwd=PADEL_DIR, check=True)
        subprocess.run(["git", "push", "origin", "main"], cwd=PADEL_DIR, check=True)
        log("Commit + Push successful")
    except Exception as e:
        log(f"Git error: {e}")
    
    log("=== TORNEOS AGENT COMPLETE ===")


if __name__ == "__main__":
    main()
