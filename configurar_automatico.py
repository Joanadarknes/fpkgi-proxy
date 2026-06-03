"""
Configurador FTP Automático - Envia config direto para o PS4
"""
import ftplib
import json
import socket
import time

def configurar_fpkgi_automatico():
    """Configura automaticamente o FPKGi no PS4 via FTP"""
    
    # IPs detectados automaticamente
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        IP_PC = s.getsockname()[0]
        s.close()
    except:
        IP_PC = "192.168.15.6"
    
    # IP do PS4 (mesmo range de rede)
    IP_PS4 = IP_PC.rsplit('.', 1)[0] + '.3'  # Assume que PS4 termina em .3
    
    print("🤖 CONFIGURADOR AUTOMÁTICO FPKGi")
    print("=" * 50)
    print(f"💻 PC: {IP_PC}:8080")
    print(f"🎮 PS4: {IP_PS4}")
    print()
    
    # Configuração completa
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
                "background_uri": f"http://{IP_PC}:8080/background.png",
                "backgroundMusic": False,
                "populateViaWeb": True,
                "enableUpdates": True
            },
            "CONTENT_URLS": {
                "PS1": None,
                "PS2": None,
                "PSP": None,
                "PS5": None,
                "games": f"http://{IP_PC}:8080/GAMES.json",
                "apps": f"http://{IP_PC}:8080/GAMES.json",
                "updates": None,
                "DLC": f"http://{IP_PC}:8080/DLC.json",
                "demos": None,
                "homebrew": f"http://{IP_PC}:8080/HOMEBREW.json",
                "emulators": None,
                "themes": None
            }
        }
    }
    
    # Testar diferentes combinações de porta FTP
    portas_ftp = [1337, 2121, 21, 1338]
    usuarios = ["", "anonymous", "ps4"]
    
    conectado = False
    
    for porta in portas_ftp:
        for usuario in usuarios:
            try:
                print(f"🔗 Tentando {IP_PS4}:{porta} (user: {usuario or 'vazio'})...")
                
                ftp = ftplib.FTP()
                ftp.set_debuglevel(0)  # Sem debug verbose
                ftp.connect(IP_PS4, porta, timeout=3)
                
                if usuario:
                    ftp.login(usuario, "")
                else:
                    ftp.login()
                
                print(f"✅ CONECTADO na porta {porta}!")
                conectado = True
                break
                
            except Exception as e:
                print(f"❌ Falhou: {str(e)[:50]}")
                continue
        
        if conectado:
            break
    
    if not conectado:
        print("\n❌ NÃO FOI POSSÍVEL CONECTAR VIA FTP")
        print("💡 Possíveis soluções:")
        print("1. Ative o servidor FTP no PS4 (HEN/CFW)")
        print("2. Verifique se o PS4 está ligado")
        print("3. Confirme se estão na mesma rede")
        return False
    
    try:
        # Navegara para diretório FPKGi
        print("📁 Acessando diretório FPKGi...")
        try:
            ftp.cwd("/user/data/FPKGi")
        except:
            try:
                ftp.mkd("/user/data/FPKGi")
                ftp.cwd("/user/data/FPKGi")
                print("✅ Diretório criado!")
            except:
                print("⚠️ Usando diretório raiz")
        
        # Criar arquivo de configuração
        config_json = json.dumps(config, indent=2, ensure_ascii=False)
        
        with open("fpkgi_temp.json", "w", encoding="utf-8") as f:
            f.write(config_json)
        
        # Enviar arquivo
        print("📤 Enviando configuração...")
        with open("fpkgi_temp.json", "rb") as f:
            ftp.storbinary("STOR fpkgi.json", f)
        
        print("✅ CONFIGURAÇÃO ENVIADA COM SUCESSO!")
        
        # Cleanup
        import os
        os.remove("fpkgi_temp.json")
        ftp.quit()
        
        print("\n🎯 CONFIGURAÇÃO APLICADA:")
        print(f"   Games: http://{IP_PC}:8080/GAMES.json")
        print(f"   DLC: http://{IP_PC}:8080/DLC.json")
        print(f"   Homebrew: http://{IP_PC}:8080/HOMEBREW.json")
        print("\n🔄 REINICIE O FPKGI NO PS4!")
        print("📋 Use R1 para atualizar a lista")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao enviar: {e}")
        if 'ftp' in locals():
            ftp.quit()
        return False

if __name__ == "__main__":
    configurar_fpkgi_automatico()
