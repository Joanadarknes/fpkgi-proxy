"""
Servidor Local para FPKGi
==========================
Serve os JSONs de jogos diretamente para o PS4
"""

from http.server import HTTPServer, SimpleHTTPRequestHandler
import socket
import json
import os
import urllib.parse
import urllib.request

# Configurações
PORTA = 8080

def get_local_ip():
    """Descobre o IP local da máquina"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

IP_LOCAL = get_local_ip()

class FPKGiHandler(SimpleHTTPRequestHandler):
    """Handler personalizado para o FPKGi"""
    
    def end_headers(self):
        # CORS para permitir acesso do PS4
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        # Headers específicos para o PS4
        self.send_header('Connection', 'keep-alive')
        self.send_header('Keep-Alive', 'timeout=30, max=100')
        super().end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()
    
    def do_GET(self):
        path = urllib.parse.unquote(self.path)
        client_ip = self.client_address[0]
        user_agent = self.headers.get('User-Agent', 'Desconhecido')
        
        print(f"📥 GET {path} de {client_ip}")
        print(f"   User-Agent: {user_agent}")
        
        # Rota principal - status
        if path == '/' or path == '':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            status = {
                "status": "online",
                "service": "FPKGi Local Server",
                "ip": IP_LOCAL,
                "port": PORTA,
                "endpoints": {
                    "games": f"http://{IP_LOCAL}:{PORTA}/GAMES.json",
                    "dlc": f"http://{IP_LOCAL}:{PORTA}/DLC.json",
                    "homebrew": f"http://{IP_LOCAL}:{PORTA}/HOMEBREW.json"
                }
            }
            self.wfile.write(json.dumps(status, indent=2).encode())
            print(f"✅ Status enviado para {client_ip}")
            return
        
        # Servir GAMES.json
        if path == '/GAMES.json':
            self.serve_games_with_proxy()
            return
        
        # Servir DLC.json (se existir)
        if path == '/DLC.json':
            if os.path.exists('DLC_format.json'):
                self.serve_json_file('DLC_format.json')
            elif os.path.exists('DLC.json'):
                self.serve_json_file('DLC.json')
            else:
                self.send_empty_json()
            return
        
        # Servir HOMEBREW.json
        if path == '/HOMEBREW.json':
            if os.path.exists('HOMEBREW_format.json'):
                self.serve_json_file('HOMEBREW_format.json')
            elif os.path.exists('HOMEBREW_original.json'):
                self.serve_json_file('HOMEBREW_original.json')
            else:
                self.send_empty_json()
            return
        
        # Proxy PKG - interceptar downloads e fazer proxy
        if path.startswith('/pkg/'):
            self.proxy_pkg_download(path[5:])
            return
        
        # Para outros arquivos, usar comportamento padrão
        super().do_GET()
    
    def serve_games_with_proxy(self):
        """Serve GAMES.json como array de objetos, compatível com FPKGi"""
        try:
            print("📦 Carregando GAMES_format.json...")
            with open('GAMES_format.json', 'r', encoding='utf-8') as f:
                data = json.load(f)

            games_list = []
            for url, info in data.get("DATA", {}).items():
                clean_url = url.replace('https://', '').replace('http://', '')
                new_url = f"http://{IP_LOCAL}:{PORTA}/pkg/{clean_url}"
                game = dict(info)
                game["url"] = new_url
                games_list.append(game)

            json_bytes = json.dumps(games_list, ensure_ascii=False).encode('utf-8')

            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', len(json_bytes))
            self.end_headers()
            self.wfile.write(json_bytes)
            print(f"✅ GAMES.json servido ({len(games_list)} jogos, {len(json_bytes)} bytes)")

        except FileNotFoundError:
            print("❌ GAMES_format.json não encontrado")
            self.send_error(404, "GAMES_format.json não encontrado")
        except json.JSONDecodeError as e:
            print(f"❌ Erro ao decodificar JSON: {e}")
            self.send_error(500, f"Erro no JSON: {e}")
        except Exception as e:
            print(f"❌ Erro ao servir GAMES.json: {e}")
            self.send_error(500, str(e))
    
    def proxy_pkg_download(self, pkg_path):
        """Faz proxy do download do PKG com headers melhorados"""
        # Apenas codificar espaços
        clean_path = pkg_path.replace(' ', '%20')
        original_url = f"https://{clean_path}"
        
        print(f"📦 PKG: {original_url}")
        
        try:
            # Headers mais completos para parecer um navegador real
            req = urllib.request.Request(original_url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Referer': 'https://archive.org/',
            })
            
            # Suporte a Range requests (para downloads grandes)
            if 'Range' in self.headers:
                req.add_header('Range', self.headers['Range'])
            
            # Adicionar delay pequeno para evitar rate limiting
            import time
            time.sleep(0.1)
            
            response = urllib.request.urlopen(req, timeout=120)
            
            # Enviar headers de resposta
            if 'Range' in self.headers and hasattr(response, 'status') and response.status == 206:
                self.send_response(206)
            else:
                self.send_response(200)
            
            content_length = response.headers.get('Content-Length')
            content_type = response.headers.get('Content-Type', 'application/octet-stream')
            
            self.send_header('Content-Type', content_type)
            if content_length:
                self.send_header('Content-Length', content_length)
            self.send_header('Accept-Ranges', 'bytes')
            
            if response.headers.get('Content-Range'):
                self.send_header('Content-Range', response.headers.get('Content-Range'))
            
            self.end_headers()
            
            # Stream do arquivo com chunks maiores
            bytes_sent = 0
            chunk_size = 1024 * 1024 * 2  # 2MB chunks para melhor performance
            
            while True:
                chunk = response.read(chunk_size)
                if not chunk:
                    break
                    
                try:
                    self.wfile.write(chunk)
                    bytes_sent += len(chunk)
                    
                    # Log a cada 50MB para não spammar
                    if bytes_sent % (50 * 1024 * 1024) == 0:  
                        print(f"   📥 {bytes_sent / (1024*1024):.1f} MB enviados...")
                except BrokenPipeError:
                    print("⚠️  Cliente desconectou durante o download")
                    break
            
            print(f"✅ Download completo: {bytes_sent / (1024*1024):.1f} MB")
            
        except urllib.error.HTTPError as e:
            if e.code == 401:
                print(f"❌ Erro 401: Acesso negado pelo servidor")
                print(f"💡 Tentando URL alternativa...")
                
                # Tentar URL direta sem proxy
                try:
                    self.send_response(302)
                    self.send_header('Location', original_url)
                    self.end_headers()
                    print(f"🔄 Redirecionado para: {original_url}")
                except:
                    self.send_error(401, "Acesso negado pelo servidor de origem")
            else:
                print(f"❌ Erro HTTP {e.code}: {e.reason}")
                self.send_error(e.code, str(e.reason))
        except Exception as e:
            print(f"❌ Erro no download: {e}")
            self.send_error(500, str(e))
    
    def serve_json_file(self, filename):
        """Serve um arquivo JSON"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = f.read()
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', len(data.encode('utf-8')))
            self.end_headers()
            self.wfile.write(data.encode('utf-8'))
            print(f"✅ Servido: {filename}")
        except FileNotFoundError:
            print(f"❌ Arquivo não encontrado: {filename}")
            self.send_empty_json()
        except Exception as e:
            print(f"❌ Erro ao servir {filename}: {e}")
            self.send_error(500, str(e))
    
    def send_empty_json(self):
        """Envia um JSON vazio"""
        data = '{"DATA": {}}'
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(data.encode())
    
    def log_message(self, format, *args):
        """Log personalizado"""
        print(f"📥 {args[0]}")

def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    print("=" * 60)
    print("🎮 SERVIDOR FPKGi LOCAL")
    print("=" * 60)
    print()
    print(f"📡 IP Local: {IP_LOCAL}")
    print(f"🌐 Porta: {PORTA}")
    print()
    print("📋 URLs para configurar no FPKGi:")
    print()
    print(f"   Games:    http://{IP_LOCAL}:{PORTA}/GAMES.json")
    print(f"   DLC:      http://{IP_LOCAL}:{PORTA}/DLC.json")
    print(f"   Homebrew: http://{IP_LOCAL}:{PORTA}/HOMEBREW.json")
    print()
    print("📁 Arquivos encontrados:")
    
    files_check = [
        ('GAMES_format.json', 'Games'),
        ('DLC_format.json', 'DLC'),
        ('DLC.json', 'DLC (alternativo)'),
        ('HOMEBREW_original.json', 'Homebrew')
    ]
    
    for filename, desc in files_check:
        if os.path.exists(filename):
            size = os.path.getsize(filename)
            print(f"   ✅ {filename} ({size:,} bytes)")
        else:
            print(f"   ⚠️  {filename} não encontrado")
    
    print()
    print("=" * 60)
    print("🔧 COMO CONFIGURAR NO PS4:")
    print("=" * 60)
    print()
    print("1. Abra o FPKGi no PS4")
    print("2. Vá em Menu (botão △) → Settings → Content URLs")
    print("3. Configure:")
    print(f"   - Games: http://{IP_LOCAL}:{PORTA}/GAMES.json")
    print()
    print("4. Salve e reinicie o FPKGi")
    print()
    print("=" * 60)
    print("⏹️  Pressione Ctrl+C para parar")
    print("=" * 60)
    print()
    
    server = HTTPServer(('', PORTA), FPKGiHandler)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Servidor parado!")
        server.shutdown()

if __name__ == '__main__':
    main()
