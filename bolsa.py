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
    except Exception as e:
        print(f"Error en Telegram: {e}")

def obtener_datos_mercado(ticker):
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1m&range=1d"
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, headers=headers, timeout=5) # Timeout corto para que no se congele
        if r.status_code != 200: return None, None, None
        
        data = r.json()['chart']['result'][0]
        precio_actual = data['meta']['regularMarketPrice']
        
        candles = data['indicators']['quote'][0]
        volumes = candles.get('volume', [])
        highs = candles.get('high', [])
        lows = candles.get('low', [])
        closes = candles.get('close', [])
        
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
    
    tickers = [
        "ADCT", "ADSE", "AGEN", "ASNS", "ALVO", "AMC", "AEMD", "APP", "AQST", "AMRE", 
        "ARRY", "ALOT", "ATRA", "ALTI", "BRKM", "BCRX", "BHG", "BLND", "BLLC", "CCO", 
        "CHRS", "CLNE", "CMPR", "CPS", "CLAR", "TRD", "RARE", "RNW", "RMNI", "CRTX", 
        "REIN", "RRGB", "SABR", "SATL", "STNE", "SLNC", "STEM", "STRO", "XERS", "ZIP"
    ]
    
    enviar_telegram("🚀 *SCANNER OPTIMIZADO CONECTADO*\nBuscando rupturas de VWAP con volumen...")
    
    precios_referencia = {}

    while True:
        for t in tickers:
            precio, vwap, vol_acumulado = obtener_datos_mercado(t)
            
            # Si es la primera vez que vemos el ticker, guardamos precio y saltamos
            if t not in precios_referencia:
                if precio: precios_referencia[t] = precio
                continue

            p_ref = precios_referencia.get(t)
            
            if precio and p_ref and vwap:
                cambio = ((precio - p_ref) / p_ref) * 100
                
                # --- FILTRO DE CALIDAD ---
                # 1. Sube más de 1.5% en este ciclo
                # 2. Está por ENCIMA del VWAP (Tendencia alcista)
                # 3. Volumen mínimo de 100,000 para evitar trampas
                if cambio > 1.5 and precio > vwap and vol_acumulado > 100000:
                    
                    msg = (f"🔥 *RUPTURA EN ${t}*\n"
                           f"Precio: ${precio:.3f}\n"
                           f"Salto: +{cambio:.2f}%\n"
                           f"Volumen: {vol_acumulado:,} 📈\n"
                           f"Señal: Confirmada sobre VWAP ✅")
                    
                    enviar_telegram(msg)
                    precios_referencia[t] = precio 
            
            time.sleep(1) # Pausa mínima entre tickers para no saturar a Yahoo
        
        print("Ciclo completado. Esperando 2 minutos para el siguiente escaneo...")
        time.sleep(120) # Escanea cada 2 minutos para detectar cambios reales
