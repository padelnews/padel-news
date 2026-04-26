#!/usr/bin/env python3
"""
INDEX AGENT - Tournament Progress Updater
==========================================

MISIÓN:
Actualizar automáticamente la página index.html según el estado del torneo actual:
- ANTES del torneo: countdown + info
- DURANTE el torneo: emparejamientos, cuartos, semis, final, scores
- DESPUÉS del torneo: campeón + stats

SE ACTIVARÁ:
- Cada día a las 08:00 (para mostrar progreso del día)
- Cuando el torneoState.json cambia
- Manual: python3 scripts/index_agent.py --force

DATOS QUE NECESITA:
- data/tournament_state.json (fecha inicio/fin, estado, torneo actual)
- data/tournament_progress.json (resultados por día/ronda)
- FIP/Premier Padel para scores en vivo

OUTPUT:
- Actualiza index.html (sección último torneo)
- Commit + Push automático
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta

PADEL_DIR = Path("/Users/cristian/Sites/padel_news")
DATA_DIR = PADEL_DIR / "data"
TOURNAMENT_STATE = DATA_DIR / "tournament_state.json"
PROGRESS_FILE = DATA_DIR / "tournament_progress.json"
INDEX_FILE = PADEL_DIR / "index.html"


def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] INDEX_AGENT: {msg}")


def load_state():
    """Cargar estado del torneo."""
    if TOURNAMENT_STATE.exists():
        with open(TOURNAMENT_STATE) as f:
            return json.load(f)
    return {}


def load_progress():
    """Cargar progreso del torneo (resultados por ronda)."""
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE) as f:
            return json.load(f)
    return {}


def save_progress(data):
    """Guardar progreso del torneo."""
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def fetch_live_scores(tournament_id):
    """
    Descargar scores en vivo de FIP/Premier Padel.
    Por ahora usa datos hardcoded hasta que scrapee bien.
    """
    # TODO: Implementar scraping real con Playwright
    # Por ahora devolvemos el progreso guardado
    return None


def generate_tournament_section(state, progress):
    """
    Generar HTML para la sección del torneo según el estado.
    
    ESTADOS POSIBLES:
    - upcoming: Faltan días para que empiece
    - in_progress: Torneo en curso (muestra fase actual)
    - finished: Torneo finalizado (muestra campeón)
    """
    
    tournament = state.get("current_tournament", {})
    name = tournament.get("name", "Torneo")
    location = tournament.get("location", "")
    start_date = tournament.get("start_date", "")
    end_date = tournament.get("end_date", "")
    status = state.get("status", "upcoming")
    
    # Bandera del país
    country_flags = {
        "Paraguay": "🇵🇾", "Argentina": "🇦🇷", "Italy": "🇮🇹", 
        "Spain": "🇪🇸", "Belgium": "🇧🇪", "Egypt": "🇪🇬",
        "Saudi Arabia": "🇸🇦", "Mexico": "🇲🇽", "USA": "🇺🇸"
    }
    flag = country_flags.get(location.split()[-1] if location else "", "🏆")
    
    # --- TORneo FINALIZADO ---
    if status == "finished":
        champion = progress.get("champion", "TBD")
        runner_up = progress.get("runner_up", "TBD")
        score = progress.get("final_score", "-")
        
        return f'''
        <section style="background: linear-gradient(135deg, rgba(0,212,255,0.15), rgba(191,0,255,0.15)); border-radius: 16px; overflow: hidden; margin-bottom: 2rem; border: 1px solid var(--glass-border);">
            <div style="background: linear-gradient(90deg, #00d4ff, #bf00ff); padding: 1rem 1.5rem;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <span style="background: #000; color: #fff; padding: 0.25rem 0.6rem; border-radius: 4px; font-size: 0.75rem; font-weight: 700;">🏆 ÚLTIMO TORNEO</span>
                        <h2 style="margin: 0.5rem 0 0; color: #fff;">{name} {start_date[:4] if start_date else ""}</h2>
                    </div>
                    <div style="text-align: right; color: #fff;">
                        <div style="font-size: 0.85rem; opacity: 0.8;">{flag} {location}</div>
                        <div style="font-size: 0.85rem; opacity: 0.8;">{start_date[:7] if start_date else ""}</div>
                    </div>
                </div>
            </div>
            <div style="padding: 1.5rem;">
                <div style="background: rgba(0,0,0,0.3); border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem; text-align: center;">
                    <div style="font-size: 0.9rem; color: var(--primary); margin-bottom: 1rem; font-weight: 600;">🏆 CAMPEONES 🏆</div>
                    <div style="font-size: 1.5rem; font-weight: 700; color: #ffd700;">{champion}</div>
                    <div style="color: var(--gray); margin-top: 0.5rem;">vs {runner_up}</div>
                    <div style="margin-top: 0.5rem; font-size: 1.2rem; color: var(--primary);">{score}</div>
                </div>
            </div>
        </section>'''
    
    # --- TORneo EN PROGRESO ---
    elif status == "in_progress":
        current_round = progress.get("current_round", "quarters")
        matches = progress.get("matches", {})
        
        round_names = {
            "round_of_32": "Dieciseisavos",
            "round_of_16": "Octavos",
            "quarters": "Cuartos",
            "semis": "Semifinales",
            "final": "Final"
        }
        round_name = round_names.get(current_round, current_round)
        
        # Generar cuadro de partidos según la ronda
        matches_html = ""
        if current_round in ["quarters", "semis", "final"]:
            round_matches = matches.get(current_round, [])
            for m in round_matches:
                team1 = m.get("team1", "TBD")
                team2 = m.get("team2", "TBD")
                score = m.get("score", "")
                status_m = m.get("status", "pending")  # pending, live, finished
                
                if status_m == "live":
                    bg = "rgba(255,0,0,0.2)"
                    badge = "🔴 EN VIVO"
                elif status_m == "finished":
                    bg = "rgba(0,255,0,0.1)"
                    badge = "✅"
                else:
                    bg = "rgba(255,255,255,0.05)"
                    badge = "⏰"
                
                matches_html += f'''
                <div style="padding: 0.8rem; background: {bg}; border-radius: 8px; margin-bottom: 0.5rem; display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <span style="font-weight: 600;">{team1}</span>
                        <span style="margin: 0 0.5rem; color: var(--gray);">vs</span>
                        <span style="font-weight: 600;">{team2}</span>
                    </div>
                    <div style="text-align: right;">
                        {f'<span style="color: var(--primary); font-weight: 700;">{score}</span>' if score else ''}
                        <span style="margin-left: 0.5rem; font-size: 0.8rem;">{badge}</span>
                    </div>
                </div>'''
        
        return f'''
        <section style="background: linear-gradient(135deg, rgba(0,212,255,0.15), rgba(191,0,255,0.15)); border-radius: 16px; overflow: hidden; margin-bottom: 2rem; border: 1px solid var(--glass-border);">
            <div style="background: linear-gradient(90deg, #00d4ff, #bf00ff); padding: 1rem 1.5rem;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <span style="background: #ff0000; color: #fff; padding: 0.25rem 0.6rem; border-radius: 4px; font-size: 0.75rem; font-weight: 700;">🔴 EN CURSO</span>
                        <h2 style="margin: 0.5rem 0 0; color: #fff;">{name} {start_date[:4] if start_date else ""}</h2>
                    </div>
                    <div style="text-align: right; color: #fff;">
                        <div style="font-size: 0.85rem; opacity: 0.8;">{flag} {location}</div>
                        <div style="font-size: 0.85rem; opacity: 0.8;">{start_date[:7] if start_date else ""}</div>
                    </div>
                </div>
            </div>
            <div style="padding: 1.5rem;">
                <div style="margin-bottom: 1rem;">
                    <span style="background: var(--accent); color: #000; padding: 0.3rem 0.8rem; border-radius: 4px; font-weight: 700; font-size: 0.9rem;">{round_name}</span>
                </div>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1rem;">
                    {matches_html or "<p style='color: var(--gray);'>Cargando emparejamientos...</p>"}
                </div>
            </div>
        </section>'''
    
    # --- TORneo PRÓXIMO ---
    else:
        # Countdown
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            days_left = (start - datetime.now()).days
        except:
            days_left = "?"
        
        return f'''
        <section style="background: linear-gradient(135deg, rgba(0,212,255,0.15), rgba(191,0,255,0.15)); border-radius: 16px; overflow: hidden; margin-bottom: 2rem; border: 1px solid var(--glass-border);">
            <div style="background: linear-gradient(90deg, #00d4ff, #bf00ff); padding: 1rem 1.5rem;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <span style="background: #000; color: #fff; padding: 0.25rem 0.6rem; border-radius: 4px; font-size: 0.75rem; font-weight: 700;">📅 PRÓXIMO TORNEO</span>
                        <h2 style="margin: 0.5rem 0 0; color: #fff;">{name}</h2>
                    </div>
                    <div style="text-align: right; color: #fff;">
                        <div style="font-size: 0.85rem; opacity: 0.8;">{flag} {location}</div>
                        <div style="font-size: 0.85rem; opacity: 0.8;">{start_date} - {end_date}</div>
                    </div>
                </div>
            </div>
            <div style="padding: 2rem; text-align: center;">
                <div style="font-size: 3rem; font-weight: 900; color: var(--primary);">{days_left if isinstance(days_left, int) and days_left > 0 else "PRONTO"}</div>
                <div style="color: var(--gray);">días para que empiece</div>
            </div>
        </section>'''


def update_index(state, progress):
    """Actualizar index.html con los datos del torneo."""
    
    # Leer index actual
    with open(INDEX_FILE, 'r') as f:
        html = f.read()
    
    # Generar nueva sección torneo
    tournament_section = generate_tournament_section(state, progress)
    
    # Reemplazar la sección entre <main> y la primera sección de 3 columnas
    # Buscamos el patrón: después de </header> y antes de la sección de 3 columnas
    
    # Dividir por la sección de 3 columnas (resultados/rankings/próximos)
    marker = '<!-- 3 COLUMNAS -->'
    parts = html.split(marker)
    
    if len(parts) >= 2:
        new_html = parts[0] + tournament_section + '\n        \n' + marker + parts[1]
    else:
        log("WARNING: No encontré el marker de 3 columnas, usando método alternativo")
        # Extraer solo la parte del main
        new_html = tournament_section + html
    
    # Guardar
    with open(INDEX_FILE, 'w') as f:
        f.write(new_html)
    
    log(f"Index actualizado - Estado: {state.get('status')}")


def main():
    force = "--force" in sys.argv
    dry_run = "--dry-run" in sys.argv
    
    log("=== INDEX AGENT STARTED ===")
    
    state = load_state()
    progress = load_progress()
    
    if not state:
        log("ERROR: No tournament state found")
        sys.exit(1)
    
    status = state.get("status", "unknown")
    log(f"Current status: {status}")
    
    if dry_run:
        section = generate_tournament_section(state, progress)
        print("=== WOULD GENERATE ===")
        print(section)
        print("=== END ===")
        return
    
    # Verificar si hay que actualizar
    if not force:
        last_update = state.get("last_index_update", "")
        today = datetime.now().strftime("%Y-%m-%d")
        
        if last_update == today and status != "in_progress":
            log(f"Ya actualizado hoy ({today}), saltando...")
            return
    
    # Actualizar
    update_index(state, progress)
    
    # Marcar como actualizado
    state["last_index_update"] = datetime.now().strftime("%Y-%m-%d")
    with open(TOURNAMENT_STATE, 'w') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
    
    # Commit + Push
    import subprocess
    try:
        subprocess.run(["git", "add", "index.html"], cwd=PADEL_DIR, check=True)
        subprocess.run(["git", "commit", "-m", f"UPDATE: Index - torneo {state.get('status')}"], cwd=PADEL_DIR, check=True)
        subprocess.run(["git", "push", "origin", "main"], cwd=PADEL_DIR, check=True)
        log("Commit + Push successful")
    except Exception as e:
        log(f"Git error: {e}")
    
    log("=== INDEX AGENT COMPLETE ===")


if __name__ == "__main__":
    main()
