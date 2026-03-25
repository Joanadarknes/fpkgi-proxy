# FPKGi Proxy Server

Servidor proxy para FPKGi que faz login no Archive.org automaticamente.

## Deploy no Render.com

1. Crie um repositório no GitHub com estes arquivos
2. Conecte ao Render.com
3. Configure as variáveis de ambiente:
   - `ARCHIVE_EMAIL`: seu email do Archive.org
   - `ARCHIVE_PASSWORD`: sua senha do Archive.org

## Endpoints

- `/` - Status do servidor
- `/GAMES.json` - Lista de jogos
- `/DLC.json` - Lista de DLCs
- `/HOMEBREW.json` - Lista de homebrew
- `/pkg/<url>` - Proxy para download de PKGs
