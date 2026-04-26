#!/usr/bin/env python3
"""
Rankings Update Flow
====================
This script updates the rankings.html page with fresh data from rankings_fetch.py

AGENT TASK (runs automatically):
1. Run rankings_fetch.py → gets data from FIP
2. Read data/rankings_data.json
3. Generate new rankings.html
4. Commit & push to GitHub

MANUAL OVERRIDE:
- Edit scripts/tournament_state.json with manual ranking updates
- Run: python3 scripts/update_rankings.py --force

CRON SCHEDULE: Every Sunday at 20:00 (before new tournament week)

LAST RUN: Check data/last_fetch.txt
"""

import json
import sys
from pathlib import Path
from datetime import datetime

PADEL_DIR = Path("/Users/cristian/Sites/padel_news")
DATA_DIR = PADEL_DIR / "data"


def load_rankings():
    """Load rankings from data directory."""
    f = DATA_DIR / "rankings_data.json"
    if f.exists():
        with open(f) as fp:
            return json.load(fp)
    return None


def generate_rankings_html(data):
    """Generate rankings.html from data."""
    
    male_pairs = data.get("male_pairs", [])
    female_pairs = data.get("female_pairs", [])
    last_updated = data.get("last_updated", "Desconocida")
    source = data.get("source", "FIP")
    
    male_rows = ""
    for p in male_pairs:
        male_rows += f'''
            <tr>
                <td>{p["rank"]}</td>
                <td>🇦🇷 {p["player1"]} / 🇪🇸 {p["player2"]}</td>
                <td>🇦🇷🇪🇸</td>
                <td class="points">{p["points"]:,}</td>
            </tr>'''
    
    female_rows = ""
    for p in female_pairs:
        female_rows += f'''
            <tr>
                <td>{p["rank"]}</td>
                <td>🇦🇷 {p["player1"]} / 🇪🇸 {p["player2"]}</td>
                <td>🇦🇷🇪🇸</td>
                <td class="points">{p["points"]:,}</td>
            </tr>'''
    
    html = f'''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rankings por Parejas Premier Padel 2026 | Padel News Pro</title>
    <link rel="stylesheet" href="css/style-futuristic.css">
    <link href="https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&family=Orbitron:wght@700;900&display=swap" rel="stylesheet">
    <style>
        .rankings-container {{ max-width: 100%; overflow-x: auto; }}
        .rankings-table {{ width: 100%; border-collapse: collapse; background: var(--glass-bg); border-radius: 12px; overflow: hidden; }}
        .rankings-table th {{ background: rgba(0, 212, 255, 0.2); padding: 1rem 0.8rem; text-align: center; font-weight: 600; font-size: 0.9rem; }}
        .rankings-table td {{ padding: 0.8rem; text-align: center; border-bottom: 1px solid rgba(255,255,255,0.05); }}
        .rankings-table td:first-child {{ text-align: center; font-weight: 700; color: var(--primary); font-size: 1.1rem; }}
        .rankings-table td:nth-child(2) {{ text-align: left; font-weight: 600; }}
        .rankings-table td:nth-child(3) {{ text-align: center; }}
        .rankings-table td:nth-child(4) {{ text-align: right; font-weight: 600; }}
        .rankings-table tr:hover {{ background: rgba(0, 212, 255, 0.1); }}
        .rankings-table tr.top-3 {{ background: rgba(191, 0, 255, 0.1); }}
        .points {{ color: var(--primary); font-weight: 700; }}
        .tab-buttons {{ display: flex; gap: 1rem; margin-bottom: 2rem; flex-wrap: wrap; }}
        .tab-btn {{ padding: 0.8rem 2rem; border: none; border-radius: 8px; cursor: pointer; font-family: 'Rajdhani', sans-serif; font-weight: 600; font-size: 1rem; transition: all 0.3s; background: rgba(255,255,255,0.1); color: #fff; }}
        .tab-btn:hover {{ background: rgba(0, 212, 255, 0.3); }}
        .tab-btn.active {{ background: linear-gradient(135deg, var(--primary), var(--accent)); color: #000; }}
        .tab-content {{ display: none; }}
        .tab-content.active {{ display: block; }}
        .ranking-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; flex-wrap: wrap; gap: 1rem; }}
        .info-box {{ margin-top: 2rem; padding: 1.5rem; background: rgba(0,212,255,0.1); border-radius: 12px; border: 1px solid var(--glass-border); }}
        .info-box h4 {{ color: var(--primary); margin-bottom: 0.5rem; }}
        .info-box p {{ color: #ccc; font-size: 0.95rem; }}
        @media (max-width: 768px) {{ .rankings-table {{ font-size: 0.85rem; }} }}
    </style>
</head>
<body>
    <header>
        <div class="container">
            <div class="header-branding">
                <h1>🎾 Padel <span>News</span> Pro</h1>
            </div>
            <p class="tagline">Tu portal profesional del Premier Padel Tour - Rankings oficiales</p>
            <span class="live-badge">🏆 Bruselas completado | LEBRÓN/AUGSBURGER campeones | Próximo: Asunción P2 (Mayo)</span>
        </div>
    </header>
    
    <nav>
        <div class="container">
            <ul>
                <li><a href="index.html">Inicio</a></li>
                <li><a href="rankings.html" class="active">Rankings</a></li>
                <li><a href="torneos.html">Torneos</a></li>
                <li><a href="resultados.html">Resultados</a></li>
                <li><a href="actualidad.html">Actualidad</a></li>
                <li><a href="chollos.html">Chollos 🏷️</a></li>
            </ul>
        </div>
    </nav>
    
    <main class="container">
        <h2 class="section-title">🏆 Rankings por Parejas - Premier Padel 2026</h2>
        
        <div class="tab-buttons">
            <button class="tab-btn active" onclick="showTab('male')">👨 Masculino</button>
            <button class="tab-btn" onclick="showTab('female')">👩 Femenino</button>
        </div>
        
        <div id="male" class="tab-content active">
            <div class="ranking-header">
                <h3 style="color: var(--primary);">📊 Ranking Masculino - Por Parejas</h3>
                <span style="color: #888; font-size: 0.9rem;">📅 Actualizado: {last_updated} • Fuente: {source}</span>
            </div>
            
            <div class="rankings-container">
                <table class="rankings-table">
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Pareja</th>
                            <th>País</th>
                            <th>Puntos</th>
                        </tr>
                    </thead>
                    <tbody>
                        {male_rows}
                    </tbody>
                </table>
            </div>
        </div>
        
        <div id="female" class="tab-content">
            <div class="ranking-header">
                <h3 style="color: var(--primary);">📊 Ranking Femenino - Por Parejas</h3>
                <span style="color: #888; font-size: 0.9rem;">📅 Actualizado: {last_updated} • Fuente: {source}</span>
            </div>
            
            <div class="rankings-container">
                <table class="rankings-table">
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Pareja</th>
                            <th>País</th>
                            <th>Puntos</th>
                        </tr>
                    </thead>
                    <tbody>
                        {female_rows}
                    </tbody>
                </table>
            </div>
        </div>
        
        <script>
            function showTab(tab) {{
                document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
                document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
                document.getElementById(tab).classList.add('active');
                event.target.classList.add('active');
            }}
        </script>
        
        <div class="info-box">
            <h4>📊 Rankings Oficiales por Parejas</h4>
            <p>En pádel, el ranking oficial es por parejas. Los puntos se acumulan según los resultados en torneos del Premier Padel Tour. Fuente: FIP (Federación Internacional de Pádel).</p>
        </div>
    </main>
    
    <footer>
        <div class="container">
            <p>© 2026 Padel News Pro | Powered by Local AI</p>
        </div>
    </footer>
</body>
</html>'''
    
    return html


def main():
    force = "--force" in sys.argv
    
    data = load_rankings()
    if not data:
        print("ERROR: No rankings data found. Run rankings_fetch.py first.")
        sys.exit(1)
    
    # Check freshness
    if not force:
        last_updated = data.get("last_updated", "")
        # Could add age check here
        
    html = generate_rankings_html(data)
    
    out_file = PADEL_DIR / "rankings.html"
    with open(out_file, 'w') as f:
        f.write(html)
    
    print(f"Updated {out_file}")
    print(f"Data source: {data.get('source')}")
    print(f"Last updated: {data.get('last_updated')}")


if __name__ == "__main__":
    main()