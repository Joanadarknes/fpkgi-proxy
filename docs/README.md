# Loja PS4

Site estatico para GitHub Pages.

Arquivos principais:

- `index.html`: interface da loja/catalogo.
- `GAMES_format.json`: catalogo carregado pela loja.
- `gamepad-controller.js`: suporte ao controle.
- `manifest.json` e `service-worker.js`: suporte PWA/cache.

Botao Baixar:

O botao aparece somente para itens marcados como `homebrew`, `freeware`, `demo`, `redistributable` ou `own` no campo `license` ou `type`. Nesses casos, a loja usa a URL da chave do item no `DATA` como link de baixar.

No GitHub, publique usando:

- Source: `Deploy from a branch`
- Branch: `main`
- Folder: `/docs`
