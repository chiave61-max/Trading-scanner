import yfinance as yf
import pandas as pd
from datetime import datetime
import time

watchlist = [
    "GC=F", "SI=F", "CL=F", "EURUSD=X", "^GSPC", "FTSEMIB.MI", 
    "NVDA", "AAPL", "TSLA", "BTC-USD", "ETH-USD"
]

def calculate_rsi(data, window=14):
    delta = data.diff()
    # Usiamo la media mobile esponenziale per un RSI più reattivo
    gain = (delta.where(delta > 0, 0)).ewm(span=window, adjust=False).mean()
    loss = (-delta.where(delta < 0, 0)).ewm(span=window, adjust=False).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def run_scanner():
    upper_cards, lower_cards = "", ""
    now = datetime.now()
    
    for ticker in watchlist:
        try:
            # Scarichiamo dati a intervalli di 1h per precisione massima
            df = yf.download(ticker, period="5d", interval="1h", progress=False)
            if df.empty: continue
            df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
            
            vol_avg = df['Volume'].rolling(20).mean().iloc[-1]
            rsi_series = calculate_rsi(df['Close'])
            rsi = rsi_series.iloc[-1]
            o, i = df.iloc[-1], df.iloc[-2]
            
            vol_ratio = o['Volume'] / vol_avg if vol_avg > 0 else 0
            
            # LOGICA V3: Più sensibile ai volumi esplosivi
            is_buy = (o['Close'] > i['High']) and (vol_ratio > 1.3) and (rsi < 68)
            is_sell = (o['Close'] < i['Low']) and (vol_ratio > 1.3) and (rsi > 32)
            
            target = o['Close'] * (1.015 if is_buy else 0.985)
            name = ticker.replace("=F","").replace("^","").replace(".MI","").replace("-USD","").replace("=X","")
            status = "BUY 🟢" if is_buy else "SELL 🔴" if is_sell else "ATTESA ⚪"
            
            bg_color = "#112a1d" if is_buy else "#2a1111" if is_sell else "#1c2128"
            rsi_color = "#ffd700" if 30 < rsi < 70 else "#ff4b4b"
            
            card = f"""
            <div style="background:{bg_color}; border:1px solid #333; border-radius:12px; padding:12px; margin-bottom:10px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <b style="color:white; font-size:1.2em;">{name}</b>
                    <b style="color:{'#00ff7f' if is_buy else '#ff4b4b' if is_sell else '#aaa'};">{status}</b>
                </div>
                <div style="display:grid; grid-template-columns: 1fr 1fr; gap:8px; margin-top:8px; font-size:0.9em; color:#bbb;">
                    <div>Prezzo: <b style="color:white;">{o['Close']:.2f}</b></div>
                    <div>Vol: <b style="color:white;">{vol_ratio:.1f}x</b></div>
                    <div>RSI: <b style="color:{rsi_color};">{rsi:.1f}</b></div>
                    <div style="color:{'#00ff7f' if is_buy else '#ff4b4b'};">Tgt: {target:.2f}</div>
                </div>
            </div>
            """
            if is_buy or is_sell: upper_cards += card
            else: lower_cards += card
        except Exception as e:
            print(f"Errore su {ticker}: {e}")
            continue

    html_final = f"""
    <!DOCTYPE html><html><head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="refresh" content="60">
    <style>body{{background:#050505; color:white; font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;}}</style>
    </head>
    <body style="padding:15px;">
        <h3 style="text-align:center; color:#ffd700; margin-bottom:20px;">💎 SCANNER ULTRA V3</h3>
        {upper_cards if upper_cards else '<p style="text-align:center; color:#555;">Nessun segnale operativo</p>'}
        <div style="text-align:center; color:#444; margin:20px 0; font-size:0.8em; letter-spacing:2px;">--- MONITORING ---</div>
        {lower_cards}
        <p style="text-align:center; color:#ff4b4b; font-size:0.75em; margin-top:20px; font-weight:bold;">
            LIVE UPDATE: {now.strftime('%H:%M:%S')}
        </p>
    </body></html>"""
    
    with open("index.html", "w") as f: f.write(html_final)

if __name__ == "__main__":
    run_scanner()




