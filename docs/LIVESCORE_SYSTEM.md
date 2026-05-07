# 🎾 Sistema de Resultados en Vivo - Premier Padel

## Descripción

Sistema automático que muestra los resultados y emparejamientos del torneo en curso, actualizándose cada **10 minutos**.

## Componentes

### 1. **Datos de Partidos** (`data/asuncion_p1_draw.json`)
- Contiene todos los partidos del torneo organizados por rondas
- Cada partido incluye: jugadores, país, seed, marcador, estado
- Estados: `scheduled`, `live`, `finished`

### 2. **Live Score Updater** (`scripts/livescore_updater.py`)
- **Ejecución:** Cada 10 minutos (600 segundos) vía launchd
- **Función:** Actualiza marcadores y genera nuevas páginas
- **Push automático:** Commit y push a GitHub

### 3. **Website Generator** (`scripts/website_generator.py`)
- Lee los datos de partidos y genera `resultados.html`
- Muestra:
  - 🔴 EN JUEGO para partidos en directo
  - Seeds [1], [2], etc.
  - Banderas de países
  - Marcadores en tiempo real
  - Horarios de partidos programados

## Estructura de Datos

```json
{
  "rounds": {
    "round_of_16": [
      {
        "team1": {"players": ["Juan Lebrón", "Leo Augsburger"], "country": "ESP/ARG", "seed": 1},
        "team2": {"players": ["Pareja A", "Pareja B"], "country": "ARG", "seed": 16},
        "score": "6-4, 3-2",
        "status": "live",
        "winner": null
      }
    ]
  }
}
```

## Comandos Útiles

### Ver logs en tiempo real
```bash
tail -f /Users/cristian/Sites/padel_news/scripts/livescore_updater.log
```

### Ejecutar manualmente
```bash
cd /Users/cristian/Sites/padel_news
python3 scripts/livescore_updater.py
```

### Ver estado del agente
```bash
launchctl list | grep livescore
```

### Recargar configuración
```bash
launchctl unload /Users/cristian/Sites/padel_news/scripts/com.ai.padelnews.livescore.plist
launchctl load /Users/cristian/Sites/padel_news/scripts/com.ai.padelnews.livescore.plist
```

## Flujo de Actualización

1. **Cada 10 minutos** el agente se ejecuta
2. **Verifica** si el torneo está "live"
3. **Actualiza** los marcadores (simulado o desde API real)
4. **Regenera** resultados.html con website_generator.py
5. **Detecta cambios** en los archivos
6. **Commit** automático con timestamp
7. **Push** a GitHub

## Estado Actual

- ✅ Agente configurado y corriendo
- ✅ Actualización cada 10 minutos
- ✅ Muestra Round of 16 completo
- ✅ Partido en directo marcado con 🔴
- ✅ Push automático a GitHub

## Futuras Mejoras

### Corto Plazo
- [ ] Conectar con API real de Premier Padel
- [ ] Scraping automático de premierpadel.com
- [ ] Web scraping de padel.live como fallback

### Medio Plazo
- [ ] Notificaciones Telegram cuando haya partido importante
- [ ] Actualizar automáticamente torneos.html con el cuadro completo
- [ ] Añadir estadísticas de partidos (aces, winners, etc.)

### Largo Plazo
- [ ] Integración con APIs de casas de apuestas para cuotas
- [ ] Predicciones IA para ganadores de partidos
- [ ] Historial de enfrentamientos entre parejas

## Troubleshooting

### El agente no se ejecuta
```bash
# Verificar launchd
launchctl list | grep livescore

# Ver logs
cat scripts/livescore_updater.log

# Recargar
launchctl unload/load scripts/com.ai.padelnews.livescore.plist
```

### Los resultados no se actualizan
1. Verificar que el torneo tenga status "live"
2. Checkear logs del agente
3. Verificar conexión a internet
4. Probar ejecución manual

### Git push falla
El agente intenta automáticamente:
1. Pull con estrategia "ours"
2. Reintentar push
3. Si falla, loguea el error y continúa

## URLs Relacionadas

- **GitHub:** https://github.com/padelnews/padel-news
- **Premier Padel:** https://www.premierpadel.com/
- **Web Local:** http://192.168.1.140:8888/resultados.html
