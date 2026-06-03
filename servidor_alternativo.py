"""
Servidor FPKGi com Fontes Alternativas
======================================
Quando o Archive.org não funciona, usa outras fontes
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import socket
import json
import os
import urllib.parse
import urllib.request

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

# Fontes alternativas para PKGs (quando Archive.org não funciona)
FONTES_ALTERNATIVAS = [
    "https://myrient.erista.me/files/No-Intro/Sony%20-%20PlayStation%204/",
    "https://vimm.net/vault/PS4/",
    "https://nxbrew.com/ps4/",
]

class FPKGiAlternativoHandler(BaseHTTPRequestHandler):
    
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, HEAD, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        super().end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()
    
    def do_GET(self):
        path = urllib.parse.unquote(self.path)
        
        # Status
        if path == '/':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            status = {
                "status": "online", 
                "service": "FPKGi Alternative Sources", 
                "ip": IP_LOCAL,
                "message": "Archive.org collection is private/removed. Using alternative sources."
            }
            self.wfile.write(json.dumps(status, indent=2).encode())
            return
        
        # GAMES.json modificado
        if path == '/GAMES.json':
            self.serve_alternative_games()
            return
        
        # DLC e Homebrew vazios por enquanto
        if path == '/DLC.json' or path == '/HOMEBREW.json':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"DATA": {}}')
            return
        
        self.send_error(404, "Use fontes alternativas - Archive.org collection is private")
    
    def serve_alternative_games(self):
        """Serve GAMES.json com aviso sobre fontes alternativas"""
        try:
            # Criar JSON informativo
            alternative_data = {
                "DATA": {},
                "MESSAGE": "AVISO: A coleção ps4-fpkg-collection-english-a do Archive.org foi TORNADA PRIVADA ou REMOVIDA",
                "ALTERNATIVES": {
                    "1": "Use PKG Linker: https://pkg-zone.com/",
                    "2": "VIMM's Lair: https://vimm.net/vault/PS4/", 
                    "3": "Myrient: https://myrient.erista.me/",
                    "4": "NXBrew: https://nxbrew.com/ps4/",
                    "5": "Busque por: 'PS4 PKG download sites' no Google"
                },
                "INSTRUCTIONS": {
                    "1": "Baixe os PKGs manualmente dessas fontes",
                    "2": "Use ferramentas como PKG Linker para instalar",
                    "3": "Configure URLs diretas no FPKGi se encontrar outras coleções"
                }
            }
            
            json_bytes = json.dumps(alternative_data, indent=2).encode('utf-8')
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', len(json_bytes))
            self.end_headers()
            self.wfile.write(json_bytes)
            print(f"✅ Informações sobre fontes alternativas enviadas")
            
        except Exception as e:
            print(f"❌ Erro: {e}")
            self.send_error(500, str(e))
    
    def log_message(self, format, *args):
        pass

def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)) or '.')
    
    print("=" * 60)
    print("🎮 SERVIDOR FPKGI - FONTES ALTERNATIVAS")
    print("=" * 60)
    print()
    print("🚨 PROBLEMA IDENTIFICADO:")
    print("   A coleção 'ps4-fpkg-collection-english-a' do Archive.org")
    print("   foi TORNADA PRIVADA ou REMOVIDA pelo proprietário.")
    print()
    print("💡 SOLUÇÕES ALTERNATIVAS:")
    print("   1. PKG Zone: https://pkg-zone.com/")
    print("   2. VIMM's Lair: https://vimm.net/vault/PS4/")
    print("   3. Myrient: https://myrient.erista.me/")
    print("   4. NXBrew: https://nxbrew.com/ps4/")
    print()
    print(f"📡 Servidor local: http://{IP_LOCAL}:{PORTA}")
    print("   (Servirá informações sobre fontes alternativas)")
    print()
    print("=" * 60)
    print("⏹️  Pressione Ctrl+C para parar")
    print("=" * 60)
    print()
    
    server = HTTPServer(('', PORTA), FPKGiAlternativoHandler)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Servidor parado!")
        server.shutdown()

if __name__ == '__main__':
    main()
