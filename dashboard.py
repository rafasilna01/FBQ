from flask import Flask, render_template, Response
import requests
import os
import json
import time
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# 📡 ROTA OPERACIONAL FIXA UNIFICADA DO SEU PROJETO PRIVADO (BATE DIRETO NO SCHEMA PURIFICADO)
SUPABASE_URL_CLEAN = "https://supabase.co"

# 🪙 CHAVE ANÔNIMA MESTRE EM STRING PURA (BLINDAGEM TOTAL ANTI-ERROS DE .ENV)
SUPABASE_KEY_FIXA = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFueW5vaHplc2dycXZlb2dmeGpiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODMwMTAzOTcsImV4cCI6MjA5ODU4NjM5N30.YuDUGxQkhbdxTPh2qIzrtafCassedfPPD2h-58pnfX0"

HEADERS_SUPABASE = {
    "apikey": SUPABASE_KEY_FIXA,
    "Authorization": f"Bearer {SUPABASE_KEY_FIXA}",
    "Content-Type": "application/json"
}

# 🔮 ITEM 2: MEMÓRIA RAM DE BACKUP LOCAL CONTRA QUEDAS DE CONEXÃO ADAPTADA À REALIDADE SEM BARRAS
cache_realtime_local = [
    {"ativo": "BTCUSDT", "tendencia_macro": "COMPRA (LONG)", "percentual": 0, "status_texto": "Inicializando Telemetria...", "score_total": 0, "volume_razao": 1.0, "c_ema": "X", "c_bb": "X", "c_rsi": "X", "c_macd": "X", "c_ao": "X", "c_cci": "X", "c_pinbar": "X", "c_engolfo": "X", "c_inside": "X", "c_orderblock": "X"},
    {"ativo": "ETHUSDT", "tendencia_macro": "COMPRA (LONG)", "percentual": 0, "status_texto": "Inicializando Telemetria...", "score_total": 0, "volume_razao": 1.0, "c_ema": "X", "c_bb": "X", "c_rsi": "X", "c_macd": "X", "c_ao": "X", "c_cci": "X", "c_pinbar": "X", "c_engolfo": "X", "c_inside": "X", "c_orderblock": "X"},
    {"ativo": "SOLUSDT", "tendencia_macro": "COMPRA (LONG)", "percentual": 0, "status_texto": "Inicializando Telemetria...", "score_total": 0, "volume_razao": 1.0, "c_ema": "X", "c_bb": "X", "c_rsi": "X", "c_macd": "X", "c_ao": "X", "c_cci": "X", "c_pinbar": "X", "c_engolfo": "X", "c_inside": "X", "c_orderblock": "X"},
    {"ativo": "BNBUSDT", "tendencia_macro": "COMPRA (LONG)", "percentual": 0, "status_texto": "Inicializando Telemetria...", "score_total": 0, "volume_razao": 1.0, "c_ema": "X", "c_bb": "X", "c_rsi": "X", "c_macd": "X", "c_ao": "X", "c_cci": "X", "c_pinbar": "X", "c_engolfo": "X", "c_inside": "X", "c_orderblock": "X"},
    {"ativo": "XRPUSDT", "tendencia_macro": "COMPRA (LONG)", "percentual": 0, "status_texto": "Inicializando Telemetria...", "score_total": 0, "volume_razao": 1.0, "c_ema": "X", "c_bb": "X", "c_rsi": "X", "c_macd": "X", "c_ao": "X", "c_cci": "X", "c_pinbar": "X", "c_engolfo": "X", "c_inside": "X", "c_orderblock": "X"},
    {"ativo": "LINKUSDT", "tendencia_macro": "COMPRA (LONG)", "percentual": 0, "status_texto": "Inicializando Telemetria...", "score_total": 0, "volume_razao": 1.0, "c_ema": "X", "c_bb": "X", "c_rsi": "X", "c_macd": "X", "c_ao": "X", "c_cci": "X", "c_pinbar": "X", "c_engolfo": "X", "c_inside": "X", "c_orderblock": "X"},
    {"ativo": "AVAXUSDT", "tendencia_macro": "COMPRA (LONG)", "percentual": 0, "status_texto": "Inicializando Telemetria...", "score_total": 0, "volume_razao": 1.0, "c_ema": "X", "c_bb": "X", "c_rsi": "X", "c_macd": "X", "c_ao": "X", "c_cci": "X", "c_pinbar": "X", "c_engolfo": "X", "c_inside": "X", "c_orderblock": "X"},
    {"ativo": "ADAUSDT", "tendencia_macro": "COMPRA (LONG)", "percentual": 0, "status_texto": "Inicializando Telemetria...", "score_total": 0, "volume_razao": 1.0, "c_ema": "X", "c_bb": "X", "c_rsi": "X", "c_macd": "X", "c_ao": "X", "c_cci": "X", "c_pinbar": "X", "c_engolfo": "X", "c_inside": "X", "c_orderblock": "X"},
    {"ativo": "NEARUSDT", "tendencia_macro": "COMPRA (LONG)", "percentual": 0, "status_texto": "Inicializando Telemetria...", "score_total": 0, "volume_razao": 1.0, "c_ema": "X", "c_bb": "X", "c_rsi": "X", "c_macd": "X", "c_ao": "X", "c_cci": "X", "c_pinbar": "X", "c_engolfo": "X", "c_inside": "X", "c_orderblock": "X"},
    {"ativo": "RENDERUSDT", "tendencia_macro": "COMPRA (LONG)", "percentual": 0, "status_texto": "Inicializando Telemetria...", "score_total": 0, "volume_razao": 1.0, "c_ema": "X", "c_bb": "X", "c_rsi": "X", "c_macd": "X", "c_ao": "X", "c_cci": "X", "c_pinbar": "X", "c_engolfo": "X", "c_inside": "X", "c_orderblock": "X"}
]

def extrair_dados_do_cliente(id_cliente):
    try:
        url_cli = f"{SUPABASE_URL_CLEAN}/rest/v1/assinantes"
        res_cli = requests.get(url_cli, headers=HEADERS_SUPABASE, timeout=10).json()
        
        cliente = None
        if isinstance(res_cli, list):
            for c in res_cli:
                if str(c.get('id')) == str(id_cliente):
                    cliente = c
                    break
        
        if not cliente:
            print(f"[-] Investidor ID {id_cliente} não localizado na memória.")
            return None, None
            
        trades_filtrados = []
        try:
            url_trades = f"{SUPABASE_URL_CLEAN}/rest/v1/historico_trades"
            res_trades = requests.get(url_trades, headers=HEADERS_SUPABASE, timeout=10).json()
            
            if isinstance(res_trades, list):
                trades_filtrados = [t for t in res_trades if str(t.get('assinante_id')) == str(id_cliente)]
                trades_filtrados.sort(key=lambda x: x.get('id', 0), reverse=True)
        except Exception as e_trades:
            print(f"[!] Histórico de trades vazio ou em standby na nuvem: {e_trades}")
            trades_filtrados = []
            
        return cliente, trades_filtrados
    except Exception as e:
        print(f"[-] Erro crítico ao carregar dados do painel: {e}")
        return None, None

def buscar_dados_monitoramento():
    try:
        url = f"{SUPABASE_URL_CLEAN}/rest/v1/painel_realtime"
        res = requests.get(url, headers=HEADERS_SUPABASE, timeout=5)
        
        if res.status_code >= 400 or not res.text.strip():
            return obter_dados_fallback()
            
        dados = res.json()
        if isinstance(dados, list) and len(dados) > 0:
            dados.sort(key=lambda x: x.get('ativo', ''))
            return dados
        return obter_dados_fallback()
    except Exception as e:
        print(f"[-] Erro na rota de dados: {e}")
        return obter_dados_fallback()

# 🔮 ITEM 1: SISTEMA DE CONTINGÊNCIA CORRIGIDO NO PADRÃO DIRETO DA BINANCE (SEM BARRAS)
def obter_dados_fallback():
    moedas = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT', 'XRPUSDT', 'LINKUSDT', 'AVAXUSDT', 'ADAUSDT', 'NEARUSDT', 'RENDERUSDT']
    return [{
        "ativo": m, 
        "tendencia_macro": "ALTA", 
        "c_ema": "X", "c_bb": "X", "c_rsi": "X", "c_macd": "X", "c_ao": "X", "c_cci": "X",
        "c_pinbar": "X", "c_engolfo": "X", "c_inside": "X", "c_orderblock": "X",
        "volume_razao": 1.0, 
        "score_total": 0, 
        "percentual": 0, 
        "status_texto": "Inicializando telemetria em tempo real..."
    } for m in moedas]

@app.route('/dashboard/<int:id_cliente>')
def index(id_cliente):
    cliente_lista, trades = extrair_dados_do_cliente(id_cliente)
    if not cliente_lista: 
        return "⚠️ Erro: Investidor não localizado na nuvem."
        
    cliente = cliente_lista
    lucro_liquido = cliente.get('lucro_liquido_atual', 0.0)
    
    banca_inicial = 200.00
    mensalidade = float(os.getenv('MENSALIDADE_FIXA', 49.90))
    nome_plano = "Bronze (Risco Ajustado Pro)"
        
    taxa_performance = lucro_liquido * 0.10 if lucro_liquido > 0 else 0.0
    total_fatura = mensalidade + taxa_performance

    return render_template(
        'index.html', 
        nome=cliente.get('nome', 'Investidor'), 
        plano=nome_plano, 
        banca_inicial=banca_inicial, 
        lucro=lucro_liquido, 
        taxa_perf=taxa_performance, 
        mensalidade=mensalidade, 
        total=total_fatura, 
        trades=trades if trades else [],
        id_cliente=id_cliente
    )

@app.route('/monitoramento')
def monitoramento_page():
    dados = buscar_dados_monitoramento()
    return render_template('monitoramento.html', dados=dados)

# 🔮 ITEM 3: UNIFICAÇÃO DAS CHAVES DE TRANSMISSÃO EM MEMÓRIA RAM (MATA BLOQUEIOS DE REDE)
def puxar_dados_seguros_supabase():
    global cache_realtime_local
    try:
        url = f"{SUPABASE_URL_CLEAN}/rest/v1/painel_realtime?select=*"
        res = requests.get(url, headers=HEADERS_SUPABASE, timeout=2)
        if res.status_code < 400:
            dados_novos = res.json()
            if dados_novos and isinstance(dados_novos, list) and len(dados_novos) > 0:
                # Ordena os ativos para manter a grade alinhada no front-end
                dados_novos.sort(key=lambda x: x.get('ativo', ''))
                cache_realtime_local = dados_novos
                return dados_novos
    except Exception as e:
        print(f"[⚠️ ALERTA REDE] Falha na ponte de sincronismo: {e}")
    return cache_realtime_local

import json
import time
from flask import Response

@app.route('/stream-monitoramento')
def stream_monitoramento():
    def evento_perpetuo():
        while True:
            try:
                dados = puxar_dados_seguros_supabase()
                payload = json.dumps(dados)
                yield f"data: {payload}\n\n"
            except Exception as e:
                # Evita que uma oscilação temporária de rede no Supabase derrube o loop
                payload_erro = json.dumps({"status": "erro_conexao", "detalhe": str(e)})
                yield f"data: {payload_erro}\n\n"
            
            time.sleep(2)

    # Headers anti-buffering essenciais para SSE ( Server-Sent Events )
    headers = {
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no"
    }

    return Response(evento_perpetuo(), mimetype="text/event-stream", headers=headers)

if __name__ == "__main__":
    print("🌐 Servidor Web do FuturesBot Quantic Inicializado com Sucesso.")
    app.run(debug=True, port=5000, host="0.0.0.0")