import requests
import time
import re

# --- CONFIGURACIÓN ---
TOKEN = '8108194946:AAGKlV3oKLGf63zlEmyG-DJ9JuMghlTQRKk'
CHAT_ID = '8297764780'

def enviar_telegram(msj):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": CHAT_ID, "text": msj, "parse_mode": "Markdown"}, timeout=5)
    except: pass

def obtener_precio_manual(ticker):
    """Extrae el precio raspando Yahoo Finance directamente."""
    try:
        url = f"https://finance.yahoo.com/quote/{ticker}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=5)
        
        # Buscamos el precio en el HTML de la página
        match = re.search(f'data-symbol="{ticker}" [^>]*value="([\d\.]+)"', response.text)
        if match:
            return float(match.group(1))
        return None
    except:
        return None

if __name__ == "__main__":
    tickers = ["CCCC", "ABAT", "BAK", "CMPS", "FFIE", "KOSS"]
    enviar_telegram("🚀 *BOT INICIADO EN RENDER*\nEscaneando mercado...")
    
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
            
        time.sleep(60) # Espera 1 minuto para no saturar
