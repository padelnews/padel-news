#!/usr/bin/env python3
"""
🤖 TikTok Live Chat Reader para Subastas
Lee el chat de TikTok Live en tiempo real usando Selenium
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import json
import re
from datetime import datetime
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import threading

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tiktok_subastas_secret'
socketio = SocketIO(app, cors_allowed_origins="*")

# Usuarios con caja pagada
USERS_WITH_BOX = {
    '@carlos92': True,
    '@maria_garcia': True,
    '@juan_perez': True,
    '@lucia_88': True,
    '@pedro_shop': True,
}

# Estado actual
current_state = {
    'product_name': 'Caja Misteriosa Premium',
    'current_price': 0,
    'time_left': 30,
    'is_running': False,
    'winners': [],
    'chat_messages': [],
    'current_winner': None
}

class TikTokChatReader:
    def __init__(self):
        self.driver = None
        self.is_running = False
        
    def setup_driver(self):
        """Configurar Chrome con Selenium"""
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Usar perfil existente (para mantener sesión de TikTok)
        chrome_options.add_argument('--user-data-dir=/tmp/tiktok_profile')
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
    def open_tiktok_live(self, live_url):
        """Abrir el Live de TikTok"""
        if not self.driver:
            self.setup_driver()
        
        self.driver.get(live_url)
        print(f"🔴 Abriendo TikTok Live: {live_url}")
        
    def read_chat(self):
        """Leer mensajes del chat"""
        try:
            # Esperar a que cargue el chat
            chat_container = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[class*="chat-container"], [class*="message-container"]'))
            )
            
            # Obtener últimos mensajes
            messages = self.driver.find_elements(By.CSS_SELECTOR, '[class*="message"], [class*="chat-item"]')
            
            for msg in messages[-10:]:  # Últimos 10 mensajes
                try:
                    username_elem = msg.find_element(By.CSS_SELECTOR, '[class*="username"], [class*="user-name"]')
                    text_elem = msg.find_element(By.CSS_SELECTOR, '[class*="text"], [class*="message-text"]')
                    
                    username = username_elem.text.strip()
                    text = text_elem.text.strip()
                    
                    if username and text:
                        self.process_message(username, text)
                except:
                    continue
                    
        except Exception as e:
            print(f"❌ Error leyendo chat: {e}")
    
    def process_message(self, username, text):
        """Procesar mensaje y detectar pujas/claims"""
        username = username.lower() if username.startswith('@') else f'@{username.lower()}'
        text = text.strip()
        
        message_data = {
            'user': username,
            'text': text,
            'time': datetime.now().strftime('%H:%M:%S'),
            'type': 'normal',
            'has_box': USERS_WITH_BOX.get(username, False)
        }
        
        # Detectar tipo de mensaje
        if any(word in text.lower() for word in ['mío', 'mio', 'yo', 'lo cojo', 'es mío']):
            message_data['type'] = 'claim'
            print(f"🎯 CLAIM detectado: {username} dice '{text}'")
            
        elif re.search(r'\d+\s*€?', text):
            message_data['type'] = 'bid'
            # Extraer cantidad
            match = re.search(r'(\d+)\s*€?', text)
            if match:
                amount = int(match.group(1))
                if amount > current_state['current_price']:
                    current_state['current_price'] = amount
                    socketio.emit('price_update', {'price': amount})
                    print(f"💰 NUEVA PUJA: {username} - {amount}€")
        
        # Enviar a la web
        socketio.emit('new_message', message_data)
        current_state['chat_messages'].append(message_data)
        
        # Mantener solo últimos 100 mensajes
        if len(current_state['chat_messages']) > 100:
            current_state['chat_messages'] = current_state['chat_messages'][-100:]
    
    def start_monitoring(self, live_url):
        """Iniciar monitoreo del Live"""
        self.open_tiktok_live(live_url)
        self.is_running = True
        
        print("✅ Bot iniciado - Leyendo chat de TikTok Live...")
        
        while self.is_running:
            self.read_chat()
            time.sleep(1)  # Leer cada segundo
    
    def stop(self):
        """Detener bot"""
        self.is_running = False
        if self.driver:
            self.driver.quit()

# Instancia global del bot
tiktok_bot = TikTokChatReader()

# Rutas Flask
@app.route('/tiktok_bot_control')
def bot_control():
    """Panel de control del bot"""
    return render_template('tiktok_bot_control.html')

@app.route('/api/start_bot', methods=['POST'])
def start_bot():
    """Iniciar bot con URL del Live"""
    data = request.json
    live_url = data.get('url', '')
    
    if not live_url:
        return jsonify({'error': 'URL requerida'}), 400
    
    # Iniciar en thread separado
    thread = threading.Thread(target=tiktok_bot.start_monitoring, args=(live_url,))
    thread.daemon = True
    thread.start()
    
    return jsonify({'status': 'started', 'url': live_url})

@app.route('/api/stop_bot', methods=['POST'])
def stop_bot():
    """Detener bot"""
    tiktok_bot.stop()
    return jsonify({'status': 'stopped'})

@app.route('/api/state')
def get_state():
    """Obtener estado actual"""
    return jsonify(current_state)

@app.route('/api/add_winner', methods=['POST'])
def add_winner():
    """Guardar ganador"""
    data = request.json
    winner = {
        'user': data.get('user'),
        'product': data.get('product', current_state['product_name']),
        'price': data.get('price', current_state['current_price']),
        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    current_state['winners'].append(winner)
    socketio.emit('new_winner', winner)
    
    return jsonify({'status': 'saved', 'winner': winner})

@app.route('/api/export', methods=['GET'])
def export_data():
    """Exportar datos"""
    return jsonify(current_state)

# WebSocket events
@socketio.on('connect')
def handle_connect():
    print("✅ Cliente conectado")
    emit('state_update', current_state)

@socketio.on('disconnect')
def handle_disconnect():
    print("❌ Cliente desconectado")

if __name__ == '__main__':
    print("🚀 TikTok Subastas Bot Server")
    print("📡 Puerto: 5001")
    print("🌐 Web: http://localhost:5001/tiktok_bot_control")
    socketio.run(app, host='0.0.0.0', port=5001, debug=True)
