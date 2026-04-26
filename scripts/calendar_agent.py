#!/usr/bin/env python3
"""
TORNEOS CALENDAR AGENT
======================

MISIÓN:
Actualizar automáticamente el calendario de torneos en torneos.html según la fecha actual:
- "En curso" → Si hoy está entre las fechas del torneo
- "Finalizado" → Si las fechas ya pasaron
- "Próximo" → Si aún no ha empezar

También añade sección de GANADORES con los torneos terminados y sus campeones.

SE ACTIVARÁ:
- Cada día a las 08:00 y 20:00
- Cuando cambie tournament_state.json

DATOS:
- tournament_state.json → sabe qué torneo está en curso y el último terminado
- tournament_progress.json → resultados

OUTPUT:
- Actualiza la tabla de calendario en torneos.html
- Añade/modifica sección de "Ganadores" 
- Commit + Push
"""

import json
import re
from pathlib import Path
from datetime import datetime

PADEL_DIR = Path("/Users/cristian/Sites/padel_news")
DATA_DIR = PADEL_DIR / "data"
STATE_FILE = DATA_DIR / "tournament_state.json"
PROGRESS_FILE = DATA_DIR / "tournament_progress.json"
TORNEOS_FILE = PADEL_DIR / "torneos.html"


def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] CALENDAR_AGENT: {msg}")


def load_state():
    with open(STATE_FILE) as f:
        return json.load(f)


def parse_date(date_str):
    """Convertir string YYYY-MM-DD a datetime."""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except:
        return None


def get_tournament_status(start_date, end_date):
    """
    Devuelve el estado del torneo según la fecha actual.
    Returns: "finished", "in_progress", "upcoming"
    """
    today = datetime.now()
    start = parse_date(start_date)
    end = parse_date(end_date)
    
    if not start or not end:
        return "unknown"
    
    if today < start:
        return "upcoming"
    elif today > end:
        return "finished"
    else:
        return "in_progress"


def generate_status_badge(status):
    """Generar HTML del badge según estado."""
    badges = {
        "finished": '<span class="badge" style="background: rgba(100,100,100,0.3);">✓ Finalizado</span>',
        "in_progress": '<span class="badge" style="background: linear-gradient(135deg, #00d4ff, #bf00ff);">🔴 En Curso</span>',
        "upcoming": '<span class="badge badge-primary">Próximo</span>',
        "today": '<span class="badge" style="background: linear-gradient(135deg, #ffd700, #ff8c00);">🏆 HOY</span>'
    }
    return badges.get(status, badges["upcoming"])


def update_calendar(state, html):
    """
    Actualizar la tabla del calendario con los estados correctos.
    """
    # Lista de torneos con fechas (del calendario original)
    # Formato: (nombre, fecha_inicio, fecha_fin)
    tournaments = [
        ("Riyadh Season P1", "2026-02-09", "2026-02-14"),
        ("Gijón P2", "2026-03-02", "2026-03-08"),
        ("Cancún P2", "2026-03-16", "2026-03-22"),
        ("Miami P1", "2026-03-23", "2026-03-29"),
        ("Newgiza P2", "2026-04-13", "2026-04-19"),
        ("Brussels P2", "2026-04-20", "2026-04-26"),
        ("Asunción P1", "2026-05-04", "2026-05-10"),
        ("Buenos Aires P1", "2026-05-11", "2026-05-17"),
        ("Italy Major", "2026-06-01", "2026-06-07"),
        ("Valencia P1", "2026-06-08", "2026-06-14"),
        ("Valladolid P2", "2026-06-22", "2026-06-28"),
        ("Bordeaux P2", "2026-06-29", "2026-07-05"),
        ("Málaga P1", "2026-07-13", "2026-07-19"),
        ("Pretoria P2", "2026-07-27", "2026-08-02"),
        ("London P1", "2026-08-03", "2026-08-09"),
        ("Mediterranean Games", "2026-08-21", "2026-08-28"),
        ("Madrid P1", "2026-08-31", "2026-09-06"),
        ("Paris Major", "2026-09-07", "2026-09-13"),
        ("Rotterdam P2", "2026-09-28", "2026-10-04"),
        ("Germany P2", "2026-10-05", "2026-10-11"),
        ("Milano P1", "2026-10-12", "2026-10-18"),
        ("Kuwait P1", "2026-10-26", "2026-10-31"),
        ("FIP World Cup", "2026-11-01", "2026-11-07"),
        ("Dubai P1", "2026-11-09", "2026-11-15"),
        ("Mexico Major", "2026-11-23", "2026-11-29"),
        ("Barcelona Finals", "2026-12-07", "2026-12-13"),
    ]
    
    # Para cada torneo, determinar su estado
    today = datetime.now()
    
    for name, start, end in tournaments:
        status = get_tournament_status(start, end)
        badge = generate_status_badge(status)
        
        # Patrón para encontrar esta fila en el HTML
        # Buscamos el td que contiene el nombre del torneo
        pattern = rf'(<tr>\s*<td>[^<]*</td>\s*<td>{re.escape(name)}.*?<td>)(.*?)(</td>\s*</tr>)'
        
        # Reemplazar el badge
        new_badge = f'<td>{badge}</td>'
        replacement = rf'\1{new_badge}\3'
        
        html = re.sub(pattern, replacement, html, flags=re.DOTALL)
    
    return html


def generate_winners_section(state):
    """Generar sección de ganadores de torneos terminados."""
    
    last = state.get("last_tournament", {})
    
    if not last:
        return ""
    
    champions = last.get("champions", [])
    name = last.get("name", "Torneo")
    score = last.get("final_score_detailed", "")
    runner_up = last.get("runner_up", [])
    
    if not champions:
        return ""
    
    champ_names = " / ".join(champions)
    ru_names = " / ".join(runner_up) if runner_up else "TBD"
    
    return f'''
        <!-- GANADORES RECIENTES -->
        <section style="margin-top: 2rem;">
            <h3 style="color: var(--primary); margin-bottom: 1rem;">🏆 Último Ganador</h3>
            <div style="background: linear-gradient(135deg, rgba(255,215,0,0.1), rgba(191,0,255,0.1)); border-radius: 12px; padding: 1.5rem; border: 1px solid rgba(255,215,0,0.3);">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div style="font-size: 0.85rem; color: var(--gray); margin-bottom: 0.3rem;">{name}</div>
                        <div style="font-size: 1.5rem; font-weight: 700; color: #ffd700;">{champ_names}</div>
                        <div style="color: var(--gray); font-size: 0.9rem; margin-top: 0.3rem;">vs {ru_names}</div>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-size: 2rem;">🏆</div>
                        <div style="color: var(--primary); font-weight: 700;">{score}</div>
                    </div>
                </div>
            </div>
        </section>'''


def update_torneos():
    """Función principal."""
    log("=== CALENDAR AGENT STARTED ===")
    
    state = load_state()
    
    # Leer HTML actual
    with open(TORNEOS_FILE, 'r') as f:
        html = f.read()
    
    # 1. Actualizar badges del calendario
    html = update_calendar(state, html)
    
    # 2. Añadir/quitar sección de ganadores
    winners_html = generate_winners_section(state)
    
    if winners_html:
        # Buscar si ya existe sección de ganadores y reemplazarla
        if '<!-- GANADORES RECIENTES -->' in html:
            # Reemplazar contenido entre los marcadores
            pattern = r'<!-- GANADORES RECIENTES -->.*?<!-- FIN GANADORES -->'
            html = re.sub(pattern, winners_html.replace('<!-- GANADORES RECIENTES -->', '').replace('<!-- FIN GANADORES -->', ''), html, flags=re.DOTALL)
        else:
            # Añadir antes del closing </main>
            html = html.replace('</main>', winners_html + '\n    </main>')
    
    # Guardar
    with open(TORNEOS_FILE, 'w') as f:
        f.write(html)
    
    log("Calendario actualizado")
    
    # Commit + Push
    import subprocess
    try:
        subprocess.run(["git", "add", "torneos.html"], cwd=PADEL_DIR, check=True)
        subprocess.run(["git", "commit", "-m", "UPDATE: Calendario - estados automáticos según fecha"], cwd=PADEL_DIR, check=True)
        subprocess.run(["git", "push", "origin", "main"], cwd=PADEL_DIR, check=True)
        log("Commit + Push successful")
    except Exception as e:
        log(f"Git error: {e}")
    
    log("=== CALENDAR AGENT COMPLETE ===")


def main():
    dry_run = "--dry-run" in __import__('sys').argv
    
    if dry_run:
        state = load_state()
        today = datetime.now()
        log(f"Today: {today.strftime('%Y-%m-%d')}")
        log("Would update tournament statuses:")
        
        tournaments = [
            ("Brussels P2", "2026-04-20", "2026-04-26"),
            ("Asunción P1", "2026-05-04", "2026-05-10"),
        ]
        
        for name, start, end in tournaments:
            status = get_tournament_status(start, end)
            log(f"  {name}: {status}")
        return
    
    update_torneos()


if __name__ == "__main__":
    main()
