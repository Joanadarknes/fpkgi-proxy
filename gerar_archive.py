import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import unquote
print("SCRIPT INICIADO")
BASE = "https://archive.org/download/ps4-fpkg-collection-english-{}"

# letras a-z
collections = [chr(i) for i in range(ord('a'), ord('z') + 1)]

games = {}

for letter in collections:
    url = BASE.format(letter)

    print(f"Processando coleção {letter.upper()}...")

    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()

        soup = BeautifulSoup(r.text, "html.parser")

        for link in soup.find_all("a"):
            href = link.get("href", "")

            if not href.lower().endswith(".pkg"):
                continue

            if href.startswith("/"):
                href = href[1:]

            full_url = f"{url}/{href}"

            filename = href.rsplit("/", 1)[-1]
            filename = unquote(filename)

            if filename.lower().endswith(".pkg"):
                filename = filename[:-4]

            games[full_url] = {
                "title_id": "",
                "region": "",
                "name": filename,
                "version": "01.00",
                "release": "",
                "size": 0,
                "min_fw": "9.00",
                "cover_url": ""
            }

        print(f"OK {letter.upper()}")

    except Exception as e:
        print(f"ERRO {letter.upper()}: {e}")

resultado = {
    "DATA": games
}

with open("games_format.json", "w", encoding="utf-8") as f:
    json.dump(resultado, f, ensure_ascii=False, indent=2)

print(f"\nTotal de jogos encontrados: {len(games)}")
print("Arquivo salvo: games_format.json")