"""
Teste de conexão com Archive.org
"""
import urllib.request
import ssl

# Ignorar SSL
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# URL de teste (jogo pequeno)
url = "https://archive.org/download/ps4-fpkg-collection-english-a/A%20Short%20Hike%20-%20%5BEU%5D%20%5BEN%5D%20%5B1.01%5D.pkg"

print("Testando conexão com Archive.org...")
print(f"URL: {url[:60]}...")
print()

try:
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://archive.org/'
    })
    req.get_method = lambda: 'HEAD'
    
    response = urllib.request.urlopen(req, context=ctx, timeout=15)
    
    print("✅ CONEXÃO OK!")
    print(f"   Status: {response.status}")
    print(f"   Content-Length: {response.headers.get('Content-Length')} bytes")
    print(f"   Content-Type: {response.headers.get('Content-Type')}")
    
except urllib.error.HTTPError as e:
    print(f"❌ HTTP Error: {e.code} - {e.reason}")
    if e.code == 403:
        print("   O Archive.org está bloqueando o acesso!")
    elif e.code == 503:
        print("   Servidor ocupado, tente novamente.")
        
except Exception as e:
    print(f"❌ Erro: {e}")
