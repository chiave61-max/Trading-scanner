import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import time

# 1. Configurazione Pagina (Titolo che vedi nella scheda del browser)
st.set_page_config(page_title="Scanner Ultra V4", layout="centered")

# 2. Design Cattivo (Stile CSS personalizzato)
st.markdown("""
    <style>
    .stApp {background-color: #050505;}
    .card {
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 10px;
        border: 1px solid #333;
        font-family: sans-serif;
    }
    .buy {background-color: #112a1d; border-left: 5px solid #00ff7f;}
    .sell {background-color: #2a1111; border-left: 5px solid #ff4b4b;}
    .wait {background-color: #1c2128; border-left: 5px solid #444;}
    .label {color: #888; font-size: 0.8em; text-transform: uppercase;}
    .value {color: white; font-weight: bold; font-size: 1.1em;}
    </style>
    """, unsafe_allow_html=True)

watchlist = [
    "GC=F", "SI=F", "CL=F", "EURUSD=X", "^GSPC", "FTSEMIB.MI", 
    "NVDA", "AAPL", "TSLA", "BTC-USD", "ETH-USD"
]

def get_data():
    results = []
    for ticker in watchlist:
        try:
            # Scarico dati freschi (periodo breve per massima velocità)
            df = yf.download(ticker, period="5d", interval="1h", progress=False)
            if df.empty: continue
            df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
            
            # Calcolo RSI Reattivo
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).ewm(span=14, adjust=False).mean()
            loss = (-delta.where(delta < 0, 0)).ewm(span=14, adjust=False).mean()
            rsi = 100 - (100 / (1 + (gain/loss))).iloc[-1]
            
            # Volume e Prezzo
            vol_avg = df['Volume'].rolling(20).mean().iloc[-1]
            o, i = df.iloc[-1], df.iloc[-2]
            vol_ratio = o['Volume'] / vol_avg if vol_avg > 0 else 0
            
            # LOGICA V4: Breakout + Volume 1.3x + Filtro RSI
            is_buy = (o['Close'] > i['High']) and (vol_ratio > 1.3) and (rsi < 68)
            is_sell = (o['Close'] < i['Low']) and (vol_ratio > 1.3) and (rsi > 32)
            
            name = ticker.replace("=F","").replace("^","").replace(".MI","").replace("-USD","").replace("=X","")
            
            results.append({
                "name": name,
                "price": o['Close'],
                "vol": vol_ratio,
                "rsi": rsi,
                "status": "BUY 🟢" if is_buy else "SELL 🔴" if is_sell else "ATTESA ⚪",
                "class": "buy" if is_buy else "sell" if is_sell else "wait"
            })
        except: continue
    return results

# INTERFACCIA STREAMLIT
st.markdown("<h2 style='text-align: center; color: #ffd700; margin-bottom:0;'>💎 SCANNER ULTRA V4</h2>", unsafe_allow_html=True)
now = datetime.now().strftime("%H:%M:%S")
st.markdown(f"<p style='text-align: center; color: #ff4b4b; font-size: 0.9em;'>LIVE UPDATE: {now}</p>", unsafe_allow_html=True)

# Recupero i dati live
data = get_data()

# Divido tra Segnali Operativi e Monitoring
operativi = [d for d in data if "ATTESA" not in d['status']]
monitoring = [d for d in data if "ATTESA" in d['status']]

# Mostro prima i BUY/SELL
for d in operativi:
    st.markdown(f"""
        <div class="card {d['class']}">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <b style="color:white; font-size:1.3em;">{d['name']}</b>
                <b style="color:{'#00ff7f' if 'BUY' in d['status'] else '#ff4b4b'}; font-size:1.1em;">{d['status']}</b>
            </div>
            <div style="display:grid; grid-template-columns: 1fr 1fr 1fr; gap:10px; margin-top:10px;">
                <div><div class="label">Prezzo</div><div class="value">{d['price']:.2f}</div></div>
                <div><div class="label">Vol Ratio</div><div class="value">{d['vol']:.1f}x</div></div>
                <div><div class="label">RSI</div><div class="value">{d['rsi']:.1f}</div></div>
            </div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<hr style='border-color:#222;'>", unsafe_allow_html=True)

# Mostro gli altri in lista
for d in monitoring:
    st.markdown(f"""
        <div class="card wait">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <b style="color:white;">{d['name']}</b>
                <b style="color:#888;">{d['status']}</b>
            </div>
            <div style="display:grid; grid-template-columns: 1fr 1fr 1fr; gap:10px; margin-top:10px;">
                <div><div class="label">Prezzo</div><div class="value" style="font-size:0.9em;">{d['price']:.2f}</div></div>
                <div><div class="label">Vol</div><div class="value" style="font-size:0.9em;">{d['vol']:.1f}x</div></div>
                <div><div class="label">RSI</div><div class="value" style="font-size:0.9em;">{d['rsi']:.1f}</div></div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# AUTO-REFRESH: Ricarica la pagina ogni 30 secondi
time.sleep(30)
st.rerun()
