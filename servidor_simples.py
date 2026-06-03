"""
Servidor Proxy Simples - SEM Login
===================================
Apenas proxy direto sem complicações
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import socket
import json
import os
import urllib.parse
import requests

# Configurações
PORTA = 8080

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

IP_LOCAL = get_local_ip()

class ProxySimples(BaseHTTPRequestHandler):
    
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, HEAD, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        super().end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()
    
    def do_HEAD(self):
        self.do_GET(head_only=True)
    
    def do_GET(self, head_only=False):
        path = urllib.parse.unquote(self.path)
        
        # Status
        if path == '/':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            if not head_only:
                status = {"status": "online", "service": "Simple Proxy", "ip": IP_LOCAL}
                self.wfile.write(json.dumps(status).encode())
            return
        
        # GAMES.json
        if path == '/GAMES.json':
            self.serve_games_json()
            return
        
        # Proxy PKG
        if path.startswith('/pkg/'):
            self.proxy_pkg_simples(path[5:], head_only)
            return
        
        self.send_error(404)
    
    def serve_games_json(self):
        """Serve GAMES.json local com URLs reescritas"""
        try:
            with open('GAMES_format.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Reescrever URLs
            new_data = {"DATA": {}}
            for url, info in data.get("DATA", {}).items():
                clean_url = url.replace('https://', '').replace('http://', '')
                new_url = f"http://{IP_LOCAL}:{PORTA}/pkg/{clean_url}"
                new_data["DATA"][new_url] = info
            
            json_bytes = json.dumps(new_data).encode('utf-8')
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', len(json_bytes))
            self.end_headers()
            self.wfile.write(json_bytes)
            print(f"✅ GAMES.json servido ({len(new_data['DATA'])} jogos)")
            
        except Exception as e:
            print(f"❌ Erro: {e}")
            self.send_error(500, str(e))
    
    def proxy_pkg_simples(self, pkg_path, head_only=False):
        """Proxy simples usando requests"""
        
        # Construir URL original
        original_url = f"https://{pkg_path}"
        print(f"📦 {'HEAD' if head_only else 'GET'}: {original_url[:80]}...")
        
        try:
            # Headers simples
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            # Adicionar Range se necessário
            if 'Range' in self.headers:
                headers['Range'] = self.headers['Range']
            
            # Fazer requisição
            if head_only:
                response = requests.head(original_url, headers=headers, stream=True, timeout=30)
            else:
                response = requests.get(original_url, headers=headers, stream=True, timeout=30)
            
            # Verificar se deu certo
            response.raise_for_status()
            
            # Enviar resposta
            self.send_response(response.status_code)
            
            # Headers importantes
            if 'Content-Length' in response.headers:
                self.send_header('Content-Length', response.headers['Content-Length'])
            if 'Content-Type' in response.headers:
                self.send_header('Content-Type', response.headers['Content-Type'])
            if 'Content-Range' in response.headers:
                self.send_header('Content-Range', response.headers['Content-Range'])
            
            self.send_header('Accept-Ranges', 'bytes')
            self.end_headers()
            
            if not head_only:
                # Stream do conteúdo
                bytes_sent = 0
                for chunk in response.iter_content(chunk_size=1024*1024):
                    if chunk:
                        self.wfile.write(chunk)
                        bytes_sent += len(chunk)
                        if bytes_sent % (10 * 1024 * 1024) == 0:
                            print(f"   📥 {bytes_sent / (1024*1024):.1f} MB enviados...")
                
                print(f"✅ Download completo: {bytes_sent / (1024*1024):.1f} MB")
            else:
                print(f"✅ HEAD OK - Size: {response.headers.get('Content-Length', 'unknown')}")
                
        except requests.exceptions.HTTPError as e:
            print(f"❌ HTTP Error: {e}")
            self.send_error(e.response.status_code, str(e))
        except Exception as e:
            print(f"❌ Erro: {e}")
            self.send_error(500, str(e))
    
    def log_message(self, format, *args):
        pass

def main():
    print("=" * 60)
    print("🎮 SERVIDOR PROXY SIMPLES")
    print("=" * 60)
    print(f"📡 IP: {IP_LOCAL}:{PORTA}")
    print(f"📋 Games: http://{IP_LOCAL}:{PORTA}/GAMES.json")
    print("=" * 60)
    print("⏹️  Pressione Ctrl+C para parar")
    print()
    
    server = HTTPServer(('', PORTA), ProxySimples)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Servidor parado!")
        server.shutdown()

if __name__ == '__main__':
    main()
