"""
Teste completo de login e download do Archive.org
"""
import urllib.request
import urllib.parse
import ssl
import http.cookiejar

# Credenciais
EMAIL = "joanadarknes2233@gmail.com"
PASSWORD = "Teste123#"

# SSL
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Cookies
cookie_jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(
    urllib.request.HTTPCookieProcessor(cookie_jar),
    urllib.request.HTTPSHandler(context=ctx)
)

print("=" * 50)
print("🔐 TESTE DE LOGIN NO ARCHIVE.ORG")
print("=" * 50)
print()

# 1. Fazer login
print("1️⃣ Fazendo login...")
login_data = urllib.parse.urlencode({
    'username': EMAIL,
    'password': PASSWORD,
    'remember': 'true',
    'referer': 'https://archive.org/',
    'login': 'true',
    'submit_by_js': 'true'
}).encode('utf-8')

req = urllib.request.Request(
    'https://archive.org/account/login',
    data=login_data,
    headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'https://archive.org',
        'Referer': 'https://archive.org/account/login'
    }
)

try:
    response = opener.open(req, timeout=30)
    print(f"   Status: {response.status}")
    
    print("\n   Cookies recebidos:")
    for cookie in cookie_jar:
        print(f"   - {cookie.name}: {cookie.value[:20]}...")
    
    print("\n✅ Login enviado!")
except Exception as e:
    print(f"❌ Erro no login: {e}")
    exit(1)

# 2. Testar acesso ao PKG
print()
print("2️⃣ Testando acesso ao PKG...")

pkg_url = "https://archive.org/download/ps4-fpkg-collection-english-a/A%20Short%20Hike%20-%20%5BEU%5D%20%5BEN%5D%20%5B1.01%5D.pkg"

req2 = urllib.request.Request(pkg_url, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://archive.org/'
})
req2.get_method = lambda: 'HEAD'

try:
    response2 = opener.open(req2, timeout=30)
    print(f"   Status: {response2.status}")
    print(f"   Content-Length: {response2.headers.get('Content-Length')} bytes")
    print(f"   Content-Type: {response2.headers.get('Content-Type')}")
    print()
    print("✅ ACESSO AO PKG OK! O download deve funcionar!")
except urllib.error.HTTPError as e:
    print(f"❌ HTTP Error: {e.code} - {e.reason}")
    if e.code == 401:
        print("   ⚠️ Login não funcionou ou a conta precisa de verificação")
    elif e.code == 403:
        print("   ⚠️ Acesso negado - Archive.org pode estar bloqueando")
except Exception as e:
    print(f"❌ Erro: {e}")
