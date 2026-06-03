"""
Gerador de URLs FPKGi - Configuração Automática
"""
import socket
import json

def get_local_ip():
    """Detecta o IP local automaticamente"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "192.168.15.6"

def gerar_urls():
    """Gera URLs automaticamente"""
    ip_local = get_local_ip()
    porta = 8080
    
    urls = {
        "games": f"http://{ip_local}:{porta}/GAMES.json",
        "apps": f"http://{ip_local}:{porta}/GAMES.json", 
        "DLC": f"http://{ip_local}:{porta}/DLC.json",
        "homebrew": f"http://{ip_local}:{porta}/HOMEBREW.json"
    }
    
    print("🎮 URLS FPKGI CONFIGURADAS AUTOMATICAMENTE")
    print("=" * 60)
    print(f"💻 IP detectado: {ip_local}")
    print(f"🌐 Porta: {porta}")
    print()
    print("📋 URLS PARA O FPKGI:")
    print("=" * 40)
    for tipo, url in urls.items():
        print(f"{tipo:10} → {url}")
    
    print()
    print("🔧 COMO CONFIGURAR NO PS4:")
    print("1. Abra o FPKGi")
    print("2. Aperte △ (triângulo)")
    print("3. Settings → Content URLs")
    print("4. Configure as URLs acima")
    print("5. Salve e reinicie o FPKGi")
    print()
    
    # Salvar configuração JSON
    config = {
        "FILTERING": {
            "CONTENT": "all",
            "SORT": {"type": "name", "ascending": True},
            "REGIONS": ["USA", "Europe", "Japan", "Asia"]
        },
        "PREFERENCES": {
            "DOWNLOADS": {
                "directDownload": True,
                "downloadPath": "/user/data/FPKGi/Downloads/",
                "installAfter": False,
                "deleteAfter": False,
                "deleteOnCancel": True
            },
            "APPLICATION": {
                "background_uri": f"http://{ip_local}:{porta}/background.png",
                "backgroundMusic": False,
                "populateViaWeb": True,
                "enableUpdates": True
            },
            "CONTENT_URLS": urls
        }
    }
    
    # Salvar arquivo de configuração
    config_file = "fpkgi_config_final.json"
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Configuração salva em: {config_file}")
    print("📤 Use este arquivo para enviar via FTP ao PS4")
    
    return urls

if __name__ == "__main__":
    gerar_urls()
