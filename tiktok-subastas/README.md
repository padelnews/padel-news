# 🎵 TikTok Subastas - Sistema de Subastas en Vivo

Sistema profesional para realizar subastas de cajas misteriosas en TikTok Live.

## 🚀 Características

- **Tienda Online**: Compra de cajas con pasarela de pago
- **Panel de Operador**: Control simplificado para subastas en vivo
- **Detección Automática**: Bot lee chat y asigna ganadores automáticamente
- **Verificación de Cajas**: Solo usuarios con caja pagada pueden ganar

## 📁 Archivos Principales

### Para el Cliente (Tienda)
- `tienda_cajas.html` - Web de compra de cajas

### Para el Operador (Live)
- `panel_operador_v2.html` - Panel simplificado de subastas
- `tiktok_subastas.html` - Web para mostrar en el live

### Backend
- `chatclaw.py` - Servidor Flask con SSL
- `tiktok_bot.py` - Bot de lectura de chat con Selenium

## 🛠️ Instalación

```bash
# Instalar dependencias
pip install selenium webdriver-manager flask flask-socketio

# Iniciar servidor
python chatclaw.py
```

## 🌐 URLs

- **Tienda**: https://192.168.1.140:8888/tienda_cajas.html
- **Panel Operador**: https://192.168.1.140:8888/panel_operador_v2.html
- **Web Live**: https://192.168.1.140:8888/tiktok_subastas.html

## 📖 Cómo Usar

### 1. El Cliente Compra una Caja
- Entra a la tienda online
- Elige caja (Básica, Premium, VIP)
- Rellena datos de envío
- Realiza el pago
- ✅ Caja activada automáticamente

### 2. El Operador Inicia la Subasta
- Abre el panel de operador
- Introduce el precio (ej: 6 = 6€)
- Click en "INICIAR SUBASTA"
- Cuenta atrás de 10 segundos

### 3. Detección Automática del Ganador
- El bot lee el chat de TikTok Live
- Busca mensajes: "mío [número]"
- Verifica si la caja está pagada
- ✅ Asigna el producto automáticamente

## 🔧 Configuración

### Cajas Pagadas
Editar en `panel_operador_v2.html`:
```javascript
const paidBoxes = new Set(['1', '2', '3', '150', '200']);
```

### Integración con TikTok
El bot usa Selenium para leer el chat en tiempo real. Necesitas:
- Chrome instalado
- WebDriver configurado
- Sesión de TikTok iniciada

## 💳 Pasarelas de Pago

Actualmente en modo simulación. Para producción integrar:
- Stripe (tarjetas)
- PayPal
- Bizum (vía Redsys)

## 📦 Estructura del Proyecto

```
chatclaw/
├── chatclaw.py              # Servidor Flask principal
├── tiktok_bot.py            # Bot de lectura de chat
├── tienda_cajas.html        # Tienda online
├── panel_operador_v2.html   # Panel de operador
├── tiktok_subastas.html     # Web para live
├── tiktok_bot_control.html  # Panel de control del bot
├── cert.pem                 # Certificado SSL
├── key.pem                  # Key SSL
└── README.md                # Este archivo
```

## 🎯 Flujo Completo

1. **Compra** → Cliente compra caja en tienda
2. **Activación** → Caja marcada como "pagada" en base de datos
3. **Subasta** → Operador inicia puja con precio
4. **Detección** → Bot busca "mío [número]" en chat
5. **Verificación** → Comprueba caja pagada
6. **Asignación** → Gana y se guarda en base de datos

## ⚠️ Notas Importantes

- Requiere HTTPS para micrófono en móviles
- Certificados SSL auto-firmados incluidos
- Puerto por defecto: 8888
- Bot requiere Chrome con sesión de TikTok iniciada

## 📞 Soporte

Para issues o preguntas, contactar con el desarrollador.

---

**Hecho con ❤️ para TikTok Live Subastas**
