#!/usr/bin/env python3
"""
Padel News Orchestrator v1.0
============================
Central orchestrator that schedules and runs agents based on time/events.

Schedule:
- Every 5 min:   Check schedule and run agents as needed
- 08:00 daily:    index_agent (update index.html with current tournament)
- 20:00 daily:    tournament_updater (check for new tournaments)
- Sunday 20:00:   rankings_agent (update FIP rankings)
- Every 10 min:   chollos_agent (fetch new deals)
- During tournament: live_score_agent (results in vivo)
- Every 30 min:   tournament_watcher (look for new tournaments)

Each agent is independent and knows what to update.
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime, time

# Configuration
PADEL_DIR = Path("/Users/cristian/Sites/padel_news")
SCRIPTS_DIR = PADEL_DIR / "scripts"
STATE_FILE = SCRIPTS_DIR / "tournament_state.json"
LOG_FILE = SCRIPTS_DIR / "orchestrator.log"

# Schedule definition
# Each entry: (name, script, run_condition, description)
SCHEDULE = {
    # Runs every 5 minutes - always check
    "check_tournament_state": {
        "script": "dynamic_flow.py",
        "interval_minutes": 5,
        "last_run": None,
        "description": "Check tournament state and transition if needed",
        "condition": "always"
    },
    
    # Morning and evening - update index
    "index_updater": {
        "script": "index_agent.py",
        "interval_minutes": 720,  # Twice daily
        "hours": [8, 20],
        "last_run": None,
        "description": "Update index.html with current tournament info",
        "condition": "time_based"
    },
    
    # Every morning - update calendar
    "torneos_updater": {
        "script": "torneos_agent.py",
        "interval_minutes": 1440,  # Daily
        "hours": [9],
        "last_run": None,
        "description": "Update torneos.html calendar",
        "condition": "time_based"
    },
    
    # Sunday evening - FIP rankings
    "rankings_updater": {
        "script": "update_rankings.py",
        "interval_minutes": 10080,  # Weekly
        "hours": [20],
        "weekdays": [6],  # Sunday (0=Mon, 6=Sun)
        "last_run": None,
        "description": "Update rankings from FIP official data",
        "condition": "time_based"
    },
    
    # Every 10 min - chollos
    "chollos_fetcher": {
        "script": "fetch_chollos.py",
        "interval_minutes": 10,
        "last_run": None,
        "description": "Fetch new deals from NOX, Siux, Babolat",
        "condition": "always"
    },
    
    # Every 30 min - tournament watcher
    "tournament_watcher": {
        "script": "tournament_watcher.py",
        "interval_minutes": 30,
        "last_run": None,
        "description": "Watch for new tournaments in Premier Padel",
        "condition": "always"
    },
    
    # During tournament only - live scores
    "live_score": {
        "script": "live_score_agent.py",
        "interval_minutes": 30,
        "last_run": None,
        "description": "Update live results during active tournament",
        "condition": "tournament_active"
    },
    
    # Every 6 hours - actualidad/news
    "actualidad_updater": {
        "script": "update_actualidad.py",
        "interval_minutes": 360,
        "last_run": None,
        "description": "Update news/actualidad section",
        "condition": "always"
    },
    
    # After tournament ends - results
    "resultados_updater": {
        "script": "fetch_results.py",
        "interval_minutes": 60,
        "last_run": None,
        "description": "Update results once tournament finishes",
        "condition": "tournament_finished"
    }
}

# State file for tracking last run times
STATE_TRACK_FILE = PADEL_DIR / "data" / "orchestrator_state.json"


def log(msg: str, verbose: bool = True):
    """Log message to file and console."""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")
    if verbose:
        print(line)


def load_state() -> dict:
    """Load tournament state."""
    try:
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}


def load_orchestrator_state() -> dict:
    """Load orchestrator tracking state."""
    try:
        with open(STATE_TRACK_FILE, 'r') as f:
            return json.load(f)
    except:
        return {"last_runs": {}}


def save_orchestrator_state(state: dict) -> bool:
    """Save orchestrator tracking state."""
    try:
        PADEL_DIR.joinpath("data").mkdir(parents=True, exist_ok=True)
        with open(STATE_TRACK_FILE, 'w') as f:
            json.dump(state, f, indent=2)
        return True
    except Exception as e:
        log(f"ERROR saving orchestrator state: {e}")
        return False


def should_run(agent_name: str, config: dict, state: dict, track_state: dict) -> tuple:
    """
    Check if an agent should run based on:
    - Time-based conditions
    - Tournament state conditions
    - Interval since last run
    
    Returns (should_run: bool, reason: str)
    """
    now = datetime.now()
    last_run = track_state.get("last_runs", {}).get(agent_name)
    
    # Check condition types
    condition = config.get("condition", "always")
    
    # Tournament state conditions
    current_tournament = state.get("current_tournament", {})
    status = current_tournament.get("status", "unknown")
    
    if condition == "tournament_active" and status != "active":
        return False, f"Tournament is {status}, not active"
    
    if condition == "tournament_finished" and status != "finished":
        return False, f"Tournament is {status}, not finished"
    
    if condition == "time_based":
        # Check if it's the right hour
        current_hour = now.hour
        allowed_hours = config.get("hours", [])
        if current_hour not in allowed_hours:
            return False, f"Hour {current_hour} not in {allowed_hours}"
        
        # Check weekday if specified
        allowed_weekdays = config.get("weekdays", [0,1,2,3,4,5,6])
        if now.weekday() not in allowed_weekdays:
            return False, f"Weekday {now.weekday()} not in {allowed_weekdays}"
        
        # Check interval
        interval = config.get("interval_minutes", 60)
        if last_run:
            last_run_dt = datetime.fromisoformat(last_run)
            minutes_since = (now - last_run_dt).total_seconds() / 60
            if minutes_since < interval:
                return False, f"Ran {minutes_since:.0f} min ago, interval is {interval}"
        
        return True, f"Time-based run at {now.strftime('%H:%M')}"
    
    if condition == "always":
        # Check interval
        interval = config.get("interval_minutes", 60)
        if last_run:
            last_run_dt = datetime.fromisoformat(last_run)
            minutes_since = (now - last_run_dt).total_seconds() / 60
            if minutes_since < interval:
                return False, f"Ran {minutes_since:.0f} min ago, interval is {interval}"
        
        return True, f"Interval-based run ({interval} min)"
    
    return False, f"Unknown condition: {condition}"


def run_agent(script_name: str) -> tuple:
    """Run an agent script and return (success, output)."""
    script_path = SCRIPTS_DIR / script_name
    if not script_path.exists():
        return False, f"Script not found: {script_path}"
    
    try:
        result = subprocess.run(
            ['python3', str(script_path)],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=str(PADEL_DIR)
        )
        success = result.returncode == 0
        output = result.stdout + result.stderr
        return success, output
    except subprocess.TimeoutExpired:
        return False, "Timeout after 120 seconds"
    except Exception as e:
        return False, str(e)


def main():
    log("=" * 60)
    log("PADEL NEWS ORCHESTRATOR v1.0 STARTED")
    log("=" * 60)
    
    # Load states
    state = load_state()
    track_state = load_orchestrator_state()
    
    now = datetime.now()
    log(f"Current time: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    log(f"Tournament status: {state.get('current_tournament', {}).get('status', 'unknown')}")
    
    # Ensure last_runs dict exists
    if "last_runs" not in track_state:
        track_state["last_runs"] = {}
    
    agents_run = []
    
    # Check each agent in schedule
    for agent_name, config in SCHEDULE.items():
        should_run_now, reason = should_run(agent_name, config, state, track_state)
        
        if should_run_now:
            log(f"\n>>> Running {agent_name}: {reason}")
            log(f"    Script: {config['script']}")
            log(f"    Description: {config['description']}")
            
            success, output = run_agent(config["script"])
            
            if success:
                log(f"    ✓ SUCCESS")
                track_state["last_runs"][agent_name] = now.isoformat()
                agents_run.append(agent_name)
            else:
                log(f"    ✗ FAILED: {output[:200]}")
        else:
            log(f"    Skipping {agent_name}: {reason}")
    
    # Save updated state
    save_orchestrator_state(track_state)
    
    # Summary
    log("\n" + "=" * 60)
    log("SUMMARY")
    log("=" * 60)
    log(f"Agents run: {len(agents_run)}")
    for agent in agents_run:
        log(f"  - {agent}")
    
    if not agents_run:
        log("  (none - all agents within their interval)")
    
    log("=" * 60)
    log("ORCHESTRATOR COMPLETED")
    log("=" * 60)


if __name__ == "__main__":
    main()
