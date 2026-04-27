import yfinance as yf
import pandas as pd
from datetime import datetime

watchlist = [
    "GC=F", "SI=F", "CL=F", "EURUSD=X", "^GSPC", "FTSEMIB.MI", 
    "NVDA", "AAPL", "TSLA", "BTC-USD", "ETH-USD"
]

def calculate_rsi(data, window=14):
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def run_scanner():
    upper_cards, lower_cards = "", ""
    now = datetime.now()
    
    for ticker in watchlist:
        try:
            df = yf.download(ticker, period="30d", progress=False)
            df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
            
            # Calcolo Indicatori PRO
            vol_avg = df['Volume'].rolling(20).mean().iloc[-1]
            rsi = calculate_rsi(df['Close']).iloc[-1]
            o, i = df.iloc[-1], df.iloc[-2]
            
            # LOGICA ULTRA: Breakout + Volume 1.5x + Filtro RSI
            is_buy = (o['Close'] > i['High']) and (o['Volume'] > vol_avg * 1.5) and (rsi < 70)
            is_sell = (o['Close'] < i['Low']) and (o['Volume'] > vol_avg * 1.5) and (rsi > 30)
            
            target = o['Close'] * (1.02 if is_buy else 0.98)
            stop = df['Low'].rolling(3).min().iloc[-1] if is_buy else df['High'].rolling(3).max().iloc[-1]
            
            name = ticker.replace("=F","").replace("^","").replace(".MI","").replace("-USD","").replace("=X","")
            status = "BUY 🟢" if is_buy else "SELL 🔴" if is_sell else "ATTESA ⚪"
            
            # Grafica migliorata con indicatore RSI
            bg_color = "#112a1d" if is_buy else "#2a1111" if is_sell else "#1c2128"
            rsi_color = "#ffd700" if 30 < rsi < 70 else "#ff4b4b"
            
            card = f"""
            <div style="background:{bg_color}; border:1px solid #333; border-radius:12px; padding:12px; margin-bottom:10px; font-family:sans-serif;">
                <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
                    <b style="color:white; font-size:1.1em;">{name}</b>
                    <b style="color:{'#00ff7f' if is_buy else '#ff4b4b' if is_sell else '#aaa'};">{status}</b>
                </div>
                <div style="display:grid; grid-template-columns: 1fr 1fr; gap:5px; font-size:0.85em; color:#bbb;">
                    <div>Prezzo: <b style="color:white;">{o['Close']:.2f}</b></div>
                    <div>Vol: <b style="color:white;">{o['Volume']/vol_avg:.1f}x</b></div>
                    <div>RSI: <b style="color:{rsi_color};">{rsi:.1f}</b></div>
                    <div style="color:#00ff7f;">Tgt: {target:.2f}</div>
                </div>
            </div>
            """
            if is_buy or is_sell: upper_cards += card
            else: lower_cards += card
        except: continue

    html_final = f"""
    <!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="refresh" content="300"></head>
    <body style="background:#0a0a0a; padding:15px; color:white; font-family:sans-serif;">
        <h3 style="text-align:center; color:#ffd700;">💎 SCANNER ULTRA V2</h3>
        {upper_cards}
        <div style="text-align:center; color:#444; margin:15px 0; font-size:0.8em;">--- MONITORING ---</div>
        {lower_cards}
        <p style="text-align:center; color:#333; font-size:0.7em;">Update: {now.strftime('%H:%M:%S')}</p>
    </body></html>"""
    
    with open("index.html", "w") as f: f.write(html_final)

if __name__ == "__main__": run_scanner()



