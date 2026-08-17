# 📌 PROJECT STATE - SAAS-CRYPTO-BOT

## 1. Visão Geral
- **Projeto:** SAAS-CRYPTO-BOT (Robô Quantitativo de Criptomoedas)
- **Infraestrutura:** Script no PowerShell ativo para captura de VPS ARM Ampere na Oracle Cloud (Ashburn - US).

## 2. Arquivos Existentes
- `engine.py`: Motor principal de escaneamento e integração WebSocket.
- `dashboard.py`: Servidor Web do painel de controle.
- `auditar_binance.py`, `auditar_sistema.py`, `ver_posicoes.py`.
- `templates/`: Interface HTML (`index.html`, `monitoramento.html`).

## 3. Checklist de Sprints (FBQ v10.0 - PRD Finalizado)

### 🎯 Fase 1: Infraestrutura Base
- [x] Estrutura base e scripts auxiliares criados
- [x] Ambiente de desenvolvimento e extensões configuradas
- [x] Layout e template do painel finalizado
- [x] Integração com Binance Demo Mode configurada via endpoints oficiais da Binance

### 🎯 Fase 2: Parâmetros Operacionais 24/7
- [x] Configuração dos parâmetros FBQ 24/7 de alta frequência concluída
- [x] 60 operações diárias distribuídas em 10 pares
- [x] Alocação dinâmica de 4% por posição
- [x] Meta de ganho de 34% e proteção de perda de 17% com break-even cognitivo ativo

### 🎯 Fase 3: Motor Multi-Timeframe Avançado (IMPLEMENTADO v10.0)
- [x] Arquitetura multi-timeframe configurada (5m, 1h, 4h, 1d)
- [x] Análise de entrada em 5m com confirmação em 1h
- [x] Detecção de regime de mercado em 4h
- [x] Contexto macro em 1d

### 🎯 Fase 4: Dynamic Leverage & Adaptive Targets (IMPLEMENTADO v10.0)
- [x] Dynamic Leverage implementado (5x-50x baseado em regime de mercado)
- [x] 5 regimes de mercado mapeados: TRENDING_STRONG, TRENDING_MILD, CHOPPY_HIGH_VOL, CHOPPY_LOW_VOL, NEUTRAL
- [x] Adaptive Targets implementados (15%-85% conforme regime)
- [x] Ajuste de stop-loss dinâmico baseado em leverage e volatilidade
- [x] Cálculo de regime baseado em ADX, volatilidade relativa e volume

### 🎯 Fase 5: Real-Time UI Signals (IMPLEMENTADO v10.0)
- [x] Geração de sinais em tempo real para Black Luxo UI
- [x] Estrutura de payloads com regime, leverage, targets, checkpoints
- [x] Sistema de confiança de sinal (convergência % + boost de leverage)
- [x] Streaming de sinais para painel em tempo real

### 📋 Tarefas Restantes
- [ ] Configure Binance Demo Mode API Keys and Local Proxy Connection
- [ ] Teste integrado de live trading (simulado em Demo Mode)
- [ ] Otimização de parâmetros por histórico de backtest

## 4. Arquitetura Técnica FBQ v10.0 (Multi-Timeframe + Dynamic Leverage)

### 📊 Timeframes Operacionais
| Timeframe | Propósito | Função |
|-----------|----------|--------|
| **5m** | Entry Signals | `TIMEFRAME_ENTRY` - Sinais de entrada rápida |
| **1h** | Confirmation | `TIMEFRAME_CONFIRM` - Validação de confirmação |
| **4h** | Regime Detection | `TIMEFRAME_REGIME` - Detecção de regime de mercado |
| **1d** | Macro Context | `TIMEFRAME_MACRO` - Contexto macro trend |

### 🎚️ Regimes de Mercado & Leverage Dinâmico
```
TRENDING_STRONG:  ADX > 30 + Vol > 1.2x → Leverage: 35x-50x, Target: 60%-85%
TRENDING_MILD:    ADX > 25 + Vol > 1.0x → Leverage: 20x-35x, Target: 40%-60%
CHOPPY_HIGH_VOL:  ADX < 20 + Vol > 1.3x → Leverage: 5x-15x,  Target: 15%-30%
CHOPPY_LOW_VOL:   ADX < 20 + Vol < 0.8x → Leverage: 10x-20x, Target: 20%-40%
NEUTRAL:          Default State         → Leverage: 15x-25x, Target: 25%-45%
```

### 🔧 Funções Principais Implementadas
- `detectar_regime_mercado(df, ativo)` - Identifica regime baseado em ADX/volatilidade/volume
- `calcular_leverage_dinamico(regime, volatilidade_relativa)` - Calcula leverage adaptativo (5x-50x)
- `calcular_alvo_adaptativo(regime, preco_atual, direcao)` - Targets adaptativos (15%-85%)
- `atualizar_break_even_cognitivo()` - Ativa break-even em 60% do ganho esperado
- `gerar_sinal_ui_black_luxo()` - Estrutura JSON para Black Luxo UI em tempo real
- `carregar_multiframe_data()` - Async multi-timeframe data loading via WebSocket

### 📡 Real-Time UI Signal Payload (Black Luxo)
```json
{
  "ativo": "BTCUSDT",
  "timestamp": "2026-08-17T...",
  "regime_mercado": "TRENDING_STRONG",
  "leverage_dinamico": 45,
  "target_adaptativo": 12485.50,
  "entrada": 11500.00,
  "sl": 9775.00,
  "convergencia_pct": 100,
  "direcao_trade": "LONG",
  "status_geral": "PRONTO",
  "confianca_sinal": 89,
  "checkpoints_status": {
    "ema": "CHECK", "rsi": "CHECK", "macd": "CHECK", ...
  }
}
```

### ⚡ Fluxo de Operação 24/7
1. **Scan continuo** em 5m (2 segundos entre scans)
2. **Carregamento multi-frame** (5m, 1h, 4h, 1d) assincrono
3. **Detecção de regime** em 4h
4. **Cálculo de leverage** dinâmico baseado em regime + volatilidade
5. **Cálculo de alvo** adaptativo conforme regime
6. **Verificação de checkpoints** técnicos (EMA, RSI, MACD, CCI, ADX, etc.)
7. **Geração de sinal Black Luxo** para UI
8. **Execução** quando convergência = 100%
9. **Break-even cognitivo** ativado em 60% do ganho esperado