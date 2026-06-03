import json
from urllib.parse import quote

# Mapeamento de regiões para letras
region_map = {
    'USA': 'u',
    'EUR': 'e',
    'JAP': 'j'
}

# Mapeamento de regiões para siglas
region_sigla = {
    'USA': 'US',
    'EUR': 'EU',
    'JAP': 'JP'
}

# Mapeamento de regiões para idioma
region_lang = {
    'USA': 'EN',
    'EUR': 'EN',
    'JAP': 'JP'
}

# Ler o arquivo atual
with open('GAMES_format.json', 'r', encoding='utf-8-sig') as f:
    data = json.load(f)

novo_formato = {"DATA": {}}

for url_atual, game_info in data.get("DATA", {}).items():
    region = game_info.get('region', 'USA')
    name = game_info.get('name', '')
    version = game_info.get('version', '01.00')
    
    # Obter a letra correspondente
    region_letter = region_map.get(region, 'n')
    region_sig = region_sigla.get(region, 'US')
    lang = region_lang.get(region, 'EN')
    
    # Construir o nome do arquivo
    # Formato: "Nome do Jogo - [REGIAO] [LINGUA] [VERSAO].pkg"
    filename = f"{name} - [{region_sig}] [{lang}] [{version}].pkg"
    filename_encoded = quote(filename, safe='[].-')
    
    # Construir a URL completa
    url_novo = f"https://archive.org/download/ps4-fpkg-collection-english-{region_letter}/{filename_encoded}"
    
    novo_formato["DATA"][url_novo] = game_info

# Salvar no formato correto
with open('GAMES_format.json', 'w', encoding='utf-8') as f:
    json.dump(novo_formato, f, ensure_ascii=False, indent=2)

print("Arquivo reconstruído com sucesso!")
print(f"Total de jogos: {len(novo_formato['DATA'])}")

# Mostrar alguns exemplos
exemplos = list(novo_formato['DATA'].items())[:3]
print("\nExemplos de URLs geradas:")
for url, info in exemplos:
    print(f"  {url}")
