# 📌 PROJECT STATE - SAAS-CRYPTO-BOT

## 1. Visão Geral
- **Projeto:** SAAS-CRYPTO-BOT (Robô Quantitativo de Criptomoedas)
- **Infraestrutura:** Script no PowerShell ativo para captura de VPS ARM Ampere na Oracle Cloud (Ashburn - US).

## 2. Arquivos Existentes
- `engine.py`: Motor principal de escaneamento e integração WebSocket.
- `dashboard.py`: Servidor Web do painel de controle.
- `auditar_binance.py`, `auditar_sistema.py`, `ver_posicoes.py`.
- `templates/`: Interface HTML (`index.html`, `monitoramento.html`).

## 3. Checklist de Sprints
- [x] Estrutura base e scripts auxiliares criados
- [x] Ambiente de desenvolvimento e extensoes configuradas
- [x] Layout e template do painel finalizado
- [x] Integração com Binance Demo Mode configurada via endpoints oficiais da Binance
- [ ] Configure Binance Demo Mode API Keys and Local Proxy Connection
- [ ] Mapeamento do WebSocket para cotações em RAM