"""
Envia o arquivo de configuração para o PS4 via FTP
"""
from ftplib import FTP
import os

# Configurações do PS4
PS4_IP = "192.168.15.3"
PS4_PORT = 2121
REMOTE_PATH = "/user/data/FPKGi/"
LOCAL_FILE = "fpkgi_config.json"
REMOTE_FILE = "config.json"

print("=" * 50)
print("📤 ENVIANDO CONFIG PARA O PS4")
print("=" * 50)
print()
print(f"📡 PS4 IP: {PS4_IP}:{PS4_PORT}")
print(f"📁 Arquivo local: {LOCAL_FILE}")
print(f"📂 Destino: {REMOTE_PATH}{REMOTE_FILE}")
print()

try:
    # Conectar ao PS4
    print("🔌 Conectando ao PS4...")
    ftp = FTP()
    ftp.connect(PS4_IP, PS4_PORT, timeout=10)
    print("✅ Conectado!")
    
    # Login anônimo (PS4 não precisa de senha)
    ftp.login()
    print("✅ Login OK!")
    
    # Ir para o diretório
    print(f"📂 Navegando para {REMOTE_PATH}...")
    ftp.cwd(REMOTE_PATH)
    print("✅ Diretório OK!")
    
    # Listar arquivos atuais
    print("\n📋 Arquivos atuais no PS4:")
    files = ftp.nlst()
    for f in files:
        print(f"   - {f}")
    
    # Enviar arquivo
    print(f"\n📤 Enviando {LOCAL_FILE}...")
    with open(LOCAL_FILE, 'rb') as f:
        ftp.storbinary(f'STOR {REMOTE_FILE}', f)
    print("✅ Arquivo enviado com sucesso!")
    
    # Verificar se foi
    print("\n📋 Arquivos após envio:")
    files = ftp.nlst()
    for f in files:
        print(f"   - {f}")
    
    ftp.quit()
    print("\n" + "=" * 50)
    print("🎉 PRONTO! Agora reinicie o FPKGi no PS4")
    print("=" * 50)
    
except Exception as e:
    print(f"\n❌ ERRO: {e}")
    print("\n⚠️  Verifique se:")
    print("   1. O PS4 está ligado e com o FTP ativado")
    print("   2. O IP está correto (192.168.15.3)")
    print("   3. A porta está correta (2121)")
