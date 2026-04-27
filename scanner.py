import yfinance as yf
import pandas as pd
from datetime import datetime

# Lista asset: Futures (H24), Indici (Europei), Azioni (USA), Crypto (H24)
watchlist = ["GC=F", "SI=F", "HG=F", "FTSEMIB.MI", "^GDAXI", "NVDA", "BTC-USD"]

def run_scanner():
    upper_cards, lower_cards = "", ""
    now = datetime.now()
    
    for ticker in watchlist:
        try:
            df = yf.download(ticker, period="20d", progress=False)
            df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
            vol_avg = df['Volume'].mean()
            o, i = df.iloc[-1], df.iloc[-2]
            
            # Calcolo Segnali
            is_buy = (o['Close'] > i['High']) and (o['Volume'] > vol_avg * 1.1)
            is_sell = (o['Close'] < i['Low']) and (o['Volume'] > vol_avg * 1.1)
            
            # Calcolo Target e Stop (Target 2%, Stop sul minimo/massimo di ieri)
            target = o['Close'] * (1.02 if is_buy else 0.98)
            stop = i['Low'] if is_buy else i['High']
            
            name = ticker.replace("=F","").replace("^","").replace(".MI","")
            
            # Design della Card con Target e Stop
            status_color = "#00ff7f" if is_buy else "#ff4b4b" if is_sell else "#555"
            bg_color = "#112a1d" if is_buy else "#2a1111" if is_sell else "#1c2128"
            border_color = status_color if (is_buy or is_sell) else "#333"
            
            card = f"""
            <div style="background:{bg_color}; border:2px solid {border_color}; border-radius:15px; padding:15px; margin-bottom:12px; font-family:sans-serif;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                    <b style="color:#ffd700; font-size:1.2em;">{name}</b>
                    <b style="color:{status_color};">{"BUY 🟢" if is_buy else "SELL 🔴" if is_sell else "ATTESA ⚪"}</b>
                </div>
                <div style="display:grid; grid-template-columns: 1fr 1fr; gap:8px; font-size:0.9em; color:#ccc;">
                    <div>Prezzo: <b style="color:white;">{o['Close']:.2f}</b></div>
                    <div>Vol: <b style="color:white;">{o['Volume']/vol_avg:.1f}x</b></div>
                    <div style="color:#00ff7f;">Target: <b>{target:.2f}</b></div>
                    <div style="color:#ff4b4b;">Stop: <b>{stop:.2f}</b></div>
                </div>
            </div>
            """
            
            if is_buy or is_sell: upper_cards += card
            else: lower_cards += card
        except: continue

    html_final = f"""
    <!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="refresh" content="300"></head>
    <body style="background:#000; margin:0; padding:15px; color:white; font-family:sans-serif;">
        <h2 style="color:#ffd700; text-align:center;">🌍 POCKET SCANNER PRO</h2>
        <p style="text-align:center; color:#666; font-size:0.8em; margin-bottom:20px;">Dati sincronizzati (EU/USA/Crypto)</p>
        {upper_cards}
        <hr style="border:0; border-top:1px solid #333; margin:20px 0;">
        {lower_cards}
        <p style="text-align:center; color:#444; font-size:0.7em;">Ultimo Update: {now.strftime('%H:%M:%S')}</p>
    </body></html>"""
    
    with open("index.html", "w") as f:
        f.write(html_final)

if __name__ == "__main__":
    run_scanner()

