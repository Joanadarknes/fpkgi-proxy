import ftplib

# Configurações do FTP
FTP_HOST = "192.168.15.6"
FTP_PORT = 2121  # Porta padrão de alguns apps FTP no PS4
FTP_USER = "anonymous"
FTP_PASS = ""
ARQUIVO_LOCAL = "GAMES_format.json"
DESTINOS = [
    "/data/FPKGi/config.json"
]
ARQUIVO_LOCAL = "config.json"

with ftplib.FTP() as ftp:
    ftp.connect(FTP_HOST, FTP_PORT)
    ftp.login(FTP_USER, FTP_PASS)
    for destino in DESTINOS:
        try:
            with open(ARQUIVO_LOCAL, "rb") as f:
                ftp.storbinary(f"STOR {destino}", f)
            print(f"Arquivo enviado para {FTP_HOST}:{destino}")
        except Exception as e:
            print(f"Falha ao enviar para {destino}: {e}")
