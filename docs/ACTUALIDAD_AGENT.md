# 📰 Actualidad Agent - Actualización Automática de Noticias

## Descripción

Agente automático que busca noticias de pádel y actualiza la sección de Actualidad de la web cada **3 horas**.

## Funcionamiento

### Ejecución Automática
- **Frecuencia:** Cada 3 horas (10800 segundos)
- **Inicio:** Se ejecuta al cargar el sistema (RunAtLoad)
- **Gestión:** launchd (macOS)

### Pasos que ejecuta:

1. **Fetch News** (`fetch_news.py`)
   - Busca noticias de fuentes oficiales (WPT, Premier Padel, RSS)
   - Genera resúmenes originales con IA (Ollama)
   - Guarda en `data/news_data.json`
   - Timeout: 300 segundos (5 minutos)

2. **Generate Pages** (`website_generator.py`)
   - Genera `actualidad.html` con las noticias actualizadas
   - Genera todas las demás páginas (index, resultados, torneos)
   - Valida el HTML generado

3. **Commit & Push** (Git)
   - Detecta cambios en los archivos
   - Hace commit automático con timestamp
   - Push a GitHub (https://github.com/padelnews/padel-news)
   - Si hay conflicto: hace pull + re-push automático

## Archivos

- `scripts/actualidad_agent.py` - Script principal del agente
- `scripts/com.ai.padelnews.actualidad.plist` - Configuración launchd
- `scripts/actualidad_state.json` - Estado del agente (última ejecución, conteo)
- `scripts/actualidad_agent.log` - Logs de ejecución
- `scripts/actualidad_agent.err` - Errores (si los hay)

## Comandos Útiles

### Ver estado del agente
```bash
launchctl list | grep actualidad
```

### Ver logs en tiempo real
```bash
tail -f /Users/cristian/Sites/padel_news/scripts/actualidad_agent.log
```

### Ejecutar manualmente
```bash
cd /Users/cristian/Sites/padel_news
python3 scripts/actualidad_agent.py
```

### Recargar configuración
```bash
launchctl unload /Users/cristian/Sites/padel_news/scripts/com.ai.padelnews.actualidad.plist
launchctl load /Users/cristian/Sites/padel_news/scripts/com.ai.padelnews.actualidad.plist
```

### Detener agente
```bash
launchctl unload /Users/cristian/Sites/padel_news/scripts/com.ai.padelnews.actualidad.plist
```

## Troubleshooting

### El fetch de noticias falla (timeout)
- **Causa:** Ollama remoto (192.168.1.240) no responde o es lento
- **Solución:** El agente continúa con noticias existentes y genera páginas igual
- **Prevención:** Aumentar timeout en `actualidad_agent.py` o verificar conexión a Ollama

### Git push falla
- **Causa:** El "agente externo" hizo commits mientras tanto
- **Solución:** El agente hace automáticamente `git pull --no-rebase -X ours` y reintenta push

### El agente no se ejecuta
- Verificar launchd: `launchctl list | grep actualidad`
- Verificar logs: `cat scripts/actualidad_agent.log`
- Recargar: `launchctl unload/load`

## Estado Actual

- ✅ Agente configurado y corriendo
- ✅ Ejecución cada 3 horas
- ✅ Commit y push automático a GitHub
- ✅ Tolerante a fallos (continúa si fetch_news falla)

## Futuras Mejoras

- [ ] Añadir más fuentes de noticias (padelworldpress, WPT RSS)
- [ ] Filtrar noticias duplicadas
- [ ] Añadir imágenes a las noticias
- [ ] Notificaciones Telegram cuando haya noticias importantes
