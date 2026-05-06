#!/usr/bin/env python3
"""
Padel News - Actualidad Agent
============================
Busca noticias de pádel automáticamente y actualiza la web.

Ejecuta cada 6 horas (360 minutos):
1. Fetch news desde fuentes (fetch_news.py)
2. Genera páginas actualizadas (website_generator.py)
3. Commit y push a GitHub si hay cambios

CRON: Ejecutar cada 6 horas vía launchd
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

PADEL_DIR = Path("/Users/cristian/Sites/padel_news")
SCRIPTS_DIR = PADEL_DIR / "scripts"
LOG_FILE = SCRIPTS_DIR / "actualidad_agent.log"
STATE_FILE = SCRIPTS_DIR / "actualidad_state.json"


def log(msg: str):
    """Log message with timestamp."""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")
    print(line)


def run_script(script_name: str, timeout: int = 120) -> tuple[bool, str]:
    """Run a Python script and return (success, output)."""
    script_path = SCRIPTS_DIR / script_name
    try:
        result = subprocess.run(
            ['python3', str(script_path)],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(PADEL_DIR)
        )
        output = result.stdout + result.stderr
        return result.returncode == 0, output
    except subprocess.TimeoutExpired:
        return False, f"Timeout after {timeout}s"
    except Exception as e:
        return False, str(e)


def git_commit_push() -> bool:
    """Commit and push changes to GitHub if any."""
    try:
        # Check if there are changes
        result = subprocess.run(
            ['git', 'status', '--porcelain'],
            capture_output=True,
            text=True,
            cwd=str(PADEL_DIR),
            timeout=30
        )
        
        if not result.stdout.strip():
            log("No changes to commit")
            return True
        
        # Add changes
        subprocess.run(['git', 'add', '-A'], cwd=str(PADEL_DIR), timeout=30, check=True)
        
        # Commit
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        subprocess.run(
            ['git', 'commit', '-m', f'📰 Actualidad auto-update: {timestamp}'],
            cwd=str(PADEL_DIR),
            timeout=30,
            check=True
        )
        
        # Push
        result = subprocess.run(
            ['git', 'push', 'origin', 'main'],
            capture_output=True,
            text=True,
            cwd=str(PADEL_DIR),
            timeout=120
        )
        
        if result.returncode == 0:
            log("✅ Changes pushed to GitHub")
            return True
        else:
            log(f"⚠️ Git push failed: {result.stderr}")
            # Try pull + re-push
            log("Attempting pull + re-push...")
            subprocess.run(['git', 'pull', '--no-rebase', '-X', 'ours'], 
                         cwd=str(PADEL_DIR), timeout=60, check=True)
            subprocess.run(['git', 'push', 'origin', 'main'], 
                         cwd=str(PADEL_DIR), timeout=120, check=True)
            log("✅ Pull + push successful")
            return True
            
    except subprocess.CalledProcessError as e:
        log(f"❌ Git error: {e}")
        return False
    except Exception as e:
        log(f"❌ Unexpected error: {e}")
        return False


def load_state() -> dict:
    """Load agent state."""
    try:
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    except:
        return {"last_run": None, "articles_fetched": 0}


def save_state(state: dict):
    """Save agent state."""
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)


def main():
    log("=" * 60)
    log("ACTUALIDAD AGENT STARTED")
    log("=" * 60)
    
    state = load_state()
    
    # Step 1: Fetch news
    log("\n>>> Step 1: Fetching news...")
    success, output = run_script("fetch_news.py", timeout=300)
    if success:
        log("✅ News fetched successfully")
        # Extract number of articles from output if possible
        articles_count = "unknown"
        for line in output.split('\n'):
            if 'articles' in line.lower() or 'noticias' in line.lower():
                articles_count = line.strip()
                break
        state["last_fetch"] = datetime.now().isoformat()
        state["articles_info"] = articles_count
    else:
        log(f"⚠️ News fetch failed or timed out: {output[:200]}")
        log("Continuing with existing news data...")
    
    # Step 2: Generate pages
    log("\n>>> Step 2: Generating pages...")
    success, output = run_script("website_generator.py", timeout=120)
    if success:
        log("✅ Pages generated successfully")
    else:
        log(f"❌ Page generation failed: {output[:200]}")
        log("Stopping here - no point committing broken pages")
        save_state(state)
        sys.exit(1)
    
    # Step 3: Commit and push
    log("\n>>> Step 3: Committing and pushing to GitHub...")
    if git_commit_push():
        log("✅ All done!")
    else:
        log("⚠️ Some issues during commit/push, but continuing...")
    
    # Update state
    state["last_run"] = datetime.now().isoformat()
    state["runs_count"] = state.get("runs_count", 0) + 1
    save_state(state)
    
    log("\n" + "=" * 60)
    log("ACTUALIDAD AGENT COMPLETED")
    log(f"Total runs: {state['runs_count']}")
    log("=" * 60)


if __name__ == "__main__":
    main()
