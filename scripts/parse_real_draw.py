#!/usr/bin/env python3
"""
Parse REAL draw from Premier Padel website text extraction.
"""

import json
from datetime import datetime
from pathlib import Path

# Read extracted text
with open('/tmp/pp_all_text.txt', 'r') as f:
    text = f.read()

# Split into lines
lines = [l.strip() for l in text.split('\n') if l.strip()]

# Find R32 section and parse matches
# Format: Player1, Player2, score1, score2, score3 (if exists)

def parse_round(lines, start_idx, num_matches):
    """Parse matches from lines starting at start_idx."""
    matches = []
    idx = start_idx
    
    for i in range(num_matches):
        if idx >= len(lines):
            break
        
        # Check for BYE
        if lines[idx] == 'BYE':
            idx += 1
            continue
        
        # Get player names
        player1 = lines[idx]
        player2 = lines[idx+1] if idx+1 < len(lines) else ''
        idx += 2
        
        # Get scores (could be 2 or 3 sets)
        scores = []
        while idx < len(lines) and lines[idx].isdigit():
            scores.append(lines[idx])
            idx += 1
        
        # Build score string
        if len(scores) >= 4:  # 3 sets
            score = f"{scores[0]}-{scores[1]}, {scores[2]}-{scores[3]}"
            if len(scores) >= 6:
                score += f", {scores[4]}-{scores[5]}"
        elif len(scores) >= 2:  # 2 sets
            score = f"{scores[0]}-{scores[1]}, {scores[2]}-{scores[3]}" if len(scores) >= 4 else f"{scores[0]}-{scores[1]}, {scores[2]}-{scores[3]}"
        else:
            score = ''
        
        matches.append({
            'player1': player1,
            'player2': player2,
            'score': score,
            'scores_raw': scores
        })
    
    return matches, idx

# Find start of R32 section
r32_start = lines.index('R32') + 1 if 'R32' in lines else 0

# Parse R32 matches (should be around 16 matches)
print(f"Parsing from index {r32_start}")

# Manual parsing based on the text structure
matches_r32 = []
idx = r32_start

# Skip "Principales" if present
if idx < len(lines) and lines[idx] == 'Principales':
    idx += 1

# Parse 16 R32 matches
for i in range(16):
    if idx >= len(lines):
        break
    
    if lines[idx] == 'BYE':
        idx += 1
        continue
    
    p1 = lines[idx] if idx < len(lines) else ''
    p2 = lines[idx+1] if idx+1 < len(lines) else ''
    idx += 2
    
    # Collect scores
    scores = []
    while idx < len(lines) and lines[idx].isdigit() and int(lines[idx]) <= 7:
        scores.append(lines[idx])
        idx += 1
    
    # Build score string
    if len(scores) >= 4:
        score = f"{scores[0]}-{scores[1]}, {scores[2]}-{scores[3]}"
    else:
        score = ''
    
    matches_r32.append({'p1': p1, 'p2': p2, 'score': score, 'scores': scores})

print(f"Parsed {len(matches_r32)} R32 matches")
for i, m in enumerate(matches_r32[:5]):
    print(f"  {i+1}. {m['p1']} / {m['p2']} - {m['score']}")

# Now find R16 section
r16_start = lines.index('R16') + 1 if 'R16' in lines else 0
print(f"\nR16 starts at index {r16_start}")

# Parse R16 - these are the winners of R32
matches_r16 = []
idx = r16_start

for i in range(8):
    if idx >= len(lines):
        break
    
    p1 = lines[idx] if idx < len(lines) else ''
    p2 = lines[idx+1] if idx+1 < len(lines) else ''
    idx += 1
    
    # Check if there's a score (some matches finished)
    scores = []
    while idx < len(lines) and lines[idx].isdigit() and int(lines[idx]) <= 7:
        scores.append(lines[idx])
        idx += 1
    
    if len(scores) >= 4:
        score = f"{scores[0]}-{scores[1]}, {scores[2]}-{scores[3]}"
        status = 'finished'
    else:
        score = ''
        status = 'scheduled'
    
    matches_r16.append({'p1': p1, 'p2': p2, 'score': score, 'status': status, 'scores': scores})

print(f"\nParsed {len(matches_r16)} R16 matches")
for i, m in enumerate(matches_r16):
    print(f"  {i+1}. {m['p1']} vs {m['p2']} - {m['score']} [{m['status']}]")
