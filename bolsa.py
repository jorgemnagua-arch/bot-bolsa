import requests
import time
import os
from flask import Flask
from threading import Thread

# --- PARCHE PARA RENDER ---
app = Flask('')

@app.route('/')
def home():
    return "Bot de Bolsa Activo"

def run():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()
# --------------------------

TOKEN = '8108194946:AAGKlV3oKLGf63zlEmyG-DJ9JuMghlTQRKk'
CHAT_ID = '8297764780'

def enviar_telegram(msj):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": CHAT_ID, "text": msj, "parse_mode": "Markdown"}, timeout=10)
    except Exception as e:
        print(f"Error Telegram: {e}")

def obtener_precio(ticker):
    try:
        # Usamos una API más directa para evitar bloqueos de Yahoo
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, headers=headers, timeout=10)
        data = r.json()
        precio = data['chart']['result'][0]['meta']['regularMarketPrice']
        return float(precio)
    except Exception as e:
        print(f"Error Ticker {ticker}: {e}")
        return None

if __name__ == "__main__":
    keep_alive()
    
    # Lista de tus tickers
    tickers = ["CCCC", "ABAT", "BAK", "CMPS", "FFIE", "KOSS"]
    
    # Mensaje de confirmación inmediata
    enviar_telegram("⚡ *BOT REINICIADO*\nProbando conexión con el mercado...")
    
    # Guardamos precios iniciales
    precios_iniciales = {}
    for t in tickers:
        p = obtener_precio(t)
        if p:
            precios_iniciales[t] = p
            print(f"Cargado {t}: {p}")
    
    while True:
        for t in tickers:
            precio_actual = obtener_precio(t)
            p_ini = precios_iniciales.get(t)
            
            if precio_actual and p_ini:
                cambio = ((precio_actual - p_ini) / p_ini) * 100
                
                # UMBRAL DE PRUEBA: 0.05%
                if abs(cambio) > 0.05: 
                    enviar_telegram(f"💹 *MOVIMIENTO DETECTADO\nTicker: *{t}**\nPrecio: ${precio_actual}\nVar: {cambio:.2f}%")
                    precios_iniciales[t] = precio_actual
            
        time.sleep(30) # Revisa cada 30 segundos
