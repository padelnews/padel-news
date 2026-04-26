#!/bin/bash
# ACTIVAR AGENTES AUTOMÁTICOS - Padel News Pro
# Ejecuta este script UNA VEZ para activar todos los agentes

echo "🎾 Activando agentes automáticos de Padel News Pro..."
echo ""

SCRIPTS_DIR="/Users/cristian/Sites/padel_news/scripts"

# Activar Index Agent
echo "📌 Activando Index Agent (08:00 y 20:00)..."
launchctl load "$SCRIPTS_DIR/com.ai.padelnews.index.plist" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "   ✅ Index Agent activo"
else
    echo "   ⚠️ Index Agent ya estaba activo o error"
fi

# Activar Live Score Agent
echo "📌 Activando Live Score Agent (cada 2 horas)..."
launchctl load "$SCRIPTS_DIR/com.ai.padelnews.livescore.plist" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "   ✅ Live Score Agent activo"
else
    echo "   ⚠️ Live Score Agent ya estaba activo o error"
fi

# Activar Rankings Agent
echo "📌 Activando Rankings Agent (domingo 20:00)..."
launchctl load "$SCRIPTS_DIR/com.ai.padelnews.rankings.plist" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "   ✅ Rankings Agent activo"
else
    echo "   ⚠️ Rankings Agent ya estaba activo o error"
fi

echo ""
echo "✅ Agentes activados. Se ejecutarán automáticamente."
echo ""
echo "Para verificar que están activos:"
echo "  launchctl list | grep padelnews"
echo ""
echo "Para ver los logs:"
echo "  tail -f $SCRIPTS_DIR/index_agent.log"
echo "  tail -f $SCRIPTS_DIR/live_score_agent.log"
