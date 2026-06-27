"""
Proxy Server para FPKGi - Faz login no Archive.org e serve os PKGs
"""

from flask import Flask, Response, request, jsonify
import requests
import os
import json
import re
from urllib.parse import unquote

app = Flask(__name__)

# Configurações do Archive.org (você vai configurar depois)
ARCHIVE_EMAIL = os.environ.get('ARCHIVE_EMAIL', '')
ARCHIVE_PASSWORD = os.environ.get('ARCHIVE_PASSWORD', '')

# URL base do Archive.org
ARCHIVE_BASE = "https://archive.org"

# Sessão global para manter o login
session = requests.Session()
logged_in = False

def login_archive():
    """Faz login no Archive.org"""
    global logged_in, session
    
    if not ARCHIVE_EMAIL or not ARCHIVE_PASSWORD:
        print("⚠️ Credenciais não configuradas!")
        return False
    
    try:
        # Página de login
        login_url = "https://archive.org/account/login"
        
        # Fazer login
        login_data = {
            'username': ARCHIVE_EMAIL,
            'password': ARCHIVE_PASSWORD,
            'remember': 'true',
            'referer': 'https://archive.org/',
            'login': 'true',
            'submit_by_js': 'true'
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://archive.org',
            'Referer': 'https://archive.org/account/login'
        }
        
        response = session.post(login_url, data=login_data, headers=headers)
        
        # Verificar se logou
        if 'logged-in' in response.text or response.status_code == 200:
            logged_in = True
            print("✅ Login no Archive.org realizado com sucesso!")
            return True
        else:
            print("❌ Falha no login")
            return False
            
    except Exception as e:
        print(f"❌ Erro no login: {e}")
        return False

@app.route('/')
def home():
    """Página inicial"""
    return jsonify({
        "status": "online",
        "service": "FPKGi Proxy Server",
        "logged_in": logged_in,
        "endpoints": {
            "json": "/json/<path>",
            "pkg": "/pkg/<path>",
            "status": "/status"
        }
    })

@app.route('/status')
def status():
    """Status do servidor"""
    return jsonify({
        "online": True,
        "logged_in": logged_in,
        "archive_configured": bool(ARCHIVE_EMAIL and ARCHIVE_PASSWORD)
    })

@app.route('/login')
def do_login():
    """Força um novo login"""
    success = login_archive()
    return jsonify({"success": success, "logged_in": logged_in})

@app.route('/GAMES.json')
def games_json():
    """Retorna o JSON de games com URLs originais do Archive.org"""
    try:
        # URL original do JSON
        json_url = "https://ia600801.us.archive.org/10/items/ps4-fpkg-collection-english-fpkgi/GAMES.json"
        
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = session.get(json_url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            # Retornar o JSON original sem modificar as URLs
            # O PS4 vai baixar direto do Archive.org
            return Response(response.content, mimetype='application/json', headers={
                'Access-Control-Allow-Origin': '*',
                'Cache-Control': 'public, max-age=3600'
            })
        else:
            return jsonify({"error": "Falha ao buscar JSON", "status": response.status_code}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/DLC.json')
def dlc_json():
    """Retorna o JSON de DLC"""
    try:
        json_url = "https://ia600801.us.archive.org/10/items/ps4-fpkg-collection-english-fpkgi/DLC.json"
        
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = session.get(json_url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            return Response(response.content, mimetype='application/json', headers={
                'Access-Control-Allow-Origin': '*',
                'Cache-Control': 'public, max-age=3600'
            })
        else:
            return jsonify({"error": "Falha ao buscar JSON"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/HOMEBREW.json')
def homebrew_json():
    """Retorna o JSON de Homebrew"""
    try:
        json_url = "https://ia600801.us.archive.org/10/items/ps4-fpkg-collection-english-fpkgi/HOMEBREW.json"
        
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = session.get(json_url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            return Response(response.content, mimetype='application/json', headers={
                'Access-Control-Allow-Origin': '*',
                'Cache-Control': 'public, max-age=3600'
            })
        else:
            return jsonify({"error": "Falha ao buscar JSON"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/pkg/<path:pkg_path>')
def proxy_pkg(pkg_path):
    """Faz proxy do download do PKG"""
    global logged_in
    
    # Garantir que está logado
    if not logged_in:
        login_archive()
    
    try:
        # Reconstruir URL original
        original_url = f"https://{pkg_path}"
        
        print(f"📦 Baixando: {original_url}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://archive.org/'
        }
        
        # Fazer request com stream para arquivos grandes
        response = session.get(original_url, headers=headers, stream=True)
        
        if response.status_code == 200:
            # Criar resposta de streaming
            def generate():
                for chunk in response.iter_content(chunk_size=1024*1024):  # 1MB chunks
                    if chunk:
                        yield chunk
            
            # Pegar headers importantes
            content_length = response.headers.get('Content-Length')
            
            resp_headers = {
                'Content-Type': 'application/octet-stream',
                'Accept-Ranges': 'bytes',
                'Access-Control-Allow-Origin': '*',
                'Content-Disposition': f'attachment; filename="{os.path.basename(unquote(pkg_path)) or "download.pkg"}"'
            }
            
            if content_length:
                resp_headers['Content-Length'] = content_length
            
            return Response(generate(), headers=resp_headers)
        else:
            print(f"❌ Erro {response.status_code} ao baixar {original_url}")
            return jsonify({"error": f"Falha ao baixar PKG: {response.status_code}"}), response.status_code
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return jsonify({"error": str(e)}), 500

# Fazer login ao iniciar
@app.before_request
def ensure_logged_in():
    global logged_in
    if not logged_in and ARCHIVE_EMAIL and ARCHIVE_PASSWORD:
        login_archive()

if __name__ == '__main__':
    print("🎮 FPKGi Proxy Server")
    print("=" * 40)
    
    if ARCHIVE_EMAIL and ARCHIVE_PASSWORD:
        login_archive()
    else:
        print("⚠️ Configure ARCHIVE_EMAIL e ARCHIVE_PASSWORD!")
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
