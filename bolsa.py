import requests
import time
import re
import os
from flask import Flask
from threading import Thread

# --- PARCHE PARA QUE RENDER NO SE APAGUE ---
app = Flask('')

@app.route('/')
def home():
    return "Bot de Bolsa Activo"

def run():
    # Render asigna el puerto automáticamente, esto lo lee
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()
# ------------------------------------------

TOKEN = '8108194946:AAGKlV3oKLGf63zlEmyG-DJ9JuMghlTQRKk'
CHAT_ID = '8297764780'

def enviar_telegram(msj):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": CHAT_ID, "text": msj, "parse_mode": "Markdown"}, timeout=5)
    except:
        pass

def obtener_precio_manual(ticker):
    try:
        url = f"https://finance.yahoo.com/quote/{ticker}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=5)
        match = re.search(f'data-symbol="{ticker}" [^>]*value="([\d\.]+)"', response.text)
        if match:
            return float(match.group(1))
        return None
    except:
        return None

if _name_ == "_main_":
    # Arrancamos la web falsa para Render
    keep_alive()
    
    tickers = ["CCCC", "ABAT", "BAK", "CMPS", "FFIE", "KOSS"]
    enviar_telegram("🚀 *BOT VIVO Y BLINDADO*\nEscaneando con puerto dinámico...")
    
    precios_iniciales = {t: obtener_precio_manual(t) for t in tickers}
    
    while True:
        for t in tickers:
            precio_actual = obtener_precio_manual(t)
            p_ini = precios_iniciales.get(t)
            
            if precio_actual and p_ini:
                cambio = ((precio_actual - p_ini) / p_ini) * 100
                if abs(cambio) > 1.5: 
                    enviar_telegram(f"🚀 *MOVIMIENTO: ${t}*\nPrecio: ${precio_actual}\nVar: {cambio:.2f}%")
                    precios_iniciales[t] = precio_actual
            
        time.sleep(60)
