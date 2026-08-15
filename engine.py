import os
import sys
import time
import asyncio
import smtplib
import requests
from datetime import datetime, timezone
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import pandas as pd
import numpy as np
from dotenv import load_dotenv

try:
    import aiohttp
except ImportError:  # pragma: no cover - optional runtime dependency for websocket proxying
    aiohttp = None

import ccxt
import ccxt.pro as ccxtpro
import ta
from ta.trend import EMAIndicator, MACD, CCIIndicator, ADXIndicator
from ta.volatility import AverageTrueRange
from ta.momentum import RSIIndicator

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# ==================================================================================
# 🛡️ MEMÓRIA CONTÁBIL E ESTADOS DE RAM (STATE-MACHINE CONTRA SPAM E DUPLICIDADE)
# ==================================================================================

estatisticas_diarias_ram = {
    "operacoes": 0,
    "wins": 0,
    "losses": 0,
    "break_evens": 0,
    "ultimo_dia_enviado": None
}

trades_ativos_ram = {}
trava_alertas_15m = {}
precos_tempo_real_ram = {}
cache_indicadores_moedas = {}
cache_macro_btc = {"tendencia": "ALTA", "adx": 20.0}
tendencia_btc = "ALTA"

# ==================================================================================
# ⚙️ CONFIGURAÇÕES DE BANCO DE DADOS (SUPABASE) E AMBIENTE
# ==================================================================================

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("⚠️ Falha Crítica: SUPABASE_URL ou SUPABASE_KEY ausentes no arquivo .env")

SUPABASE_URL_CLEAN = SUPABASE_URL.strip().rstrip('/')

HEADERS_SUPABASE = {
    "apikey": SUPABASE_KEY.strip(),
    "Authorization": f"Bearer {SUPABASE_KEY.strip()}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

TIMEFRAME_SINAL = '5m'
TIMEFRAME_MACRO = '30m'

ATIVOS = [
    'BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT', 'XRPUSDT', 
    'LINKUSDT', 'AVAXUSDT', 'ADAUSDT', 'NEARUSDT', 'RENDERUSDT'
]

# ==================================================================================
# 🔌 CONEXÕES BINANCE DEMO MODE (SEM ENDPOINTS TESTNET ANTIGOS)
# ==================================================================================

BINANCE_PROXY_URL = (
    os.getenv('BINANCE_PROXY_URL')
    or os.getenv('HTTPS_PROXY')
    or os.getenv('HTTP_PROXY')
    or os.getenv('ALL_PROXY')
    or ''
).strip()

BINANCE_DEMO_REST_URL = 'https://api.binance.com'
BINANCE_DEMO_WS_URL = 'wss://stream.binance.com:9443'
BINANCE_DEMO_FUTURES_WS_URL = 'wss://fstream.binance.com'


def resolve_binance_proxy():
    proxy = BINANCE_PROXY_URL or os.getenv('HTTPS_PROXY') or os.getenv('HTTP_PROXY') or os.getenv('ALL_PROXY')
    return proxy.strip() if isinstance(proxy, str) and proxy.strip() else None


def build_binance_demo_proxy_map():
    proxy = resolve_binance_proxy()
    return {'http': proxy, 'https': proxy} if proxy else {}


def build_binance_demo_session():
    session = requests.Session()
    session.trust_env = True
    proxy_map = build_binance_demo_proxy_map()
    if proxy_map:
        session.proxies.update(proxy_map)
    return session


async def build_binance_demo_aiohttp_session():
    if aiohttp is None:
        return None
    proxy = resolve_binance_proxy()
    timeout = aiohttp.ClientTimeout(total=20)
    session_kwargs = {
        'trust_env': True,
        'timeout': timeout,
        'connector': aiohttp.TCPConnector(ssl=False),
    }
    if proxy:
        session_kwargs['proxy'] = proxy
    return aiohttp.ClientSession(**session_kwargs)


def build_binance_demo_exchange(exchange_factory, api_key=None, secret=None, futures=True):
    proxy = resolve_binance_proxy()
    exchange_config = {
        'apiKey': api_key or os.getenv('BINANCE_API_KEY'),
        'secret': secret or os.getenv('BINANCE_API_SECRET'),
        'proxy': proxy,
        'enableRateLimit': True,
        'timeout': 10000,
        'urls': {
            'api': {
                'public': BINANCE_DEMO_REST_URL,
                'private': BINANCE_DEMO_REST_URL,
            },
            'ws': BINANCE_DEMO_WS_URL if not futures else BINANCE_DEMO_FUTURES_WS_URL,
        },
        'options': {
            'defaultType': 'future' if futures else 'spot',
            'adjustForTimeDifference': True,
            'testnet': False,
            'demo': True,
        },
    }
    return exchange_factory(exchange_config)


exchange_mestre = build_binance_demo_exchange(ccxt.binance, futures=True)
exchange_ws = build_binance_demo_exchange(ccxtpro.binance, futures=True)

# ==================================================================================
# 🛠️ FUNÇÕES AUXILIARES DE SUPORTE E BANCO DE DADOS
# ==================================================================================

def buscar_assinantes_ativos():
    try:
        url = f"{SUPABASE_URL_CLEAN}/rest/v1/assinantes?status=eq.ativo"
        res = requests.get(url, headers=HEADERS_SUPABASE, timeout=10)
        return res.json() if res.status_code < 400 else []
    except Exception:
        return []

def contar_posicoes_abertas_supabase(assinante_id):
    try:
        url = f"{SUPABASE_URL_CLEAN}/rest/v1/historico_trades?assinante_id=eq.{assinante_id}&status_trade=eq.ABERTO"
        res = requests.get(url, headers=HEADERS_SUPABASE, timeout=5).json()
        return len(res) if isinstance(res, list) else 0
    except Exception:
        return 0

def gravar_historico_trade(assinante_id, ativo, direcao, preco_entrada, sl, tp):
    try:
        url = f"{SUPABASE_URL_CLEAN}/rest/v1/historico_trades"
        payload = {
            "assinante_id": int(assinante_id), 
            "ativo": ativo, 
            "direcao": direcao, 
            "preco_entrada": float(preco_entrada), 
            "status_trade": "ABERTO",
            "resultado_usdt": 0.0
        }
        requests.post(url, json=payload, headers=HEADERS_SUPABASE, timeout=10)
    except Exception:
        pass

def atualizar_painel_realtime(payload):
    try:
        url = f"{SUPABASE_URL_CLEAN}/rest/v1/painel_realtime"
        headers = {
            **HEADERS_SUPABASE, 
            "Prefer": "resolution=merge-duplicates"
        }
        
        payload["updated_at"] = datetime.now(timezone.utc).isoformat()
        
        response = requests.post(url, json=payload, headers=headers, timeout=5)
        
        # Exibe o erro real do Supabase se o status não for sucesso (200, 201 ou 204)
        if response.status_code not in (200, 201, 204):
            print(f"[-] [SUPABASE HTTP {response.status_code}] {response.text}")
            
    except Exception as e:
        print(f"[-] Erro de conexão com Supabase: {e}")

def calcular_lote_blindado_2pct(saldo_usdt, preco_ent, atr):
    if saldo_usdt < 20.0 or preco_ent <= 0 or atr <= 0: 
        return 0.0
    risco_tolerado_usdt = saldo_usdt * 0.02
    distancia_sl_nominal = atr
    if distancia_sl_nominal <= 0: 
        return 0.0
    qnt_contratos = risco_tolerado_usdt / distancia_sl_nominal
    return round(qnt_contratos, 3)

def gerar_html_neon_template(titulo, subtitulo, cor_neon, paridade, direcao, vol, adx, entrada, tp, sl, nota_rodape, extras_usdt=""):
    return f"""
    <html>
    <body style="background-color:#000000; color:#f3f4f6; font-family:monospace; padding:20px;">
        <div style="max-width:500px; margin:0 auto; border:1px solid {cor_neon}; padding:24px; border-radius:16px; background-color:#050505; box-shadow:0 0 20px {cor_neon};">
            <h2 style="color:{cor_neon}; font-size:16px; margin:0 0 6px 0; text-transform:uppercase; letter-spacing:1px;">{titulo}</h2>
            <div style="background-color:{cor_neon}; color:#000000; font-weight:bold; font-size:11px; padding:6px 12px; border-radius:6px; margin-bottom:16px; text-transform:uppercase; display:inline-block;">{subtitulo}</div>
            <table style="width:100%; font-size:12px; border-collapse:collapse; color:#d1d5db;">
                <tr style="border-bottom:1px solid #111827;"><td style="padding:10px 0; color:#6b7280;">Paridade Técnica:</td><td style="padding:10px 0; text-align:right; font-weight:bold; color:#ffffff;">{paridade}</td></tr>
                <tr style="border-bottom:1px solid #111827;"><td style="padding:10px 0; color:#6b7280;">Vetor de Direção:</td><td style="padding:10px 0; text-align:right; font-weight:bold; color:{cor_neon};">{direcao}</td></tr>
                <tr style="border-bottom:1px solid #111827;"><td style="padding:10px 0; color:#6b7280;">Razão de Volume:</td><td style="padding:10px 0; text-align:right; font-weight:bold; color:#4ade80;">{vol}</td></tr>
                <tr style="border-bottom:1px solid #111827;"><td style="padding:10px 0; color:#6b7280;">Força ADX (Macro):</td><td style="padding:10px 0; text-align:right; font-weight:bold; color:#eab308;">{adx}</td></tr>
                <tr style="border-bottom:1px solid #111827;"><td style="padding:10px 0; color:#6b7280;">Preço Entrada Est.:</td><td style="padding:10px 0; text-align:right; font-weight:bold; color:#ffffff;">${entrada:.4f}</td></tr>
                {extras_usdt}
                <tr style="border-bottom:1px solid #111827;"><td style="padding:10px 0; color:#4ade80; font-weight:bold;">🎯 Target Profit (TP):</td><td style="padding:10px 0; text-align:right; font-weight:bold; color:#4ade80;">${tp:.4f} (+34.00% NET)</td></tr>
                <tr style="border-bottom:1px solid #111827;"><td style="padding:10px 0; color:#f87171; font-weight:bold;">🛡️ Stop Loss (SL):</td><td style="padding:10px 0; text-align:right; font-weight:bold; color:#f87171;">${sl:.4f} (-17.00% NET)</td></tr>
                <tr style="border-bottom:1px solid #111827;"><td style="padding:10px 0; color:#6b7280;">Modalidade Margem:</td><td style="padding:10px 0; text-align:right; color:#ffffff;">Binance Futures Demo Cross (20x)</td></tr>
            </table>
            <p style="font-size:9px; color:#4b5563; margin-top:16px; line-height:1.4; text-align:center;">{nota_rodape}</p>
        </div>
    </body>
    </html>
    """

def enviar_email_gratuito(destinatario, assunto, html_corpo):
    if not destinatario:
        return
    server_smtp = os.getenv("EMAIL_SMTP_SERVER", "smtp.gmail.com")
    port_smtp = int(os.getenv("EMAIL_SMTP_PORT", 587))
    remetente = os.getenv("EMAIL_REMETENTE")
    senha_app = os.getenv("EMAIL_SENHA_APP")
    if not remetente or not senha_app: 
        return
    try:
        msg = MIMEMultipart('alternative')
        msg['From'], msg['To'], msg['Subject'] = remetente, destinatario, assunto
        msg.attach(MIMEText(html_corpo, 'html', 'utf-8'))
        server = smtplib.SMTP(server_smtp, port_smtp)
        server.starttls()
        server.login(remetente, senha_app)
        server.sendmail(remetente, destinatario, msg.as_string())
        server.quit()
    except Exception:
        pass

# ==================================================================================
# 🚀 ROUTER DE ROTEAMENTO E EXECUÇÃO DE ORDENS VIA API
# ==================================================================================

def executar_lote_nas_apis(ativo, direcao, preco_ent, sl, tp, atr_atual):
    assinantes = buscar_assinantes_ativos()
    relatorio_adm = f"FBQ OPERADO: {ativo} | Tipo: {direcao}\n"
    
    cor_neon = "#22c55e" if direcao == "LONG" else "#ef4444"
    direcao_str = "🟢 COMPRA (LONG)" if direcao == "LONG" else "🔴 VENDA (SHORT)"
    ativo_limpo = ativo.strip()
    
    for cli in assinantes:
        status_api_binance = "Sincronizado"
        qnt_estimada = calcular_lote_blindado_2pct(1000.0, preco_ent, atr_atual)
        
        # 🛡️ GRAVAÇÃO IMEDIATA: Registra ordem pendente no Supabase
        try:
            url_hist = f"{SUPABASE_URL_CLEAN}/rest/v1/historico_trades"
            payload_hist = {
                "assinante_id": int(cli['id']), 
                "ativo": ativo_limpo, 
                "direcao": direcao, 
                "preco_entrada": float(preco_ent), 
                "status_trade": "ABERTO",
                "resultado_usdt": 0.0,
                "status_api": "Aguardando Resposta"
            }
            requests.post(url_hist, json=payload_hist, headers=HEADERS_SUPABASE, timeout=10)
        except Exception:
            pass

        try:
            if contar_posicoes_abertas_supabase(cli['id']) >= 6:
                status_api_binance = "Recusado (Limite Máximo de 6 Posições)"
                raise ValueError("Limite Excedido")

            cli_exchange = build_binance_demo_exchange(
                ccxt.binance,
                api_key=cli.get('binance_key'),
                secret=cli.get('binance_secret'),
                futures=True,
            )
            
            cli_exchange.set_leverage(20, ativo_limpo)
            saldo = cli_exchange.fetch_balance()['total']['USDT']
            qnt_estimada = calcular_lote_blindado_2pct(saldo, preco_ent, atr_atual)
            
            if qnt_estimada <= 0.0:
                status_api_binance = "Recusado (Saldo Insuficiente)"
                raise ValueError("Saldo Insuficiente")
            
            side_in, side_out = ('buy', 'sell') if direcao == "LONG" else ('sell', 'buy')
            
            # Execução de ordens
            cli_exchange.create_market_order(ativo_limpo, side_in, qnt_estimada)
            cli_exchange.create_order(ativo_limpo, 'STOP_MARKET', side_out, qnt_estimada, params={'stopPrice': sl})
            cli_exchange.create_order(ativo_limpo, 'TAKE_PROFIT_MARKET', side_out, qnt_estimada, params={'stopPrice': tp})
            
            status_api_binance = "Aceito (Sincronizado via API)"
            relatorio_adm += f" {cli.get('nome', 'Cliente')}: Sincronizado com Sucesso\n"
            
        except Exception as err_api:
            status_api_binance = f"Falha (API Rejeitada: {err_api})"
            relatorio_adm += f" {cli.get('nome', 'Desconhecido')}: Contingência Ativada ({err_api})\n"
            
        # Atualiza o status da API na tabela historico_trades
        try:
            url_up = f"{SUPABASE_URL_CLEAN}/rest/v1/historico_trades?assinante_id=eq.{cli['id']}&ativo=eq.{ativo_limpo}&status_trade=eq.ABERTO"
            requests.patch(url_up, json={"status_api": status_api_binance}, headers=HEADERS_SUPABASE, timeout=5)
        except Exception:
            pass

        # Trava posição em memória RAM
        trades_ativos_ram[ativo_limpo] = {
            "entrada": preco_ent, "tp": tp, "sl": sl, "sl_original": sl, "dir": direcao, 
            "qnt": qnt_estimada, "inicio": datetime.now(), "be_ativado": False
        }

        html_extras_100 = f"""
        <tr style="border-bottom:1px solid #111827;">
            <td style="padding:10px 0; color:#eab308; font-weight:bold;">Roteamento API:</td>
            <td style="padding:10px 0; text-align:right; font-weight:bold; color:#eab308; font-size:11px;">{status_api_binance}</td>
        </tr>
        """
        html_100 = gerar_html_neon_template(
            titulo="🚨 DISPARO EM EXECUÇÃO QUANTIC",
            subtitulo="CONVERGÊNCIA: 100% (Sinal Ativo)",
            cor_neon=cor_neon,
            paridade=ativo_limpo,
            direcao=direcao_str,
            vol="Atendido",
            adx="Forte (>20)",
            entrada=preco_ent,
            tp=tp,
            sl=sl,
            nota_rodape="Caso o status acuse rejeição da API, realize a entrada imediatamente pelo painel manual.",
            extras_usdt=html_extras_100
        )
        enviar_email_gratuito(cli.get('email_notificacao'), f"🚨 DISPARO EM EXECUÇÃO: {ativo_limpo} 20X", html_100)

    try:
        enviar_email_gratuito(os.getenv("EMAIL_REMETENTE"), f"Relatório Contingência: {ativo_limpo}", relatorio_adm)
    except Exception:
        pass

# ==================================================================================
# ⚡ INFRAESTRUTURA DE TEMPO REAL ASSÍNCRONA INTEGRADA (WEBSOCKETS)
# ==================================================================================

async def escutar_websockets_binance():
    print("[+] Conectando ao canal de WebSockets de Alta Velocidade da Binance Futures...")
    while True:
        try:
            stream = await exchange_ws.watch_tickers(ATIVOS)
            for ativo, dados_ticker in stream.items():
                if dados_ticker and 'last' in dados_ticker:
                    precos_tempo_real_ram[ativo] = float(dados_ticker['last'])
        except Exception:
            await asyncio.sleep(2)

async def escutar_candles_websockets(ativo):
    global cache_indicadores_moedas
    while True:
        try:
            candles_ws = await exchange_ws.watch_ohlcv(ativo, timeframe=TIMEFRAME_SINAL, limit=100)
            if candles_ws:
                df = pd.DataFrame(candles_ws, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                cache_indicadores_moedas[ativo] = df
        except Exception:
            await asyncio.sleep(2)

# ==================================================================================
# 📊 MOTOR DE VARREDURA QUÂNTICA E ANÁLISE TÉCNICA
# ==================================================================================

def escanear_mercado_cripto():
    global tendencia_btc
    try:
        btc_candles = exchange_mestre.fetch_ohlcv('BTC/USDT', timeframe=TIMEFRAME_SINAL, limit=50)
        df_btc = pd.DataFrame(btc_candles, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        ema_btc = EMAIndicator(close=df_btc['close'], window=50).ema_indicator().iloc[-1]
        preco_btc = df_btc['close'].iloc[-1]
        tendencia_btc = "ALTA" if preco_btc > ema_btc else "BAIXA"
    except Exception as e:
        print(f"[-] Erro ao calcular tendência do BTC: {e}")
        tendencia_btc = "ALTA"

    for ativo in ATIVOS:
        try:
            ativo_limpo = ativo.replace('/', '').strip()
            
            df_cache = cache_indicadores_moedas.get(ativo)
            if df_cache is None:
                try:
                    candles = exchange_mestre.fetch_ohlcv(ativo, timeframe=TIMEFRAME_SINAL, limit=100)
                    df_cache = pd.DataFrame(candles, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                    cache_indicadores_moedas[ativo] = df_cache
                    cache_indicadores_moedas[ativo_limpo] = df_cache
                except Exception as e:
                    print(f"[-] Erro ao carregar candles para {ativo}: {e}")
                    continue

            df = df_cache.copy()
            if len(df) < 50:
                continue

            # Adicione no final da função escanear_mercado_cripto(), fora do loop dos ativos:
            print(f"[+] Varredura concluída com sucesso às {datetime.now().strftime('%H:%M:%S')} | {len(ATIVOS)} ativos atualizados no Supabase.")

            # Atualização do último candle com preço WebSocket em tempo real
            preco_ws = precos_tempo_real_ram.get(ativo) or precos_tempo_real_ram.get(ativo_limpo)
            if preco_ws is not None:
                df.at[df.index[-1], 'close'] = preco_ws
                if preco_ws > df.at[df.index[-1], 'high']: 
                    df.at[df.index[-1], 'high'] = preco_ws
                if preco_ws < df.at[df.index[-1], 'low']: 
                    df.at[df.index[-1], 'low'] = preco_ws

            # Atualização do último candle com preço WebSocket
            preco_ws = precos_tempo_real_ram.get(ativo) or precos_tempo_real_ram.get(ativo_limpo)
            if preco_ws is not None:
                df.at[df.index[-1], 'close'] = preco_ws
                if preco_ws > df.at[df.index[-1], 'high']: 
                    df.at[df.index[-1], 'high'] = preco_ws
                if preco_ws < df.at[df.index[-1], 'low']: 
                    df.at[df.index[-1], 'low'] = preco_ws

            # ----------------------------------------------------------------------
            # 1. CÁLCULO DOS INDICADORES TÉCNICOS QUANTITATIVOS
            # ----------------------------------------------------------------------
            df['EMA_50'] = EMAIndicator(close=df['close'], window=50).ema_indicator()
            df['RSI_14'] = RSIIndicator(close=df['close'], window=14).rsi()
            macd = MACD(close=df['close'])
            df['MACD_LINE'] = macd.macd()
            df['MACD_SIGNAL'] = macd.macd_signal()
            df['CCI_20'] = CCIIndicator(high=df['high'], low=df['low'], close=df['close'], window=20).cci()
            df['ATR_14'] = AverageTrueRange(high=df['high'], low=df['low'], close=df['close'], window=14).average_true_range()
            df['AO'] = ta.momentum.awesome_oscillator(high=df['high'], low=df['low'])
            
            # ADX para Força da Tendência (Termômetros)
            adx_ind = ADXIndicator(high=df['high'], low=df['low'], close=df['close'], window=14)
            df['ADX_14'] = adx_ind.adx()

            # ----------------------------------------------------------------------
            # 2. CÁLCULO DINÂMICO DE VOLUME (RAZÃO DE VOLUME)
            # ----------------------------------------------------------------------
            vol_medio_20 = df['volume'].rolling(20).mean().iloc[-1]
            vol_atual = df['volume'].iloc[-1]
            volume_razao_calc = round(vol_atual / vol_medio_20, 2) if vol_medio_20 > 0 else 1.0

            # Leituras do último candle
            preco_atual = float(df['close'].iloc[-1])
            ema_val = float(df['EMA_50'].iloc[-1])
            rsi_val = float(df['RSI_14'].iloc[-1])
            macd_line = float(df['MACD_LINE'].iloc[-1])
            macd_sig = float(df['MACD_SIGNAL'].iloc[-1])
            ao_val = float(df['AO'].iloc[-1])
            cci_val = float(df['CCI_20'].iloc[-1])
            atr_val = float(df['ATR_14'].iloc[-1])
            adx_val = float(df['ADX_14'].iloc[-1])

            # Awesome Oscillator
            df['AO'] = ta.momentum.awesome_oscillator(high=df['high'], low=df['low'])

            preco_atual = float(df['close'].iloc[-1])
            ema_val = float(df['EMA_50'].iloc[-1])
            rsi_val = float(df['RSI_14'].iloc[-1])
            macd_line = float(df['MACD_LINE'].iloc[-1])
            macd_sig = float(df['MACD_SIGNAL'].iloc[-1])
            ao_val = float(df['AO'].iloc[-1])
            cci_val = float(df['CCI_20'].iloc[-1])
            atr_val = float(df['ATR_14'].iloc[-1])

            # ----------------------------------------------------------------------
            # 3. VALIDAÇÃO DOS CHECKPOINTS (INDICADORES)
            # ----------------------------------------------------------------------
            c_ema = "CHECK" if (tendencia_btc == "ALTA" and preco_atual > ema_val) or (tendencia_btc == "BAIXA" and preco_atual < ema_val) else "STANDBY"
            c_bb = "CHECK" if abs(preco_atual - ema_val) > (atr_val * 0.5) else "STANDBY"
            c_rsi = "CHECK" if (tendencia_btc == "ALTA" and rsi_val > 50) or (tendencia_btc == "BAIXA" and rsi_val < 50) else "STANDBY"
            c_macd = "CHECK" if (tendencia_btc == "ALTA" and macd_line > macd_sig) or (tendencia_btc == "BAIXA" and macd_line < macd_sig) else "STANDBY"
            c_ao = "CHECK" if (tendencia_btc == "ALTA" and ao_val > 0) or (tendencia_btc == "BAIXA" and ao_val < 0) else "STANDBY"
            c_cci = "CHECK" if (tendencia_btc == "ALTA" and cci_val > 0) or (tendencia_btc == "BAIXA" and cci_val < 0) else "STANDBY"

            checks = [c_ema, c_bb, c_rsi, c_macd, c_ao, c_cci]
            score_total = sum(1 for c in checks if c == "CHECK")
            
            percentual = 0
            if score_total >= 6: percentual = 100
            elif score_total >= 4: percentual = 75
            elif score_total >= 2: percentual = 50
            elif score_total >= 1: percentual = 25

            direcao_trade = "LONG" if tendencia_btc == "ALTA" else "SHORT"
            
            if direcao_trade == "LONG":
                tp = preco_atual + (atr_val * 2.0)
                sl = preco_atual - (atr_val * 1.0)
            else:
                tp = preco_atual - (atr_val * 2.0)
                sl = preco_atual + (atr_val * 1.0)

            status_txt = f"P: {preco_atual:.4f} | TP: {tp:.4f} | SL: {sl:.4f}"
            if ativo_limpo in trades_ativos_ram:
                status_txt = f"EM OPERAÇÃO ({trades_ativos_ram[ativo_limpo]['dir']}) | P: {preco_atual:.4f}"

            # ----------------------------------------------------------------------
            # 4. INTELIGÊNCIA DE VELAS / ANATOMIA (PRICE ACTION QUANTITATIVO)
            # ----------------------------------------------------------------------
            c_open, c_close = float(df['open'].iloc[-1]), float(df['close'].iloc[-1])
            c_high, c_low = float(df['high'].iloc[-1]), float(df['low'].iloc[-1])
            
            corpo_candle = max(abs(c_close - c_open), 0.00001)
            pavio_superior = c_high - max(c_close, c_open)
            pavio_inferior = min(c_close, c_open) - c_low
            
            # Tolerâncias ajustadas para detecção realística
            c_pinbar_alta = pavio_inferior >= (corpo_candle * 1.8) and pavio_superior <= (corpo_candle * 0.8)
            c_pinbar_baixa = pavio_superior >= (corpo_candle * 1.8) and pavio_inferior <= (corpo_candle * 0.8)
            c_pinbar = "CHECK" if (c_pinbar_alta or c_pinbar_baixa) else "STANDBY"
            
            prev_open, prev_close = float(df['open'].iloc[-2]), float(df['close'].iloc[-2])
            c_engolfo_alta = c_close > c_open and c_close > prev_open and c_open < prev_close
            c_engolfo_baixa = c_close < c_open and c_close < prev_open and c_open > prev_close
            c_engolfo = "CHECK" if (c_engolfo_alta or c_engolfo_baixa) else "STANDBY"
            
            c_inside = "CHECK" if (c_high <= float(df['high'].iloc[-2]) and c_low >= float(df['low'].iloc[-2])) else "STANDBY"
            
            diff_ob = abs(float(df['high'].iloc[-3]) - float(df['low'].iloc[-1]))
            c_orderblock = "CHECK" if diff_ob > (atr_val * 0.4) else "STANDBY"

            # ----------------------------------------------------------------------
            # 5. PAYLOAD COMPLETO (SINAIS + METRICAS NUMÉRICAS PARA MÉTRICAS DO PAINEL)
            # ----------------------------------------------------------------------
            payload_realtime = {
                "ativo": ativo_limpo,
                "tendencia_macro": f"MACRO {tendencia_btc}",
                "percentual": str(percentual),
                "score_total": score_total,
                "volume_razao": f"{volume_razao_calc:.2f}",  # <--- AGORA DINÂMICO
                "status_texto": status_txt,
                
                # Checkpoints de Status
                "c_ema": c_ema,
                "c_bb": c_bb,
                "c_rsi": c_rsi,
                "c_macd": c_macd,
                "c_ao": c_ao,
                "c_cci": c_cci,
                "c_pinbar": c_pinbar,
                "c_engolfo": c_engolfo,
                "c_inside": c_inside,
                "c_orderblock": c_orderblock,

                # Valores Numéricos Brutos (Alimentam Réguas, Termômetros e Telemetria)
                "preco_atual": round(preco_atual, 4),
                "rsi_val": round(rsi_val, 2),
                "cci_val": round(cci_val, 2),
                "ao_val": round(ao_val, 4),
                "atr_val": round(atr_val, 4),
                "adx_val": round(adx_val, 2),
                "macd_line": round(macd_line, 4),
                "macd_signal": round(macd_sig, 4),
                "tp": round(tp, 4),
                "sl": round(sl, 4)
            }

            atualizar_painel_realtime(payload_realtime)

            if percentual == 100 and ativo_limpo not in trades_ativos_ram:
                executar_lote_nas_apis(ativo_limpo, direcao_trade, preco_atual, sl, tp, atr_val)

        except Exception as e:
            print(f"[-] Erro ao processar ativo {ativo}: {e}")

# ==================================================================================
# 🔄 LOOP DE EXECUÇÃO ASSÍNCRONA E CICLO PRINCIPAL
# ==================================================================================

async def loop_varredura_continua():
    while True:
        try:
            escanear_mercado_cripto()
        except Exception as e:
            print(f"[-] Erro na varredura: {e}")
        await asyncio.sleep(5)

async def main():
    print("[+] Inicializando Motor Quântico FBQ v9.5 PRO...")
    tasks = [
        asyncio.create_task(escutar_websockets_binance()),
        asyncio.create_task(loop_varredura_continua())
    ]
    for ativo in ATIVOS:
        tasks.append(asyncio.create_task(escutar_candles_websockets(ativo)))
    
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[!] Motor encerrado pelo usuário.")
        sys.exit(0)