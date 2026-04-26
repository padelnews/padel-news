#!/usr/bin/env python3
"""
INDEX AGENT - Tournament Progress Updater
==========================================

MISIÓN:
Actualizar automáticamente la página index.html según el estado del torneo actual:
- ANTES del torneo: countdown + info
- DURANTE el torneo: emparejamientos, cuartos, semis, final, scores
- DESPUÉS del torneo: campeón + stats (del torneo anterior)

SE ACTIVARÁ:
- Cada día a las 08:00 (para mostrar progreso del día)
- Cuando el torneoState.json cambia
- Manual: python3 scripts/index_agent.py --force
"""

import json
import sys
from pathlib import Path
from datetime import datetime

PADEL_DIR = Path("/Users/cristian/Sites/padel_news")
DATA_DIR = PADEL_DIR / "data"
STATE_FILE = DATA_DIR / "tournament_state.json"
PROGRESS_FILE = DATA_DIR / "tournament_progress.json"
INDEX_FILE = PADEL_DIR / "index.html"


def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] INDEX_AGENT: {msg}")


def load_state():
    """Cargar estado del torneo."""
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
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


def save_state(data):
    """Guardar estado del torneo."""
    with open(STATE_FILE, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def generate_tournament_section(state, progress):
    """
    Generar HTML para la sección del torneo según el estado.
    
    ESTADOS POSIBLES:
    - upcoming: Faltan días para que empiece
    - in_progress: Torneo en curso (muestra fase actual)
    - finished: No se usa, siempre mostramos el ÚLTIMO TORNEO TERMINADO
    """
    
    tournament = state.get("current_tournament", {})
    last_tournament = state.get("last_tournament", {})
    status = state.get("status", "upcoming")
    
    # Bandera del país
    country_flags = {
        "Paraguay": "🇵🇾", "Argentina": "🇦🇷", "Italy": "🇮🇹", 
        "Spain": "🇪🇸", "Belgium": "🇧🇪", "Egypt": "🇪🇬",
        "Saudi Arabia": "🇸🇦", "Mexico": "🇲🇽", "USA": "🇺🇸",
        "Bélgica": "🇧🇪"
    }
    
    # --- SI HAY ÚLTIMO TORNEO TERMINADO (siempre mostramos esto) ---
    if last_tournament:
        name = last_tournament.get("name", "Torneo")
        location = last_tournament.get("location", "")
        start_date = last_tournament.get("start_date", "")[:7] if last_tournament.get("start_date") else ""
        champions = last_tournament.get("champions", [])
        champion_country = last_tournament.get("champion_country", [])
        runner_up = last_tournament.get("runner_up", [])
        score = last_tournament.get("final_score_detailed", "")
        prize = last_tournament.get("prize", "")
        participants = last_tournament.get("participants", "")
        spectators = last_tournament.get("spectators", "")
        venue = last_tournament.get("venue", "")
        
        flag = country_flags.get(location, "🏆")
        
        # Construir nombres de campeones
        champ1 = f"{champions[0]}" if len(champions) > 0 else "TBD"
        champ2 = f"{champions[1]}" if len(champions) > 1 else ""
        champ1_country = f"🇦🇷" if len(champion_country) > 0 and champion_country[0] == "Argentina" else "🇪🇸"
        champ2_country = f"🇦🇷" if len(champion_country) > 1 and champion_country[1] == "Argentina" else "🇪🇸"
        
        champ_photo1 = champ1.lower().replace(" ", "-")
        champ_photo2 = champ2.lower().replace(" ", "-")
        
        ru1 = f"{runner_up[0]}" if len(runner_up) > 0 else "TBD"
        ru2 = f"{runner_up[1]}" if len(runner_up) > 1 else ""
        
        return f'''
        <section style="background: linear-gradient(135deg, rgba(0,212,255,0.15), rgba(191,0,255,0.15)); border-radius: 16px; overflow: hidden; margin-bottom: 2rem; border: 1px solid var(--glass-border);">
            <div style="background: linear-gradient(90deg, #00d4ff, #bf00ff); padding: 1rem 1.5rem;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <span style="background: #000; color: #fff; padding: 0.25rem 0.6rem; border-radius: 4px; font-size: 0.75rem; font-weight: 700;">🏆 ÚLTIMO TORNEO</span>
                        <h2 style="margin: 0.5rem 0 0; color: #fff;">{name}</h2>
                    </div>
                    <div style="text-align: right; color: #fff;">
                        <div style="font-size: 0.85rem; opacity: 0.8;">{flag} {location}</div>
                        <div style="font-size: 0.85rem; opacity: 0.8;">{start_date}</div>
                    </div>
                </div>
            </div>
            <div style="padding: 1.5rem;">
                <div style="background: rgba(0,0,0,0.3); border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem; text-align: center;">
                    <div style="font-size: 0.9rem; color: var(--primary); margin-bottom: 1rem; font-weight: 600;">🏆 CAMPEONES 🏆</div>
                    
                    <div style="display: flex; justify-content: center; align-items: center; gap: 2rem; flex-wrap: wrap;">
                        <div style="text-align: center;">
                            <img src="images/players/{champ_photo1}.jpg" alt="{champ1}" style="width: 70px; height: 70px; border-radius: 50%; object-fit: cover; border: 3px solid gold;" onerror="this.src='https://placehold.co/70x70/ffd700/000?text={champ1[:1]}'">
                            <div style="font-weight: 700; margin-top: 0.5rem;">{champ1}</div>
                            <div style="font-size: 0.8rem; color: var(--gray);">{champ1_country}</div>
                        </div>
                        
                        <div style="text-align: center;">
                            <img src="images/players/{champ_photo2}.jpg" alt="{champ2}" style="width: 70px; height: 70px; border-radius: 50%; object-fit: cover; border: 3px solid gold;" onerror="this.src='https://placehold.co/70x70/ffd700/000?text={champ2[:1]}'">
                            <div style="font-weight: 700; margin-top: 0.5rem;">{champ2}</div>
                            <div style="font-size: 0.8rem; color: var(--gray);">{champ2_country}</div>
                        </div>
                        
                        <div style="background: rgba(191,0,255,0.3); border-radius: 12px; padding: 1rem 1.5rem;">
                            <div style="font-size: 1.5rem; font-weight: 900; color: var(--accent);">VS</div>
                            <div style="font-size: 1.8rem; font-weight: 700; margin-top: 0.5rem;">2-1</div>
                            <div style="font-size: 0.85rem; color: var(--gray);">Marcador final</div>
                        </div>
                    </div>
                    
                    <div style="margin-top: 1rem; padding: 0.8rem; background: rgba(0,212,255,0.2); border-radius: 8px;">
                        <span style="font-size: 0.9rem;">📍 Final: {score} vs {ru1}/{ru2}</span>
                    </div>
                </div>
                
                <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem;">
                    <div style="background: rgba(255,255,255,0.05); padding: 1rem; border-radius: 8px; text-align: center;">
                        <div style="font-size: 1.5rem; margin-bottom: 0.3rem;">💰</div>
                        <div style="font-weight: 700; color: var(--primary);">{prize}</div>
                        <div style="font-size: 0.75rem; color: var(--gray);">Premio pareja ganadora</div>
                    </div>
                    <div style="background: rgba(255,255,255,0.05); padding: 1rem; border-radius: 8px; text-align: center;">
                        <div style="font-size: 1.5rem; margin-bottom: 0.3rem;">🎾</div>
                        <div style="font-weight: 700; color: var(--primary);">{participants}</div>
                        <div style="font-size: 0.75rem; color: var(--gray);">Parejas participantes</div>
                    </div>
                    <div style="background: rgba(255,255,255,0.05); padding: 1rem; border-radius: 8px; text-align: center;">
                        <div style="font-size: 1.5rem; margin-bottom: 0.3rem;">👁️</div>
                        <div style="font-weight: 700; color: var(--primary);">{spectators}</div>
                        <div style="font-size: 0.75rem; color: var(--gray);">Espectadores semana</div>
                    </div>
                    <div style="background: rgba(255,255,255,0.05); padding: 1rem; border-radius: 8px; text-align: center;">
                        <div style="font-size: 1.5rem; margin-bottom: 0.3rem;">🏟️</div>
                        <div style="font-weight: 700; color: var(--primary);">{venue}</div>
                        <div style="font-size: 0.75rem; color: var(--gray);">Sede del torneo</div>
                    </div>
                </div>
            </div>
        </section>'''
    
    # --- TORneo PRÓXIMO (sin último torneo) ---
    name = tournament.get("name", "Torneo")
    location = tournament.get("location", "")
    start_date = tournament.get("start_date", "")
    end_date = tournament.get("end_date", "")
    flag = country_flags.get(location.split()[-1] if location else "", "🏆")
    
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
    
    # Dividir por la sección de 3 columnas
    marker = '<!-- 2 COLUMNAS: Resultados + Próximos -->'
    parts = html.split(marker)
    
    if len(parts) >= 2:
        new_html = parts[0] + tournament_section + '\n        \n' + marker + parts[1]
    else:
        log("WARNING: No encontré el marker, usando método alternativo")
        new_html = tournament_section + html
    
    # Guardar
    with open(INDEX_FILE, 'w') as f:
        f.write(new_html)
    
    log(f"Index actualizado - Status: {state.get('status')}")


def main():
    force = "--force" in sys.argv
    dry_run = "--dry-run" in sys.argv
    
    log("=== INDEX AGENT STARTED ===")
    
    state = load_state()
    progress = load_progress()
    
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
        
        if last_update == today:
            log(f"Ya actualizado hoy ({today}), saltando...")
            return
    
    # Actualizar
    update_index(state, progress)
    
    # Marcar como actualizado
    state["last_index_update"] = datetime.now().strftime("%Y-%m-%d")
    save_state(state)
    
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
