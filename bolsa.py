import requests
import time
import os
from flask import Flask
from threading import Thread

# --- CONFIGURACIÓN DE RENDER ---
app = Flask('')
@app.route('/')
def home(): return "Bot de Bolsa XTB Activo"

def run():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

# --- DATOS DE TELEGRAM ---
TOKEN = '8108194946:AAGKlV3oKLGf63zlEmyG-DJ9JuMghlTQRKk'
CHAT_ID = '8297764780'

def enviar_telegram(msj):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": CHAT_ID, "text": msj, "parse_mode": "Markdown"}, timeout=10)
    except: pass

def obtener_datos_mercado(ticker):
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}.US?interval=1m&range=1d"
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, headers=headers, timeout=10)
        data = r.json()['chart']['result'][0]
        
        precio_actual = data['meta']['regularMarketPrice']
        
        # --- CÁLCULO VWAP ---
        candles = data['indicators']['quote'][0]
        volumes = candles['volume']
        highs = candles['high']
        lows = candles['low']
        closes = candles['close']
        
        suma_pv = 0
        vol_total = 0
        
        for i in range(len(volumes)):
            if volumes[i] and highs[i] and lows[i] and closes[i]:
                tp = (highs[i] + lows[i] + closes[i]) / 3
                suma_pv += tp * volumes[i]
                vol_total += volumes[i]
        
        vwap = suma_pv / vol_total if vol_total > 0 else None
        return precio_actual, vwap, vol_total
    except:
        return None, None, None

if __name__ == "__main__":
    keep_alive()
    
    # LISTA EXTRAÍDA DE TUS CAPTURAS
    tickers = [
        "ADCT", "ADSE", "AGEN", "ASNS", "ALVO", "AMC", "AEMD", "APP", "AQST", "AMRE", 
        "ARRY", "ALOT", "ATRA", "ALTI", "BRKM", "BCRX", "BHG", "BLND", "BLLC", "CCO", 
        "CHRS", "CLNE", "CMPR", "CPS", "CLAR", "TRD", "RARE", "RNW", "RMNI", "CRTX", 
        "REIN", "RRGB", "SABR", "SATL", "STNE", "SLNC", "STEM", "STRO", "XERS", "ZIP"
    ]
    
    enviar_telegram("🚀 *RADAR XTB INICIADO*\nMonitoreando 40 Small Caps...")
    
    precios_iniciales = {}
    for t in tickers:
        p, v, vol = obtener_datos_mercado(t)
        if p: precios_iniciales[t] = p
    
    while True:
        for t in tickers:
            precio, vwap, vol_acumulado = obtener_datos_mercado(t)
            p_ini = precios_iniciales.get(t)
            
            if precio and p_ini and vwap and vol_acumulado:
                cambio = ((precio - p_ini) / p_ini) * 100
                
                # FILTRO: Cambio > 1.5% Y Volumen > 50,000 acciones
                if abs(cambio) > 1.5 and vol_acumulado > 50000:
                    posicion = "🟢 ARRIBA" if precio > vwap else "🔴 ABAJO"
                    msg = (f"💹 *ALERTA: ${t}*\n"
                           f"Precio: ${precio:.3f}\n"
                           f"Var: {cambio:.2f}%\n"
                           f"Vol: {vol_acumulado:,} 📊\n"
                           f"VWAP: ${vwap:.3f} ({posicion})")
                    
                    enviar_telegram(msg)
                    precios_iniciales[t] = precio # Actualizamos base tras alerta
            
        time.sleep(60) # Espera 1 minuto entre rondas
