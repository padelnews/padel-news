#!/usr/bin/env python3
"""
Padel News Dynamic Flow v3.0
===========================
Main orchestrator for automatic website updates.

Flow:
1. Load state
2. Check for tournament updates (scrape/premierpadel)
3. Detect if tournament ended
4. If ended: transition to next tournament
5. Generate all pages from state
6. Validate generated pages
7. If validation passes: deploy to GitHub

CRON: Runs every 5 minutes via launchd
"""

import json
import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime

# Add scripts directory to path
SCRIPT_DIR = Path(__file__).parent
PADEL_DIR = Path("/Users/cristian/Sites/padel_news")
STATE_FILE = PADEL_DIR / "scripts" / "tournament_state.json"
LOG_FILE = PADEL_DIR / "scripts" / "dynamic_flow.log"


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
    except Exception as e:
        log(f"ERROR loading state: {e}")
        return {}


def save_state(state: dict) -> bool:
    """Save state to JSON file."""
    try:
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        log(f"ERROR saving state: {e}")
        return False


def run_script(script_name: str) -> Tuple[bool, str]:
    """Run a Python script and return (success, output)."""
    script_path = SCRIPT_DIR / script_name
    try:
        result = subprocess.run(
            ['python3', str(script_path)],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(PADEL_DIR)
        )
        return result.returncode == 0, result.stdout + result.stderr
    except Exception as e:
        return False, str(e)


def check_official_results() -> dict:
    """
    Check official Premier Padel for tournament results.
    Returns dict with 'finished' bool and 'results' if available.
    """
    # TODO: Implement actual scraping from premierpadel.com
    # For now, returns empty - human will update state manually
    
    state = load_state()
    current = state.get("current_tournament", {})
    
    # If current tournament is 'upcoming' and date has passed, prompt for update
    # This is where automatic detection would go
    
    return {"finished": False, "results": None}


def transition_to_next_tournament(state: dict) -> dict:
    """
    Transition from current tournament to next one.
    Called when a tournament is confirmed as finished.
    """
    log("Transitioning to next tournament...")
    
    # Move current to past
    current = state.get("current_tournament", {})
    if current.get("status") != "upcoming":
        # Create past entry
        past_entry = {
            "id": current.get("id"),
            "name": current.get("name"),
            "location": current.get("location"),
            "dates": current.get("dates"),
            "status": "finished",
            "finished_at": datetime.now().isoformat()
        }
        
        # Check if already in past
        past_ids = [t.get("id") for t in state.get("past_tournaments", [])]
        if current.get("id") not in past_ids:
            state["past_tournaments"].insert(0, past_entry)
    
    # Promote first upcoming to current
    upcoming = state.get("upcoming_tournaments", [])
    if upcoming:
        next_t = upcoming.pop(0)
        state["current_tournament"] = {
            "id": next_t.get("id"),
            "name": next_t.get("name"),
            "location": next_t.get("location"),
            "dates": next_t.get("dates"),
            "status": "upcoming",
            "prize_money": next_t.get("prize_money", "€264,534"),
            "venue": next_t.get("location")
        }
        log(f"Promoted '{next_t.get('name')}' to current tournament")
    
    save_state(state)
    return state


def main():
    log("=" * 60)
    log("DYNAMIC FLOW v3.0 STARTED")
    log("=" * 60)
    
    # Step 1: Load current state
    state = load_state()
    if not state:
        log("ERROR: No state file found. Run website_generator.py first.")
        sys.exit(1)
    
    log(f"Current tournament: {state.get('current_tournament', {}).get('name', 'Unknown')}")
    log(f"Status: {state.get('current_tournament', {}).get('status', 'Unknown')}")
    
    # Step 2: Check official results (placeholder for real scraping)
    # TODO: Uncomment when scraping is implemented
    # results = check_official_results()
    # if results.get("finished"):
    #     log("Tournament detected as FINISHED!")
    #     # Update state with results
    #     transition_to_next_tournament(state)
    
    # Step 3: Generate all pages from state
    log("\n--- Generating pages from state ---")
    success, output = run_script("website_generator.py")
    if success:
        log("Pages generated successfully")
    else:
        log(f"ERROR generating pages: {output}")
        sys.exit(1)
    
    # Step 4: Validate generated pages
    log("\n--- Validating pages ---")
    success, output = run_script("validator.py")
    if success:
        log("Validation passed")
    else:
        log(f"VALIDATION FAILED: {output}")
        log("NOT deploying to GitHub until errors are fixed")
        sys.exit(1)
    
    # Step 5: Deploy to GitHub
    log("\n--- Deploying to GitHub ---")
    try:
        subprocess.run(['git', 'add', '-A'], cwd=str(PADEL_DIR), timeout=10)
        subprocess.run(['git', 'commit', '-m', f'Auto-update: {datetime.now().strftime("%Y-%m-%d %H:%M")}'], 
                     cwd=str(PADEL_DIR), timeout=10)
        result = subprocess.run(['git', 'push', 'origin', 'main'], 
                              cwd=str(PADEL_DIR), timeout=30,
                              capture_output=True, text=True)
        if result.returncode == 0:
            log("Deployed to GitHub successfully")
        else:
            log(f"Git push failed: {result.stderr}")
    except Exception as e:
        log(f"ERROR deploying: {e}")
        sys.exit(1)
    
    log("=" * 60)
    log("DYNAMIC FLOW v3.0 COMPLETED")
    log("=" * 60)


if __name__ == "__main__":
    main()
