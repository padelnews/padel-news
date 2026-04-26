# Padel News Pro - Sistema de Agentes Automáticos

## 📌 RESUMEN

Este proyecto tiene **5 agentes automáticos** que actualizan el sitio web `padel_news/` según la fecha y eventos del Premier Padel Tour 2026.

---

## 🏃 AGENTES (scripts/)

### 1. index_agent.py
**Propósito:** Actualiza la página `index.html` con el último torneo y estadísticas.

**Schedule:** 08:00 y 20:00 diario

**Qué hace:**
- Lee `tournament_state.json` para saber cuál es el último torneo
- Genera HTML con: campeón, runner-up, score, prize, parejas, espectadores, sede
- Actualiza la sección "TORNEO DESTACADO" en index.html
- Commit + Push automático

**Archivo config:** `com.ai.padelnews.index.plist` (launchd)

---

### 2. calendar_agent.py
**Propósito:** Actualiza el calendario de torneos en `torneos.html` según la fecha actual.

**Schedule:** 08:00 y 20:00 diario

**Qué hace:**
- Compara la fecha actual con las fechas de cada torneo
- Cambia los badges:
  - Si pasó la fecha fin → "✓ Finalizado"
  - Si está entre inicio y fin → "🔴 En Curso"
  - Si es futuro → "Próximo"
- Añade sección "🏆 Último Ganador" con datos del tournament_state.json

**Torneos vigilados:**
```
Riyadh P1 (09-14 Feb) → automático
Gijón P2 (02-08 Mar) → automático
Cancún P2 (16-22 Mar) → automático
Miami P1 (23-29 Mar) → automático
Newgiza P2 (13-18 Abr) → automático
Brussels P2 (20-26 Abr) → automático
Asunción P1 (04-10 May) → automático
Buenos Aires P1 (11-17 May) → automático
Italy Major (01-07 Jun) → automático
Valencia P1 (08-14 Jun) → automático
Valladolid P2 (22-28 Jun) → automático
Bordeaux P2 (29 Jun-05 Jul) → automático
... (hasta Barcelona Finals Dic)
```

**Archivo config:** `com.ai.padelnews.calendar.plist` (launchd)

---

### 3. live_score_agent.py
**Propósito:** Actualiza los scores en vivo durante los torneos.

**Schedule:** Cada 2 horas

**Qué hace:**
- Descarga scores de FIP/Premier Padel (por implementar con Playwright)
- Por ahora usa datos hardcoded del tournament_progress.json
- Actualiza las secciones de resultados en index.html
- Commit + Push automático

**Estado:** En desarrollo (scraping no implementado aún)

**Archivo config:** `com.ai.padelnews.livescore.plist` (launchd)

---

### 4. rankings_agent.py
**Propósito:** Actualiza los rankings en `rankings.html`.

**Schedule:** Domingo a las 20:00

**Qué hace:**
- Descarga rankings oficiales FIP (por implementar)
- Por ahora usa datos hardcoded
- Actualiza tabs Masculino/Femenino
- Commit + Push automático

**Estado:** En desarrollo (scraping no implementado aún)

**Archivo config:** `com.ai.padelnews.rankings.plist` (launchd)

---

### 5. torneos_agent.py
**Propósito:** Actualiza la página `torneos.html` con el último torneo terminado.

**Schedule:** 08:00 y 20:00

**Qué hace:**
- Lee tournament_state.json
- Genera tarjeta del último torneo con ganador
- Actualiza la sección "TORNEO EN CURSO / ÚLTIMO TERMINADO"
- Commit + Push automático

**Nota:** Este agente complementa al calendar_agent. El calendar_agent cambia los estados y badges, este añade la tarjeta del winner.

**Archivo config:** `com.ai.padelnews.torneos.plist` (launchd)

---

## 📁 ARCHIVOS CLAVE

### Datos
- `data/tournament_state.json` → Estado actual del torneo (último torneo, próximo torneo)
- `data/tournament_progress.json` → Resultados por ronda
- `data/rankings_data.json` → Rankings FIP

### Páginas web
- `index.html` → Página principal
- `torneos.html` → Calendario de torneos
- `rankings.html` → Rankings masculino/femenino
- `resultados.html` → Resultados
- `actualidad.html` → Artículos/novedades
- `chollos.html` → Chollos (zapatillas padel)

### Estilos
- `css/style-futuristic.css` → CSS principal (NUNCA editar directamente, usar clases)

---

## 🔧 ACTIVAR/DESACTIVAR AGENTES

### Activar todos
```bash
launchctl load ~/Sites/padel_news/scripts/com.ai.padelnews.index.plist
launchctl load ~/Sites/padel_news/scripts/com.ai.padelnews.calendar.plist
launchctl load ~/Sites/padel_news/scripts/com.ai.padelnews.torneos.plist
launchctl load ~/Sites/padel_news/scripts/com.ai.padelnews.livescore.plist
launchctl load ~/Sites/padel_news/scripts/com.ai.padelnews.rankings.plist
```

### Desactivar todos
```bash
launchctl unload ~/Sites/padel_news/scripts/com.ai.padelnews.index.plist
launchctl unload ~/Sites/padel_news/scripts/com.ai.padelnews.calendar.plist
launchctl unload ~/Sites/padel_news/scripts/com.ai.padelnews.torneos.plist
launchctl unload ~/Sites/padel_news/scripts/com.ai.padelnews.livescore.plist
launchctl unload ~/Sites/padel_news/scripts/com.ai.padelnews.rankings.plist
```

### Script rápido
```bash
bash /Users/cristian/Sites/padel_news/scripts/activar_agentes.sh
```

### Ver estado
```bash
launchctl list | grep padelnews
```

---

## 🔄 ACTUALIZAR DATOS DE TORNEO

### Cuando termina un torneo:
1. Editar `data/tournament_state.json`:

```json
{
  "current_tournament": {
    "name": "Buenos Aires P1",
    "location": "Argentina",
    "start_date": "2026-05-11",
    "end_date": "2026-05-17",
    "prize": "$200,000",
    "category": "P1"
  },
  "last_tournament": {
    "name": "Asunción P1",
    "location": "Paraguay",
    "start_date": "2026-05-04",
    "end_date": "2026-05-10",
    "champions": ["Juan Lebrón", "Leo Augsburger"],
    "champion_country": ["España", "Argentina"],
    "runner_up": ["Agustín Tapia", "Arturo Coello"],
    "final_score_detailed": "2-6, 6-3, 6-3",
    "prize": "$35,000",
    "participants": 32,
    "spectators": 2847,
    "venue": "Royal Paddel Club"
  }
}
```

2. Ejecutar agentes manualmente:
```bash
python3 /Users/cristian/Sites/padel_news/scripts/calendar_agent.py
python3 /Users/cristian/Sites/padel_news/scripts/index_agent.py
python3 /Users/cristian/Sites/padel_news/scripts/torneos_agent.py
```

---

## 📅 LÓGICA DE FECHAS (calendar_agent)

```
Si hoy < fecha_inicio → "Próximo"
Si fecha_inicio <= hoy <= fecha_fin → "🔴 En Curso"
Si hoy > fecha_fin → "✓ Finalizado"
```

### Ejemplo práctico:
- Hoy: 26 Abril 2026
- Brussels P2 (20-26 Abr) → Finalizado ✓
- Asunción P1 (04-10 May) → Próximo

Cuando llegue 4 Mayo:
- Asunción P1 → En Curso 🔴
- Brussels P2 → Finalizado ✓

Cuando llegue 11 Mayo:
- Asunción P1 → Finalizado ✓ + sección GANADORES se añade
- Buenos Aires P1 → En Curso 🔴

---

## ⚠️ REGLAS IMPORTANTES

1. **NUNCA editar CSS inline** - Usar clases de `style-futuristic.css`
2. **Siempre actualizar tournament_state.json** cuando termine un torneo
3. **Los agentes solo actualizan secciones específicas** - No reescriben páginas enteras
4. **Los launchd agents están desacticados por defecto** - Activar con launchctl load

---

## 🐛 SOLUCIÓN DE PROBLEMAS

### Agente no se ejecuta
```bash
# Ver logs
cat ~/Sites/padel_news/scripts/calendar_agent.log
cat ~/Sites/padel_news/scripts/calendar_agent.err

# Ver si está cargado
launchctl list | grep padelnews
```

### Forzar ejecución manual
```bash
python3 /Users/cristian/Sites/padel_news/scripts/calendar_agent.py --dry-run
python3 /Users/cristian/Sites/padel_news/scripts/index_agent.py --dry-run
```

### Git no hace push
```bash
cd /Users/cristian/Sites/padel_news
git status
git log --oneline -3
```

---

## 📂 ESTRUCTURA DEL SITIO

```
padel_news/
├── index.html          # Página principal
├── rankings.html       # Rankings M/F
├── torneos.html       # Calendario + Winners
├── resultados.html    # Resultados
├── actualidad.html    # Artículos
├── chollos.html       # Chollos padel
├── css/
│   └── style-futuristic.css
├── data/
│   ├── tournament_state.json    # Estado actual
│   ├── tournament_progress.json # Resultados
│   └── rankings_data.json       # Rankings
├── images/
│   └── players/                 # Fotos jugadores
├── scripts/
│   ├── index_agent.py
│   ├── calendar_agent.py
│   ├── live_score_agent.py
│   ├── rankings_agent.py
│   ├── torneos_agent.py
│   ├── activar_agentes.sh
│   └── *.plist                  # Config launchd
└── README_AGENTS.md            # Este archivo
```

---

## 🌐 REPOSITORIO

- **GitHub:** https://github.com/padelnews/padel-news.git
- **Live:** https://padelnews.github.io/padel-news/

---

*Última actualización: 26 Abril 2026*
