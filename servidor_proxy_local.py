"""
Servidor Proxy Local para FPKGi
================================
Seu PC baixa do Archive.org e repassa para o PS4
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import socket
import json
import os
import urllib.parse
import urllib.request
import ssl
import http.cookiejar

# Configurações
PORTA = 8080

# Credenciais do Archive.org
ARCHIVE_EMAIL = "joanadarknes2233@gmail.com"
ARCHIVE_PASSWORD = "Teste123#"

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

# Criar contexto SSL que ignora verificação (para Archive.org)
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# Cookie jar e opener global para manter sessão
cookie_jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(
    urllib.request.HTTPCookieProcessor(cookie_jar),
    urllib.request.HTTPSHandler(context=ssl_context)
)
logged_in = False

def login_archive():
    """Faz login no Archive.org"""
    global logged_in
    
    print("🔐 Fazendo login no Archive.org...")
    
    try:
        # Primeiro, acessar a página de login para pegar cookies iniciais
        login_page = urllib.request.Request(
            'https://archive.org/account/login',
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        )
        opener.open(login_page, timeout=30)
        
        # Dados do login
        login_data = urllib.parse.urlencode({
            'username': ARCHIVE_EMAIL,
            'password': ARCHIVE_PASSWORD,
            'remember': 'CHECKED',
            'referer': 'https://archive.org/',
            'login': 'true',
            'submit_by_js': 'true'
        }).encode('utf-8')
        
        req = urllib.request.Request(
            'https://archive.org/account/login',
            data=login_data,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Origin': 'https://archive.org',
                'Referer': 'https://archive.org/account/login',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
        )
        
        response = opener.open(req, timeout=30)
        response_text = response.read().decode('utf-8', errors='ignore')
        
        # Verificar se logou com sucesso
        logged_in = False
        for cookie in cookie_jar:
            if 'logged-in-user' in cookie.name or 'logged-in-sig' in cookie.name or cookie.name == 'logged-in-user':
                logged_in = True
                print(f"✅ Cookie de login encontrado: {cookie.name}")
                break
        
        # Verificar também na resposta HTML
        if not logged_in and ('user-menu' in response_text or 'logout' in response_text.lower()):
            logged_in = True
            print("✅ Login detectado via HTML!")
        
        if logged_in:
            print("✅ Login realizado com sucesso!")
            return True
        else:
            print("⚠️ Login pode não ter funcionado, mas tentando continuar...")
            logged_in = True  # Tentar mesmo assim
            return True
            
    except Exception as e:
        print(f"❌ Erro no login: {e}")
        print("⚠️ Continuando sem login...")
        logged_in = True  # Tentar mesmo sem login
        return False

class ProxyHandler(BaseHTTPRequestHandler):
    
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, HEAD, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        super().end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()
    
    def do_HEAD(self):
        """Responde HEAD requests (PS4 usa para verificar tamanho)"""
        self.do_GET(head_only=True)
    
    def do_GET(self, head_only=False):
        path = urllib.parse.unquote(self.path)
        
        # Status
        if path == '/':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            if not head_only:
                status = {"status": "online", "service": "FPKGi Local Proxy", "ip": IP_LOCAL}
                self.wfile.write(json.dumps(status).encode())
            return
        
        # GAMES.json - reescreve URLs para passar pelo proxy local
        if path == '/GAMES.json':
            self.serve_games_json()
            return
        
        # DLC.json
        if path == '/DLC.json':
            self.serve_dlc_json()
            return
        
        # HOMEBREW.json
        if path == '/HOMEBREW.json':
            self.serve_homebrew_json()
            return
        
        # Proxy de PKG - /pkg/archive.org/download/...
        if path.startswith('/pkg/'):
            self.proxy_pkg(path[5:], head_only)
            return
        
        self.send_error(404)
    
    def serve_games_json(self):
        """Serve GAMES.json com URLs reescritas para o proxy local"""
        try:
            # Usar arquivo local se existir
            if os.path.exists('GAMES_format.json'):
                with open('GAMES_format.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                # Baixar do Archive.org
                url = "https://ia600801.us.archive.org/10/items/ps4-fpkg-collection-english-fpkgi/GAMES.json"
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, context=ssl_context, timeout=30) as response:
                    data = json.loads(response.read().decode())
            
            # Reescrever URLs para passar pelo proxy local
            new_data = {"DATA": {}}
            for url, info in data.get("DATA", {}).items():
                # Converter https://archive.org/... para http://IP:8080/pkg/archive.org/...
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
            print(f"❌ Erro ao servir GAMES.json: {e}")
            self.send_error(500, str(e))
    
    def serve_dlc_json(self):
        """Serve DLC.json"""
        try:
            url = "https://ia600801.us.archive.org/10/items/ps4-fpkg-collection-english-fpkgi/DLC.json"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, context=ssl_context, timeout=30) as response:
                data = json.loads(response.read().decode())
            
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
            
        except Exception as e:
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"DATA": {}}')
    
    def serve_homebrew_json(self):
        """Serve HOMEBREW.json"""
        try:
            if os.path.exists('HOMEBREW_original.json'):
                with open('HOMEBREW_original.json', 'r', encoding='utf-8') as f:
                    data = f.read()
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(data.encode())
            else:
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(b'{"DATA": {}}')
        except:
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"DATA": {}}')
    
    def proxy_pkg(self, pkg_path, head_only=False):
        """Faz proxy do download do PKG - tenta público primeiro, depois com login"""
        global logged_in
        
        # APENAS codificar espaços para %20 - nada mais!
        clean_path = pkg_path.replace(' ', '%20')
        original_url = f"https://{clean_path}"
        
        print(f"📦 {'HEAD' if head_only else 'GET'}: {original_url}")
        
        # Tentar primeiro SEM login (mais rápido para arquivos públicos)
        success = self._try_download_public(original_url, head_only)
        if success:
            return
        
        # Se falhou, garantir login e tentar novamente
        print(f"🔐 Tentando com autenticação...")
        if not logged_in:
            login_archive()
        
        success = self._try_download_with_cookies(original_url, head_only)
        if not success:
            print(f"❌ Falha mesmo com autenticação")
            self.send_error(403, "Arquivo requer permissões especiais")
    
    def _try_download_public(self, url, head_only=False):
        """Tenta download público SEM cookies"""
        try:
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': '*/*',
                'Referer': 'https://archive.org/',
            })
            
            if head_only:
                req.get_method = lambda: 'HEAD'
            
            if 'Range' in self.headers:
                req.add_header('Range', self.headers['Range'])
            
            # Usar urllib padrão sem cookies
            response = urllib.request.urlopen(req, context=ssl_context, timeout=60)
            
            return self._send_response(response, head_only, "público")
                
        except urllib.error.HTTPError as e:
            if e.code == 401:
                print(f"   ❌ Acesso público negado (401) - arquivo requer login")
                return False
            else:
                print(f"   ❌ Erro público: {e}")
                return False
        except Exception as e:
            print(f"   ❌ Erro público: {e}")
            return False
    
    def _try_download_with_cookies(self, url, head_only=False):
        """Tenta download COM cookies de sessão"""
        try:
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': '*/*',
                'Referer': 'https://archive.org/',
            })
            
            if head_only:
                req.get_method = lambda: 'HEAD'
            
            if 'Range' in self.headers:
                req.add_header('Range', self.headers['Range'])
            
            # Usar opener com cookies
            response = opener.open(req, timeout=60)
            
            return self._send_response(response, head_only, "autenticado")
                
        except Exception as e:
            print(f"   ❌ Erro autenticado: {e}")
            return False
    
    def _send_response(self, response, head_only, source_type):
        """Envia a resposta HTTP para o PS4"""
        try:
            # Responder
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
            
            if not head_only:
                bytes_sent = 0
                while True:
                    chunk = response.read(1024 * 1024)
                    if not chunk:
                        break
                    self.wfile.write(chunk)
                    bytes_sent += len(chunk)
                    if bytes_sent % (10 * 1024 * 1024) == 0:
                        print(f"   📥 {bytes_sent / (1024*1024):.1f} MB enviados...")
                
                print(f"✅ Download {source_type} completo: {bytes_sent / (1024*1024):.1f} MB")
            else:
                print(f"✅ HEAD {source_type} OK - Size: {content_length}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro enviando resposta: {e}")
            return False
    
    def log_message(self, format, *args):
        pass  # Silenciar logs padrão

def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)) or '.')
    
    print("=" * 60)
    print("🎮 SERVIDOR PROXY LOCAL PARA FPKGi")
    print("=" * 60)
    print()
    
    # Fazer login no Archive.org
    login_archive()
    
    print()
    print(f"📡 IP Local: {IP_LOCAL}")
    print(f"🌐 Porta: {PORTA}")
    print()
    print("📋 URL para configurar no FPKGi (PS4):")
    print()
    print(f"   Games: http://{IP_LOCAL}:{PORTA}/GAMES.json")
    print()
    print("=" * 60)
    print("⚠️  MANTENHA ESTE SERVIDOR RODANDO ENQUANTO BAIXA JOGOS!")
    print("=" * 60)
    print()
    print("⏹️  Pressione Ctrl+C para parar")
    print()
    
    server = HTTPServer(('', PORTA), ProxyHandler)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Servidor parado!")
        server.shutdown()

if __name__ == '__main__':
    main()
