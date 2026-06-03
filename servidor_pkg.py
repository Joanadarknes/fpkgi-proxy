"""
Servidor HTTP para enviar PKGs para o PS4
==========================================
1. Coloque seus arquivos .pkg na pasta 'pkgs' 
2. Execute este script
3. No PS4, use o Remote Package Installer com o IP mostrado
"""

import http.server
import socketserver
import os
import socket

# Configurações
PORTA = 8080
PASTA_PKG = "pkgs"

# Criar pasta se não existir
if not os.path.exists(PASTA_PKG):
    os.makedirs(PASTA_PKG)
    print(f"📁 Pasta '{PASTA_PKG}' criada!")
    print(f"   Coloque seus arquivos .pkg nesta pasta.")
    print()

# Descobrir IP local
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

# Mudar para pasta de PKGs
os.chdir(PASTA_PKG)

# Criar servidor
class MyHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

print("=" * 50)
print("🎮 SERVIDOR PKG PARA PS4")
print("=" * 50)
print()
print(f"📡 Seu IP: {IP_LOCAL}")
print(f"🌐 URL: http://{IP_LOCAL}:{PORTA}/")
print()
print("📋 No PS4, use:")
print("   - Remote Package Installer")
print("   - Ou PKG Sender")
print()
print(f"   Digite este endereço: http://{IP_LOCAL}:{PORTA}/")
print()
print("📁 Coloque os .pkg na pasta: pkgs")
print()
print("⏹️  Pressione Ctrl+C para parar o servidor")
print("=" * 50)

with socketserver.TCPServer(("", PORTA), MyHandler) as httpd:
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Servidor parado!")
