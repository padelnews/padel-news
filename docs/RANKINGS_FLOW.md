# Rankings Update Flow

## Overview
This system automatically updates the rankings page from FIP official data.

## Files

### Data Flow
```
FIP Website (ranking-male/, ranking-female/)
       ↓
rankings_fetch.py → data/rankings_data.json
       ↓
update_rankings.py → rankings.html
       ↓
GitHub (padel-news)
```

### Files Created
- `scripts/rankings_fetch.py` - Fetches rankings from FIP
- `scripts/update_rankings.py` - Generates rankings.html
- `scripts/com.ai.padelnews.rankings.plist` - Cron job config (macOS launchd)
- `data/rankings_data.json` - Fresh rankings data
- `data/last_fetch.txt` - Timestamp of last fetch

## Manual Update

### Step 1: Fetch new data
```bash
cd /Users/cristian/Sites/padel_news
python3 scripts/rankings_fetch.py
```

### Step 2: Update HTML
```bash
python3 scripts/update_rankings.py
```

### Step 3: Commit & push
```bash
cd /Users/cristian/Sites/padel_news
git add rankings.html data/
git commit -m "UPDATE: Rankings from FIP $(date +%Y-%m-%d)"
git push origin main
```

## Automatic (Cron)

The plist file schedules updates every Sunday at 20:00.

To install:
```bash
launchctl load /Users/cristian/Sites/padel_news/scripts/com.ai.padelnews.rankings.plist
```

## Agent Instructions

When running rankings update task:
1. Run `python3 scripts/rankings_fetch.py`
2. Check `data/rankings_data.json` for fresh data
3. If data looks correct, run `python3 scripts/update_rankings.py`
4. Commit with message: "UPDATE: Rankings from FIP [DATE]"
5. Push to GitHub

## Fallback Data

If FIP website is down or parsing fails, the script falls back to
manually verified data stored in `rankings_fetch.py` → `get_fallback_rankings()`.

To update fallback data:
1. Visit https://www.padelfip.com/ranking-male/
2. Copy top 10 pairs manually
3. Edit `get_fallback_rankings()` in rankings_fetch.py

## Current Data (Manually Verified)
- Source: FIP Official
- Last verified: 2026-04-26
- Male #1: Tapia/Coello (20,910 pts)
- Female #1: Josemaría/González (17,660 pts)

## Troubleshooting

**Problem:** Script fails to fetch
**Solution:** Check internet connection, try again later, or use fallback data

**Problem:** Data looks wrong
**Solution:** Manually verify at padelfip.com, update fallback data

**Problem:** Cron not running
**Solution:** Check with `launchctl list | grep padelnews`