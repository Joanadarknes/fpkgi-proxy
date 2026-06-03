# 🎮 PS4 Games Database - Progressive Web App

Protótipo de loja estilo console que consome metadados públicos de jogos PS4.

## 🌟 Features

- **17,065+ Jogos PS4** - Base de dados completa do dlpsgame.com
- **UI Otimizada para PS4** - 1920x1080, design estilo PlayStation
- **Suporte a Controle** - DualShock 4 totalmente funcional
- **Funciona Offline** - Service Worker para cache local
- **Busca em Tempo Real** - Encontre jogos instantaneamente

## 🚀 Como Usar no PS4

### Passo 1: Abrir o Browser do PS4
1. No menu principal do PS4, vá em **Biblioteca**
2. Selecione **Internet Browser**

### Passo 2: Acessar a Loja
Digite a URL:
```
https://huggingfacer04.github.io/ps4-games-database/ps4-pwa-optimized.html
```

### Passo 3: Adicionar aos Favoritos
1. Pressione **OPTIONS** no controle
2. Selecione **Adicionar aos Favoritos**
3. Acesse rapidamente sempre que quiser

## 🎮 Controles do DualShock 4

| Botão | Função |
|-------|--------|
| **D-Pad** | Navegar entre jogos |
| **Analógico Esquerdo** | Scroll suave |
| **X** | Selecionar/Confirmar |
| **○** | Voltar ao topo |
| **△** | Abrir busca |
| **L1/R1** | Página anterior/próxima |

## 📁 Estrutura do Projeto

```
LojaPS4/
├── ps4-pwa-optimized.html    # App principal (PWA)
├── service-worker.js         # Cache offline
├── gamepad-controller.js     # Suporte a controle
├── manifest.json             # Configuração PWA
├── ps4_games_database.json   # Base de dados de jogos
└── README.md                 # Este arquivo
```

## 🔧 Rodar Localmente

### Opção 1: Servidor Python
```powershell
cd c:\Users\Joana\Desktop\LojaPS4
python -m http.server 8000
```
Acesse: `http://localhost:8000/ps4-pwa-optimized.html`

### Opção 2: Live Server (VS Code)
1. Instale a extensão "Live Server"
2. Clique direito em `ps4-pwa-optimized.html`
3. Selecione "Open with Live Server"

## ⚠️ Aviso Legal

Este projeto é apenas para fins educacionais. Exibe metadados públicos (títulos, capas, descrições) de jogos. Não hospedamos arquivos de jogos.

---

**Fontes:** dlpsgame.com | **Plataforma:** PS4 Browser (WebKit)
