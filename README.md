# 🎾 Padel News Pro

Professional World Padel Tour news portal with real-time data.

## Content Philosophy

**ORIGINAL & UNIQUE** - All content is synthesized from multiple authoritative sources:
- Never copy-paste from other sites
- Combine information from 5+ sources per article
- Create unique summaries with added value
- Transparent source attribution

## Data Files

All dynamic content is stored in `/data/` as JSON:

| File | Content | Updated |
|------|---------|---------|
| `noticias.json` | 7 news articles with unique summaries | Manual + AI synthesis |
| `resultados.json` | Match results from 4 tournaments | Manual + verified data |
| `torneos.json` | Rankings, active tours, statistics | Manual + FIP data |

## Sources Used

- MundoDeportivo.com
- PadelFIP.com (official rankings)
- MundiPadel.com
- Sport.es
- Padelandia.com
- Padel-Magazine.es
- Actu-Padel.com
- PadelStar.es

## Website Structure

```
padel_news/
├── index.html          # Home page
├── actualidad.html     # News (loads noticias.json)
├── resultados.html     # Results (loads resultados.json)
├── torneos.html        # Rankings (loads torneos.json)
├── css/
│   └── style.css       # Professional WPT-inspired styling
├── scripts/
│   ├── app.js          # Dynamic content loader
│   └── fetch_news.py   # Future: automated fetching
└── data/
    ├── noticias.json
    ├── resultados.json
    └── torneos.json
```

## How It Works

1. **HTML pages** load and show loading state
2. **app.js** fetches JSON data files
3. **Dynamic rendering** populates content
4. **Source attribution** displayed on each news card

## Adding New Content

### Add a News Article

Edit `data/noticias.json`:

```json
{
  "id": 8,
  "titulo": "Your unique headline",
  "resumen": "2-3 sentence summary synthesized from multiple sources",
  "fecha": "2026-04-25",
  "categoria": "Ranking|Torneos|Jugadores|Fichajes|Circuitos",
  "imagen": "/images/noticias/slug-image.jpg",
  "fuente_sintetizada": "Source1 + Source2 + Source3"
}
```

### Add Match Results

Edit `data/resultados.json` with tournament structure.

### Update Rankings

Edit `data/torneos.json` ranking arrays.

## Local Testing

Open `index.html` in a browser or run:

```bash
cd /Users/cristian/Sites/padel_news
python3 -m http.server 8000
# Visit http://localhost:8000
```

## Future Enhancements

- [ ] Automated RSS feed parsing
- [ ] Premier Padel API integration
- [ ] Cron job for daily updates
- [ ] Image generation for news cards
- [ ] Social media auto-posting

---

**Last Updated:** April 25, 2026
**Content Approach:** Human-curated + AI-synthesized summaries
