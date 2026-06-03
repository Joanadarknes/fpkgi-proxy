import json

# Ler o arquivo atual com formato errado
with open('GAMES_format.json', 'r', encoding='utf-8-sig') as f:
    data = json.load(f)

# Converter para o formato correto (URL como chave)
novo_formato = {"DATA": {}}

for title_id, game_info in data.get("DATA", {}).items():
    # Procurar pela URL nos dados ou reconstruir
    # Se houver um campo 'url', usar como chave
    if 'url' in game_info:
        url = game_info['url']
    else:
        # Reconstruir a URL baseado no nome do jogo (aproximado)
        game_name = game_info.get('name', '').replace(' ', '%20')
        region_code = {'USA': 'us', 'EUR': 'eu', 'JAP': 'jp'}.get(game_info.get('region', ''), 'en')
        url = f"https://archive.org/download/ps4-fpkg-collection-english-{region_code}/{game_name}.pkg"
    
    novo_formato["DATA"][url] = game_info

# Salvar no formato correto
with open('GAMES_format.json', 'w', encoding='utf-8') as f:
    json.dump(novo_formato, f, ensure_ascii=False, indent=2)

print("Arquivo convertido com sucesso!")
print(f"Total de jogos: {len(novo_formato['DATA'])}")
