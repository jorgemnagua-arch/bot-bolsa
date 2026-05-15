import requests
import time
import os
from flask import Flask
from threading import Thread

# --- CONFIGURACIÓN DE RENDER (Para que no se apague) ---
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
    except Exception as e:
        print(f"Error enviando a Telegram: {e}")

def obtener_datos_mercado(ticker):
    try:
        # Hemos quitado el .US para que Yahoo reconozca mejor los tickers de NASDAQ/NYSE
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1m&range=1d"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
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
        
        # Filtramos valores nulos para el cálculo
        for i in range(len(volumes)):
            if volumes[i] and highs[i] and lows[i] and closes[i]:
                tp = (highs[i] + lows[i] + closes[i]) / 3
                suma_pv += tp * volumes[i]
                vol_total += volumes[i]
        
        vwap = suma_pv / vol_total if vol_total > 0 else None
        return precio_actual, vwap, vol_total
    except Exception as e:
        return None, None, None

if __name__ == "__main__":
    keep_alive()
    
    # LISTA DE TICKERS EXTRAÍDA DE TUS CAPTURAS DE XTB
    tickers = [
        "ADCT", "ADSE", "AGEN", "ASNS", "ALVO", "AMC", "AEMD", "APP", "AQST", "AMRE", 
        "ARRY", "ALOT", "ATRA", "ALTI", "BRKM", "BCRX", "BHG", "BLND", "BLLC", "CCO", 
        "CHRS", "CLNE", "CMPR", "CPS", "CLAR", "TRD", "RARE", "RNW", "RMNI", "CRTX", 
        "REIN", "RRGB", "SABR", "SATL", "STNE", "SLNC", "STEM", "STRO", "XERS", "ZIP"
    ]
    
    enviar_telegram("🚀 *RADAR XTB CONECTADO*\nEsperando movimientos en el mercado...")
    
    # Guardamos el precio de referencia al arrancar
    precios_referencia = {}
    for t in tickers:
        p, v, vol = obtener_datos_mercado(t)
        if p:
            precios_referencia[t] = p
    
    while True:
        for t in tickers:
            precio, vwap, vol_acumulado = obtener_datos_mercado(t)
            p_ref = precios_referencia.get(t)
            
            if precio and p_ref and vwap:
                cambio = ((precio - p_ref) / p_ref) * 100
                
                # --- FILTROS DE SEÑAL ---
                # 1. Variación mayor al 1.0% (lo bajé de 1.5% para que sea más sensible hoy)
                # 2. Volumen mayor a 20,000 acciones (lo bajé de 50k para captar más alertas)
                if abs(cambio) > 1.0 and vol_acumulado > 20000:
                    posicion_vwap = "🟢 ARRIBA" if precio > vwap else "🔴 ABAJO"
                    
                    msg = (f"💹 *MOVIMIENTO EN ${t}*\n"
                           f"Precio: ${precio:.3f}\n"
                           f"Variación: {cambio:.2f}%\n"
                           f"Volumen: {vol_acumulado:,} 📊\n"
                           f"VWAP: ${vwap:.3f} ({posicion_vwap})")
                    
                    enviar_telegram(msg)
                    # Actualizamos el precio de referencia para que no repita la misma alerta seguido
                    precios_referencia[t] = precio 
            
        time.sleep(60) # Revisa cada minuto
