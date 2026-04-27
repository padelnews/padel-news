# 🏢 OFICINA PADEL NEWS PRO
## Sistema Multi-Agente para Gestión Automatizada

```
╔═══════════════════════════════════════════════════════════════════════════════════╗
║                         PADEL NEWS PRO - SALA DE CONTROL                          ║
╠═══════════════════════════════════════════════════════════════════════════════════╣
║                                                                                   ║
║   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            ║
║   │  🏠 INDEX    │  │  📊         │  │  📰         │  │  🏆         │            ║
║   │  AGENT      │  │  RANKINGS   │  │  ACTUALIDAD │  │  RESULTADOS │            ║
║   │             │  │  AGENT      │  │  AGENT      │  │  AGENT      │            ║
║   │ Encargado   │  │             │  │             │  │             │            ║
║   │ del home    │  │ Encargado   │  │ Encargado   │  │ Encargado   │            ║
║   │ principal   │  │ de rankings│  │ de noticias│  │ de cuadros │            ║
║   └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘            ║
║         │                │                │                │                     ║
║         ▼                ▼                ▼                ▼                     ║
║   ┌─────────────────────────────────────────────────────────────────┐            ║
║   │                    📁 BASE DE DATOS COMPARTIDA                  │            ║
║   │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │            ║
║   │  │tournament_   │  │ rankings_    │  │ articles_    │          │            ║
║   │  │state.json    │  │ data.json    │  │ data.json    │          │            ║
║   │  └──────────────┘  └──────────────┘  └──────────────┘          │            ║
║   └─────────────────────────────────────────────────────────────────┘            ║
║                                    │                                               ║
║   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            ║
║   │  🎯 TORNEOS │  │  🛒 CHOLLOS │  │  📹 VIDEO   │  │  🔴 LIVE    │            ║
║   │  AGENT      │  │  AGENT      │  │  AGENT      │  │  AGENT      │            ║
║   │             │  │             │  │             │  │             │            ║
║   │ Encargado   │  │ Encargado   │  │ Encargado   │  │ Encargado   │            ║
║   │ calendario │  │ del market  │  │ highlights  │  │ scores     │            ║
║   └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘            ║
║                                                                                   ║
╚═══════════════════════════════════════════════════════════════════════════════════╝
```

---

## 🏠 AGENTE INDEX (Home Page)

### 📋 MISIÓN
Gestionar la página principal: mostrar el torneo actual con progreso, emparejamientos, scores.

**El agente detecta automáticamente:**
- 🕐 **ANTES del torneo:** Muestra countdown + info del próximo torneo
- 🔴 **DURANTE el torneo:** Muestra ronda actual (cuartos/semis/final) + partidos + scores
- ✅ **DESPUÉS del torneo:** Muestra campeón + resultado final

### 📂 ARCHIVOS QUE CONTROLA
- `index.html` - Página principal
- `data/tournament_state.json` - Estado del torneo (estado, fechas, tipo)
- `data/tournament_progress.json` - Progreso (ronda actual, partidos, scores)
- `scripts/index_agent.py` - Script principal del agente

### 🔄 FLUJO DE ACTUALIZACIÓN

```
1. Leer tournament_state.json
   → ¿status = upcoming / in_progress / finished?

2. SI in_progress:
   → Mostrar ronda actual (Cuartos/Semis/Final)
   → Mostrar partidos con equipos y scores
   → Si hay partido en vivo, marcar con 🔴 EN VIVO

3. SI upcoming:
   → Mostrar countdown: "X días para que empiece"
   → Info: nombre, ubicación, fechas, premio

4. SI finished:
   → Mostrar campeón + runner-up + score final
   → Stats del torneo

5. Actualizar index.html (solo la sección torneo, no tocar 3 columnas)
6. Commit + Push automático
```

### ⚠️ REGLAS CRÍTICAS
- **SOLO modificar la sección del torneo**, nunca las 3 columnas inferiores
- **Scores reales solo** - no inventar resultados (el usuario los ve en TV)
- **Formato consistente** - usar el mismo HTML structure siempre

### 📊 TRIGGER (Cuándo ejecutarse)
- **Automatic schedule:** Cada día 08:00 y 20:00 via launchd
- **Cuando cambia tournament_state.json**
- **Manual:** `python3 scripts/index_agent.py --force`

### 📁 DATOS DEL PRÓXIMO TORNEO
```json
{
  "current_tournament": {
    "name": "Asunción P1",
    "location": "Paraguay",
    "start_date": "2026-05-04",
    "end_date": "2026-05-10",
    "prize": "$200,000"
  },
  "status": "upcoming"
}
```

---

## 📊 AGENTE RANKINGS

### 📋 MISIÓN
Gestionar rankings oficiales: descargar datos de FIP, generar tabla, mantener formato.

### 📂 ARCHIVOS QUE CONTROLA
- `rankings.html` - Página de rankings
- `data/rankings_data.json` - Source of truth
- `scripts/rankings_fetch.py` - Descarga datos
- `scripts/update_rankings.py` - Genera HTML

### 🔄 FLUJO DE ACTUALIZACIÓN

```
1. EJECUTAR rankings_fetch.py
   → Descarga de padelfip.com/ranking-male/ y /ranking-female/
   → Guarda en data/rankings_data.json
   
2. SI fetch exitoso:
   → EJECUTAR update_rankings.py
   → Lee JSON → genera HTML
   → Mantiene estilo de tabla (.rankings-table, .top-3, .points)
   
3. SI fetch falla:
   → Usar fallback data del JSON existente
   → Loguear error
   
4. Commit + Push
```

### ⚠️ REGLAS CRÍTICAS
- **SOLO rankings POR PAREJAS** (no individual)
- **NUNCA inventar datos** - usar fuente oficial
- Mantener formato tabla consistente
- Incluir fecha de última actualización

### 📊 TRIGGER (Cuándo ejecutarse)
- Cada domingo 20:00 via launchd
- Manual: `python3 scripts/update_rankings.py --force`

---

## 📰 AGENTE ACTUALIDAD

### 📋 MISIÓN
Gestionar artículos de noticias: crear, actualizar, mantener estructura.

### 📂 ARCHIVOS QUE CONTROLA
- `actualidad.html` - Página de noticias
- `articles/article-*.html` - Artículos individuales
- `data/articles_data.json` - Índice de artículos

### 🔄 FLUJO DE ACTUALIZACIÓN

```
1. DETECTAR nuevo artículo necesario
   → Leer tournament_state.json
   → SI nuevo torneo finalizado SIN artículo → CREAR
   
2. GENERAR artículo siguiendo plantilla:
   → article-newgiza-2026.html como referencia
   → Incluir: highlight-box, article-gallery, resultados-box, prize-money
   
3. ACTUALIZAR actualidad.html
   → Añadir card del nuevo artículo
   → Mantener orden cronológico (más nuevo primero)
   → NO romper estructura de news-grid
   
4. Commit + Push
```

### ⚠️ REGLAS CRÍTICAS
- **FOTOS realEs** - usar de FIP con créditos debajo
- **Estructura clone** - seguir exactamente article-newgiza-2026.html
- **Badges** - usar clases .badge-campeones, .badge-final, .badge-live
- **Galería** - 3 fotos mínimo con figcaption y créditos FIP

### 📊 TRIGGER (Cuándo ejecutarse)
- Cuando `tournament_state.json` indica torneo finalizado
- Manual: crear artículo nuevo

---

## 🏆 AGENTE RESULTADOS

### 📋 MISIÓN
Gestionar página de resultados: cuadro de torneo, scores, Ordnung.

### 📂 ARCHIVOS QUE CONTROLA
- `resultados.html` - Página principal
- `data/tournament_results.json` - Resultados guardados

### 🔄 FLUJO DE ACTUALIZACIÓN

```
1. LEER tournament_state.json
   → Detectar torneo activo o finalizado
   
2. SI torneo activo:
   → Activar live score banner
   → Mostrar partido actual con scores
   
3. SI torneo finalizado:
   → Añadir a sección "Torneos Finalizados"
   → Mostrar: campeón, marcador final, pista central
   → Mantener orden: próximos primero, luego finalizados
   
4. MANTENER formato consistente:
   → .results-section, .match-card, .winner-badge
   → Tabla con scroll horizontal
```

### ⚠️ REGLAS CRÍTICAS
- **NO mezclar resultados** de torneos diferentes
- **Orden correcto**: próximos (cronológico) → finalizados (más reciente primero)
- **Scores completos**: no dejar "pendiente" si terminó
- **Live solo si hay partido** - no mostrar cuando no hay

### 📊 TRIGGER (Cuándo ejecutarse)
- Cada 2 minutos cuando hay torneo en curso
- Cuando torneo finaliza
- Cada hora via cron para verificar

---

## 🎯 AGENTE TORNEOS

### 📋 MISIÓN
Gestionar calendario de torneos: upcoming, en curso, finalizados.

### 📂 ARCHIVOS QUE CONTROLA
- `torneos.html` - Página de calendario
- `data/tournament_state.json` - Estado actual

### 🔄 FLUJO DE ACTUALIZACIÓN

```
1. LEER tournament_state.json
   → Ver estado: upcoming / in_progress / finished
   
2. ACTUALIZAR tournaments.html:
   → SI upcoming: mostrar countdown + info
   → SI in_progress: mostrar banner "EN CURSO"
   → SI finished: mostrar badge ✅
   
3. Mantener grid de torneos
   → Cards con: nombre, fecha, ubicación, estado, prize
   → Estilo: .tournament-card, .status-badge
```

### ⚠️ REGLAS CRÍTICAS
- **Un torneo = un card** - no duplicar
- **Estados coherentes** - no mostrar "en curso" si terminó
- **Prize money visible** - siempre mostrar cantidad

### 📊 TRIGGER (Cuándo ejecutarse)
- Cada 6 horas via cron
- Cuando cambia tournament_state.json

---

## 🛒 AGENTE CHOLLOS

### 📋 MISIÓN
Vigilar chollos de palas y encontrar mejores precios.

### 📂 ARCHIVOS QUE CONTROLA
- `chollos.html` - Página de chollos
- `scripts/chollos_monitor.py` - Monitor de precios

### 🔄 FLUJO DE ACTUALIZACIÓN

```
1. EJECUTAR chollos_monitor.py
   → Revisar Amazon, PC componentes, etc.
   → Buscar chollos de palas padel
   
2. FILTRAR:
   → Solo productos con descuento ≥30%
   → Solo palas (no accesorios)
   → Solo en stock
   
3. ACTUALIZAR chollos.html
   → Grid de productos con: imagen, nombre, precio, descuento
   → Estilo: .chollo-card, .price-old, .price-new
   → Ordenar por % descuento (mayor primero)
   
4. Commit + Push
```

### 📊 TRIGGER (Cuándo ejecutarse)
- Cada 4 horas via cron
- Manual: `python3 scripts/chollos_monitor.py`

---

## 📹 AGENTE VIDEO

### 📋 MISIÓN
Gestionar sección de videos/higlights.

### 📂 ARCHIVOS QUE CONTROLA
- `index.html` (sección videos)
- `data/video_urls.json` - URLs de videos

### 🔄 FLUJO DE ACTUALIZACIÓN

```
1. LEER video_urls.json
   → Verificar que URLs siguen activas (YouTube)
   
2. SI video caído:
   → Buscar replacement en canal Premier Padel
   → Actualizar JSON
   
3. MANTENER sección videos en index.html
   → 3 videos: Highlights, Replay último torneo, Entrevista
   → Estilo: .video-grid, .video-card
```

### 📊 TRIGGER (Cuándo ejecutarse)
- Diario via cron
- Cuando se reporta video caído

---

## 🔴 AGENTE LIVE SCORE

### 📋 MISIÓN
Monitorizar partidos en vivo y actualizar scores en tiempo real.

### 📂 ARCHIVOS QUE CONTROLA
- `includes/header.html` (banner live)
- `includes/live_score.html` (scoreboard)
- `scripts/live_monitor_v2.py` - Monitor

### 🔄 FLUJO DE ACTUALIZACIÓN

```
1. EJECUTAR live_monitor_v2.py
   → Fetch de premierpadel.com/tournaments-live/[id]
   → Extraer score actual
   
2. SI score cambió:
   → Actualizar header banner con score
   → Formato: "EQUIPO1 [score] - [score] EQUIPO2"
   
3. SI partido terminó:
   → Desactivar live banner
   → Notificar a AGENTE RESULTADOS
   
4. SI no hay partido:
   → Banner en modo "próximo torneo"
```

### ⚠️ REGLAS CRÍTICAS
- **No mostrar live si no hay partido**
- **Score exacto** - usuario ve TV real
- **Formato TV**: EQUIPO | S1 | S2 | S3

### 📊 TRIGGER (Cuándo ejecutarse)
- Cada 2 minutos cuando hay torneo activo
- Pausar cuando torneo termina

---

## 📁 BASE DE DATOS COMPARTIDA

```
data/
├── tournament_state.json    # Estado actual (qué torneo, fecha, resultado)
├── rankings_data.json       # Rankings FIP (male + female)
├── articles_data.json       # Índice de artículos publicados
├── video_urls.json          # URLs de videos activos
├── tournament_results.json  # Resultados históricos
└── last_fetch.txt          # Timestamp último update
```

### PROTOCOLO DE ACCESO
1. **LEER** siempre del JSON, nunca hardcodear
2. **ESCRIBIR** solo si tienes lock (evitar conflicts)
3. **COMMIT** después de cada escritura exitosa

---

## 🚀 EJECUCIÓN EN CASCADA

```
[CRON TRIGGER] → 14:00 every Sunday
        │
        ▼
┌───────────────────┐
│ rankings_fetch.py │ → Descarga de FIP
└───────────────────┘
        │
        ▼ (datos en rankings_data.json)
┌───────────────────┐
│ update_rankings.py│ → Genera rankings.html
└───────────────────┘
        │
        ▼ (todo OK)
┌───────────────────┐
│   Git Commit      │
└───────────────────┘
        │
        ▼
┌───────────────────┐
│   Git Push        │
└───────────────────┘
```

---

## 🔧 COMANDOS DE MANTENIMIENTO

```bash
# Ver estado de todos los agentes
ls -la padel_news/scripts/

# Ejecutar agente manualmente
python3 scripts/rankings_fetch.py --dry-run
python3 scripts/update_rankings.py --force

# Ver logs
cat scripts/rankings_update.log
cat scripts/rankings_fetch.log

# Restart launchd
launchctl unload ~/Sites/padel_news/scripts/com.ai.padelnews.rankings.plist
launchctl load ~/Sites/padel_news/scripts/com.ai.padelnews.rankings.plist
```

---

## ✅ CHECKLIST DE VERIFICACIÓN

Antes de cada commit, verificar:
- [ ] ¿Los datos vienen de JSON (no hardcoded)?
- [ ] ¿Los estilos usan clases de CSS (no inline)?
- [ ] ¿El header es consistente con otras páginas?
- [ ] ¿No hay duplicados o inconsistencias?
- [ ] ¿El log muestra éxito?