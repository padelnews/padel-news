#!/usr/bin/env python3
"""
ChatClaw - Web Chat para OpenClaw (v2 - Gateway directo)
=========================================================
Interfaz web que conecta con OpenClaw Gateway vía HTTP.
Puerto: 3000
Acceso: http://192.168.1.140:3000
"""

from flask import Flask, request, jsonify, render_template_string, send_from_directory
from flask_cors import CORS
import requests
import json
import os

app = Flask(__name__)
CORS(app)

# Gateway de OpenClaw con autenticación
GATEWAY_URL = "http://127.0.0.1:18789"
GATEWAY_TOKEN = "e6669c7fe98b6a5e458a567436ad8190bb41ad58b6cb5e03"

def generate_html():
    return '''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ChatClaw 🦞</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            min-height: 100vh;
            color: white;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        
        .chat-container {
            width: 100%;
            max-width: 600px;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            overflow: hidden;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }
        
        .header {
            background: linear-gradient(135deg, #e94560, #c73e54);
            padding: 20px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 1.8rem;
            font-weight: 700;
        }
        
        .header p {
            opacity: 0.9;
            margin-top: 5px;
            font-size: 0.9rem;
        }
        
        .status-bar {
            background: rgba(0, 0, 0, 0.3);
            padding: 8px 15px;
            text-align: center;
            font-size: 0.85rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        #messages {
            height: 400px;
            overflow-y: auto;
            padding: 20px;
            background: rgba(0, 0, 0, 0.2);
        }
        
        .message {
            margin-bottom: 15px;
            animation: slideIn 0.3s ease;
        }
        
        @keyframes slideIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .message.user {
            text-align: right;
        }
        
        .message.ai {
            text-align: left;
        }
        
        .message .bubble {
            display: inline-block;
            padding: 12px 18px;
            border-radius: 18px;
            max-width: 80%;
            word-wrap: break-word;
            line-height: 1.4;
        }
        
        .message.user .bubble {
            background: linear-gradient(135deg, #e94560, #c73e54);
            border-bottom-right-radius: 4px;
        }
        
        .message.ai .bubble {
            background: rgba(255, 255, 255, 0.15);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-bottom-left-radius: 4px;
        }
        
        .message .time {
            font-size: 0.75rem;
            opacity: 0.6;
            margin-top: 5px;
        }
        
        .input-area {
            display: flex;
            padding: 15px;
            background: rgba(0, 0, 0, 0.3);
            gap: 10px;
        }
        
        #input {
            flex: 1;
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 25px;
            padding: 12px 20px;
            color: white;
            font-size: 1rem;
            outline: none;
            transition: all 0.3s;
        }
        
        #input:focus {
            background: rgba(255, 255, 255, 0.15);
            border-color: #e94560;
        }
        
        #input::placeholder {
            opacity: 0.5;
        }
        
        #send {
            width: 50px;
            height: 50px;
            border-radius: 50%;
            border: none;
            background: linear-gradient(135deg, #e94560, #c73e54);
            color: white;
            font-size: 1.2rem;
            cursor: pointer;
            transition: all 0.3s;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        #send:hover {
            transform: scale(1.1);
            box-shadow: 0 4px 15px rgba(233, 69, 96, 0.4);
        }
        
        #send:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
        }
        
        .typing {
            text-align: center;
            padding: 10px;
            font-style: italic;
            opacity: 0.7;
            font-size: 0.9rem;
            display: none;
        }
        
        .typing.show {
            display: block;
        }
        
        /* Scrollbar */
        #messages::-webkit-scrollbar {
            width: 8px;
        }
        
        #messages::-webkit-scrollbar-track {
            background: rgba(0, 0, 0, 0.2);
        }
        
        #messages::-webkit-scrollbar-thumb {
            background: rgba(255, 255, 255, 0.2);
            border-radius: 4px;
        }
        
        #messages::-webkit-scrollbar-thumb:hover {
            background: rgba(255, 255, 255, 0.3);
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="header">
            <h1>🦞 ChatClaw</h1>
            <p>Tu asistente IA de OpenClaw</p>
        </div>
        
        <div class="status-bar" id="status-bar">
            <span>🟢 Conectado</span>
            <span id="last-error" style="display:none; color: #ff6b6b;"></span>
        </div>
        
        <div id="messages"></div>
        
        <div class="typing" id="typing">Escribiendo...</div>
        
        <div class="input-area">
            <input type="text" id="input" placeholder="Escribe tu mensaje..." autocomplete="off">
            <button id="send">➤</button>
        </div>
    </div>

    <script>
        const messages = document.getElementById('messages');
        const input = document.getElementById('input');
        const sendBtn = document.getElementById('send');
        const typing = document.getElementById('typing');
        const statusBar = document.getElementById('last-error');
        
        let chatHistory = JSON.parse(localStorage.getItem('chatclaw_history') || '[]');
        
        function getTime() {
            return new Date().toLocaleTimeString('es-ES', {hour: '2-digit', minute: '2-digit'});
        }
        
        function addMessage(role, text) {
            const div = document.createElement('div');
            div.className = 'message ' + role;
            div.innerHTML = `
                <div class="bubble">${text}</div>
                <div class="time">${getTime()}</div>
            `;
            messages.appendChild(div);
            messages.scrollTop = messages.scrollHeight;
            
            chatHistory.push({role, text, time: getTime()});
            localStorage.setItem('chatclaw_history', JSON.stringify(chatHistory.slice(-50)));
        }
        
        async function sendMessage() {
            const text = input.value.trim();
            if (!text) return;
            
            input.value = '';
            addMessage('user', text);
            typing.classList.add('show');
            sendBtn.disabled = true;
            
            try {
                const resp = await fetch('/ask', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({question: text})
                });
                
                const data = await resp.json();
                typing.classList.remove('show');
                sendBtn.disabled = false;
                
                if (data.response) {
                    addMessage('ai', data.response);
                } else if (data.error) {
                    addMessage('ai', '❌ Error: ' + data.error);
                }
            } catch (e) {
                typing.classList.remove('show');
                sendBtn.disabled = false;
                const errorMsg = '❌ Error de conexión: ' + e.message;
                addMessage('ai', errorMsg);
                
                // Mostrar error en la barra de estado
                statusBar.textContent = errorMsg;
                statusBar.style.display = 'inline';
                setTimeout(() => { statusBar.style.display = 'none'; }, 5000);
            }
        }
        
        sendBtn.addEventListener('click', sendMessage);
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendMessage();
        });
        
        // Cargar historial
        chatHistory.forEach(msg => {
            const div = document.createElement('div');
            div.className = 'message ' + msg.role;
            div.innerHTML = `
                <div class="bubble">${msg.text}</div>
                <div class="time">${msg.time}</div>
            `;
            messages.appendChild(div);
        });
        
        input.focus();
    </script>
</body>
</html>'''


@app.route('/')
def index():
    return render_template_string(generate_html())


@app.route('/voice_chat.html')
def voice_chat():
    """Servir el archivo de chat de voz"""
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'voice_chat.html')


@app.route('/jarvis_interface.html')
def jarvis_interface():
    """Servir la interfaz JARVIS completa"""
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'jarvis_interface.html')


@app.route('/jarvis_completo.html')
def jarvis_completo():
    """Servir wake_agent.html original adaptado"""
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'jarvis_completo.html')


@app.route('/jarvis_threejs.html')
def jarvis_threejs():
    """Servir interfaz JARVIS con Three.js (partículas 3D)"""
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'jarvis_threejs.html')


@app.route('/jarvis_original.html')
def jarvis_original():
    """Servir interfaz JARVIS original de GitHub (2000 partículas + líneas)"""
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'jarvis_original.html')


@app.route('/jarvis_pro.html')
def jarvis_pro():
    """Servir interfaz JARVIS PRO (3000 partículas, rings, core glow)"""
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'jarvis_pro.html')


@app.route('/jarvis_cyber.html')
def jarvis_cyber():
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'jarvis_cyber.html')


@app.route('/jarvis_dashboard_v2.html')
def jarvis_dashboard_v2():
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'jarvis_dashboard_v2.html')


@app.route('/jarvis_dashboard.html')
def jarvis_dashboard():
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'jarvis_dashboard.html')


@app.route('/componentes_pc.jpg')
def componentes():
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'componentes_pc.jpg')


@app.route('/pc_gaming_poster.html')
def pc_gaming_poster():
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'pc_gaming_poster.html')


@app.route('/tiktok_bot_control.html')
def tiktok_bot_control():
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'tiktok_bot_control.html')


@app.route('/tiktok_subastas.html')
def tiktok_subastas():
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'tiktok_subastas.html')


@app.route('/futbet_pro.html')
def futbet_pro():
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'futbet_pro.html')


@app.route('/futbet.html')
def futbet():
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'futbet.html')


@app.route('/test_mic.html')
def test_mic_route():
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'test_mic.html')


@app.route('/status')
def status():
    """Endpoint para ver el estado del servidor"""
    return jsonify({
        'status': 'running',
        'gateway_url': GATEWAY_URL,
        'gateway_connected': True
    })


@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    question = data.get('question', '')
    
    if not question:
        return jsonify({'error': 'No hay pregunta'})
    
    try:
        print(f"\n📩 Pregunta: {question[:50]}...")
        
        # Conectar con el Gateway de OpenClaw
        headers = {
            "Authorization": f"Bearer {GATEWAY_TOKEN}",
            "Content-Type": "application/json"
        }
        
        resp = requests.post(
            f"{GATEWAY_URL}/v1/chat/completions",
            headers=headers,
            json={
                "model": "openclaw",
                "messages": [
                    {"role": "user", "content": question}
                ],
                "max_tokens": 1024,
                "stream": False
            },
            timeout=120  # 2 minutos de timeout
        )
        
        if resp.status_code == 200:
            result = resp.json()
            response = result['choices'][0]['message']['content']
            print(f"✅ Respuesta: {response[:100]}...")
            return jsonify({'response': response})
        else:
            print(f"❌ Error gateway: {resp.status_code}")
            print(f"   Response body: {resp.text}")
            print(f"   Request headers: {headers}")
            print(f"   Request body: model=ollama/qwen3.5:cloud, messages=[{question}]")
            return jsonify({'error': f'Error del servidor ({resp.status_code}): {resp.text[:200]}'})
    
    except requests.Timeout:
        print("⚠️ Timeout")
        return jsonify({'error': 'Tiempo de espera agotado. Intenta de nuevo.'})
    except requests.ConnectionError as e:
        print(f"❌ Connection error: {e}")
        return jsonify({'error': 'No se pudo conectar con OpenClaw. Verifica que el gateway esté corriendo.'})
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({'error': str(e)})



@app.route('/stats')
def get_stats():
    """Retorna estadísticas reales del sistema"""
    import psutil
    try:
        cpu = psutil.cpu_percent(interval=0.5)
        ram = psutil.virtual_memory().percent
        
        # Intentar obtener temperatura (solo macOS/Linux)
        temp = None
        try:
            temps = psutil.sensors_temperatures()
            if temps:
                for name, entries in temps.items():
                    for entry in entries:
                        if 'cpu' in entry.label.lower() or 'core' in entry.label.lower():
                            temp = entry.current
                            break
        except:
            pass
        
        return {'cpu': cpu, 'ram': ram, 'temp': temp}
    except Exception as e:
        return {'cpu': 0, 'ram': 0, 'error': str(e)}


@app.route('/tienda_cajas.html')
def tienda_cajas():
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'tienda_cajas.html')

@app.route('/panel_operador_v2.html')
def panel_operador_v2():
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'panel_operador_v2.html')


@app.route('/panel_operador.html')
def panel_operador():
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'panel_operador.html')

@app.route('/api/comprar_caja', methods=['POST'])
def comprar_caja():
    data = request.json
    print(f"📦 COMPRA: {data['tiktokUser']} compra {data['box']} por €{data['price']}")
    # Aquí iría la integración con Stripe/PayPal
    # Y guardar en base de datos con caja pagada = True
    return jsonify({'status': 'success', 'userId': data['tiktokUser']})

@app.route('/api/guardar_ganador', methods=['POST'])
def guardar_ganador():
    data = request.json
    print(f"🏆 GANADOR: {data['user']} gana {data['product']} por €{data['price']}")
    # Guardar en base de datos
    return jsonify({'status': 'saved'})

if __name__ == '__main__':
    import ssl
    print('🦞 ChatClaw HTTPS: https://192.168.1.140:3000\n')
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain('cert.pem', 'key.pem')
    app.run(host='0.0.0.0', port=8888, debug=False, ssl_context=context)
