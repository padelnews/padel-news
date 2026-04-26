# 🤖 FLUJO AUTOMÁTICO - PADEL NEWS PRO
## Sin intervención humana - Todo se actualiza solo

---

## 🎯 RESUMEN EJECUTIVO

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CÓMO FUNCIONA TODO SOLO                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  DÍA CUALQUIERA (06:00)                                                    │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  LIVE_SCORE_AGENT (launchd cada 2h)                                 │    │
│  │  ├── Descarga resultados de FIP/Premier Padel                     │    │
│  │  ├── Actualiza tournament_progress.json                            │    │
│  │  └── Si detecta torneo en curso → actualiza web                    │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  INDEX_AGENT (launchd 08:00 y 20:00)                               │    │
│  │  ├── Lee tournament_state.json + tournament_progress.json           │    │
│  │  ├── Genera sección del torneo según estado                         │    │
│  │  │   ├── upcoming → countdown                                       │    │
│  │  │   ├── in_progress → cuartos/semis/final + scores               │    │
│  │  │   └── finished → campeón + resultado                            │    │
│  │  ├── Actualiza index.html                                          │    │
│  │  └── Commit + Push automático                                       │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  DÍA DE CAMBIO DE TORNEO (automatic_flow.py)                               │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  DYNAMIC_FLOW                                                       │    │
│  │  ├── Detecta que terminó un torneo                                  │    │
│  │  ├── Actualiza tournament_state.json con nuevo torneo               │    │
│  │  ├── Crea artículo en actualidad.html                              │    │
│  │  ├── Resetea tournament_progress.json                              │    │
│  │  └── Commit + Push                                                  │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  DOMINGO 20:00 (RANKINGS)                                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  RANKINGS_AGENT                                                     │    │
│  │  ├── Ejecuta rankings_fetch.py → descarga de FIP                   │    │
│  │  ├── Actualiza rankings_data.json                                   │    │
│  │  ├── Genera rankings.html                                          │    │
│  │  └── Commit + Push                                                  │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📅 CALENDARIO DE TORNEOS 2026

El sistema sabe las fechas y cambia automáticamente:

| Torneo | Fecha | Status en Web |
|--------|-------|---------------|
| Asunción P1 | 4-10 Mayo | 🔴 EN CURSO (cuando llegue la fecha) |
| Buenos Aires P1 | 11-17 Mayo | 🔴 EN CURSO |
| Rome Major | 1-7 Junio | 🔴 EN CURSO |

---

## 🔄 FLUJO DÍA A DÍA

### 1. ANTES DEL TORNEO (ejemplo: 3 Mayo, un día antes de Asunción)

```
06:00 → LIVE_SCORE_AGENT
        Estado: upcoming
        No hace nada específico, solo verifica

08:00 → INDEX_AGENT
        Ve: status = "upcoming"
        Muestra: "8 días para Asunción P1"
        Actualiza index.html
        Commit + Push ✅
```

### 2. PRIMER DÍA DEL TORNEO (4 Mayo)

```
06:00 → LIVE_SCORE_AGENT
        Detecta: today >= start_date
        Actualiza: status → "in_progress"
        Descarga emparejamientos de FIP
        Guarda en tournament_progress.json

08:00 → INDEX_AGENT
        Ve: status = "in_progress"
        Detecta: día 1 del torneo
        Muestra: "Round of 32" + partidos
        Actualiza index.html
        Commit + Push ✅
```

### 3. DÍA DE CUARTOS (ejemplo: 8 Mayo)

```
06:00 → LIVE_SCORE_AGENT
        Detecta: día 5 del torneo
        Actualiza: current_round → "quarters"
        Descarga resultados de octavos
        Actualiza scores en progress.json

08:00 → INDEX_AGENT
        Ve: status = "in_progress", current_round = "quarters"
        Muestra: "CUARTOS DE FINAL" + 4 partidos
        Actualiza index.html
        Commit + Push ✅
```

### 4. DÍA DE FINAL (10 Mayo)

```
06:00 → LIVE_SCORE_AGENT
        Detecta: día 7 del torneo
        Actualiza: current_round → "final"
        Descarga resultado final

08:00 → INDEX_AGENT
        Ve: status = "in_progress", current_round = "final"
        Muestra: FINAL + partido + score
        Actualiza index.html
        Commit + Push ✅
```

### 5. EL DÍA QUE TERMINA (11 Mayo)

```
06:00 → LIVE_SCORE_AGENT
        Detecta: today > end_date
        Actualiza: status → "finished"
        
        DYNAMIC_FLOW (triggered)
        ├── Detecta: status = "finished"
        ├── Crea artículo de Asunción en actualidad
        ├── Busca próximo torneo: Buenos Aires P1
        ├── Actualiza state con nuevo torneo
        ├── Resetea progress.json
        └── Commit + Push ✅

08:00 → INDEX_AGENT
        Ve: status = "upcoming" (nuevo torneo)
        Muestra: countdown para Buenos Aires
        Commit + Push ✅
```

---

## 📊 DATOS COMPARTIDOS

### tournament_state.json
```json
{
  "current_tournament": {
    "name": "Asunción P1",
    "location": "Paraguay",
    "start_date": "2026-05-04",
    "end_date": "2026-05-10"
  },
  "status": "in_progress",
  "last_index_update": "2026-05-08"
}
```

### tournament_progress.json
```json
{
  "tournament": "Asunción P1",
  "current_round": "quarters",
  "matches": {
    "quarters": [
      {"team1": "Tapia/Coello", "team2": "Stupaczuk/Yanguas", "score": "6-4 4-6", "status": "finished"},
      {"team1": "Galán/Chingotto", "team2": "Lebrón/Augsburger", "score": "", "status": "pending"}
    ]
  }
}
```

---

## ⚡ AGENTES Y SUS HORARIOS

| Agente | Schedule | Qué hace |
|--------|----------|----------|
| `live_score_agent.py` | Cada 2h (launchd) | Scrapes FIP, actualiza scores |
| `index_agent.py` | 08:00 y 20:00 | Actualiza página inicio |
| `dynamic_flow.py` | Cada 5 min | Detecta cambios de torneo |
| `rankings_agent.py` | Domingo 20:00 | Actualiza rankings |

---

## 🚀 ACTIVAR/DESACTIVAR

```bash
# Activar todos los agentes
launchctl load ~/Sites/padel_news/scripts/com.ai.padelnews.livescore.plist
launchctl load ~/Sites/padel_news/scripts/com.ai.padelnews.index.plist

# Ver si están activos
launchctl list | grep padelnews

# Ver logs
cat ~/Sites/padel_news/scripts/live_score_agent.log
cat ~/Sites/padel_news/scripts/index_agent.log

# Ejecutar manualmente
python3 ~/Sites/padel_news/scripts/live_score_agent.py
python3 ~/Sites/padel_news/scripts/index_agent.py --force
```

---

## 🎓 CÓMO EL SISTEMA APRENDE

```
El sistema NO necesita que le digas nada.

1. SAVES las fechas de torneos en tournament_state.json
2. LIVE_SCORE_AGENT scrapea FIP cada 2 horas
3. INDEX_AGENT actualiza la web automáticamente
4. Si hay error, el agente loguea y sigue intentando
5. El siguiente ciclo reintenta

TÚ NO HACES NADA. El sistema funciona solo.
```

---

## ❓ PREGUNTAS FRECUENTES

**P: ¿De dónde sacan los datos?**
R: De FIP (padelfip.com) y Premier Padel (premierpadel.com)

**P: ¿Qué pasa si no hay torneo?**
R: El agente detecta status="upcoming" y muestra countdown del próximo

**P: ¿Puedo ver qué hará antes de que pase?**
R: Sí: `python3 scripts/index_agent.py --dry-run`

**P: ¿Qué pasa si falla el scrapeo?**
R: El agente usa datos en cache y reintenta en 2 horas

**P: ¿Cuándo sale el Artikel de cada torneo?**
R: Automatically cuando termina el torneo (dynamic_flow.py)
