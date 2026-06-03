"""
Configurador automático FPKGi para PS4
Envia configuração via FTP automaticamente
"""
import ftplib
import json
import socket

def get_local_ip():
    """Detecta o IP local"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "192.168.15.6"

def enviar_config_automatico():
    """Envia configuração diretamente para o PS4"""
    
    IP_LOCAL = get_local_ip()
    PS4_IP = "192.168.15.3"  # Ajuste se necessário
    
    print("🎮 CONFIGURADOR AUTOMÁTICO FPKGi")
    print("=" * 50)
    print(f"💻 IP do PC: {IP_LOCAL}")
    print(f"🎮 IP do PS4: {PS4_IP}")
    print()
    
    # Configuração completa do FPKGi
    config = {
        "FILTERING": {
            "CONTENT": "all",
            "SORT": {
                "type": "name", 
                "ascending": True
            },
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
                "background_uri": f"http://{IP_LOCAL}:8080/background.png",
                "backgroundMusic": False,
                "populateViaWeb": True,
                "enableUpdates": True
            },
            "CONTENT_URLS": {
                "PS1": None,
                "PS2": None,
                "PSP": None,
                "PS5": None,
                "games": f"http://{IP_LOCAL}:8080/GAMES.json",
                "apps": f"http://{IP_LOCAL}:8080/GAMES.json",
                "updates": None,
                "DLC": f"http://{IP_LOCAL}:8080/DLC.json", 
                "demos": None,
                "homebrew": f"http://{IP_LOCAL}:8080/HOMEBREW.json",
                "emulators": None,
                "themes": None
            }
        }
    }
    
    # Tentar conexão FTP com diferentes portas
    portas_ftp = [1337, 2121, 21]  # Portas comuns do PS4
    conectado = False
    ftp = None
    
    for porta in portas_ftp:
        try:
            print(f"🔗 Tentando conectar em {PS4_IP}:{porta}...")
            
            ftp = ftplib.FTP()
            ftp.connect(PS4_IP, porta, timeout=5)
            ftp.login()  # Login anônimo
            
            print(f"✅ Conectado na porta {porta}!")
            conectado = True
            break
            
        except Exception as e:
            print(f"❌ Porta {porta}: Falha na conexão")
            if ftp:
                try:
                    ftp.close()
                except:
                    pass
            continue
    
    if not conectado:
        print("\n💡 NENHUMA PORTA FTP RESPONDEU")
        print("Verifique se o FTP está ativo no PS4")
        return False
        
    # Continuar com o envio do arquivo
    try:
        # Navegar/criar diretório FPKGi
        try:
            ftp.cwd("/user/data/FPKGi")
            print("📁 Acessando /user/data/FPKGi")
        except:
            try:
                ftp.mkd("/user/data/FPKGi")
                ftp.cwd("/user/data/FPKGi")
                print("📁 Diretório criado: /user/data/FPKGi")
            except:
                print("⚠️  Usando diretório atual")
        
        # Converter config para JSON
        config_json = json.dumps(config, indent=2, ensure_ascii=False)
        
        # Criar arquivo temporário
        temp_file = "fpkgi_temp.json"
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(config_json)
        
        # Enviar arquivo
        print("📤 Enviando configuração...")
        with open(temp_file, 'rb') as f:
            ftp.storbinary('STOR fpkgi.json', f)
        
        # Limpar arquivo temporário
        import os
        os.remove(temp_file)
        
        print("✅ Configuração enviada com sucesso!")
        ftp.quit()
        
        print("\n🎯 CONFIGURAÇÃO APLICADA:")
        print(f"   Games: http://{IP_LOCAL}:8080/GAMES.json")
        print(f"   DLC: http://{IP_LOCAL}:8080/DLC.json") 
        print(f"   Homebrew: http://{IP_LOCAL}:8080/HOMEBREW.json")
        print(f"   Background: http://{IP_LOCAL}:8080/background.png")
        print("\n🔄 Reinicie o FPKGi no PS4 para aplicar!")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao enviar arquivo: {e}")
        print("\n💡 CONFIGURAÇÃO MANUAL:")
        print("Use o arquivo config_ps4.json criado anteriormente")
        if ftp:
            try:
                ftp.quit()
            except:
                pass
        return False

if __name__ == "__main__":
    enviar_config_automatico()
