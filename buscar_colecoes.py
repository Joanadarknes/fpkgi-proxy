import json
from urllib.request import urlopen
from urllib.error import URLError
import time
import re

# Letras das coleções disponíveis
colecoes = ['c', 's']  # Começar com as que você mencionou

novo_formato = {"DATA": {}}
jogos_encontrados = 0

print("Buscando arquivos nas coleções do Archive.org...")
print("=" * 60)

for letra in colecoes:
    colecao_url = f"https://archive.org/download/ps4-fpkg-collection-english-{letra}/"
    
    try:
        print(f"\nBuscando coleção: ps4-fpkg-collection-english-{letra}")
        response = urlopen(colecao_url, timeout=15)
        html = response.read().decode('utf-8', errors='ignore')
        
        # Procurar por links de .pkg usando regex
        matches = re.findall(r'href="([^"]+\.pkg)"', html)
        
        print(f"  Encontrados {len(matches)} arquivos .pkg")
        
        for arquivo in matches:
            if not arquivo.startswith('http'):  # Se for caminho relativo
                url_completa = f"https://archive.org/download/ps4-fpkg-collection-english-{letra}/{arquivo}"
            else:
                url_completa = arquivo
            
            # Limpar o nome do arquivo
            nome_limpo = arquivo.replace('%20', ' ').replace('.pkg', '')
            
            game_info = {
                "title_id": "",
                "region": "",
                "name": nome_limpo,
                "version": "01.00",
                "release": "",
                "size": 0,
                "min_fw": "9.00",
                "cover_url": ""
            }
            
            novo_formato["DATA"][url_completa] = game_info
            jogos_encontrados += 1
            print(f"    ✓ {nome_limpo[:60]}")
    
    except URLError as e:
        print(f"  Erro de conexão: {e}")
    except Exception as e:
        print(f"  Erro: {e}")
    
    time.sleep(1)

print("\n" + "=" * 60)
print(f"Total de jogos encontrados: {jogos_encontrados}")

# Salvar arquivo
with open('GAMES_format.json', 'w', encoding='utf-8') as f:
    json.dump(novo_formato, f, ensure_ascii=False, indent=2)

print(f"\nArquivo GAMES_format.json atualizado com {len(novo_formato['DATA'])} jogos!")
