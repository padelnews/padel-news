#!/usr/bin/env python3
"""Proxy simple para evitar CORS - reenvía peticiones a Ollama remote"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.request
import json

OLLAMA_URL = "http://192.168.1.240:11434"

class ProxyHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_POST(self):
        # Leer contenido
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        
        # Reenviar a Ollama
        try:
            req = urllib.request.Request(
                OLLAMA_URL + "/api/generate",
                data=body,
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=30) as response:
                result = response.read()
                
            # Devolver con CORS
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(result)
        except Exception as e:
            self.send_response(500)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
    
    def do_GET(self):
        # Ping simple
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(b'Proxy OK')

if __name__ == "__main__":
    server = HTTPServer(('0.0.0.0', 8889), ProxyHandler)
    print("Proxy activo en http://0.0.0.0:8889")
    server.serve_forever()
