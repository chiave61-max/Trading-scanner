import yfinance as yf
import pandas as pd

watchlist = ["GC=F", "SI=F", "HG=F", "FTSEMIB.MI", "^GDAXI", "NVDA", "BTC-USD"]

def run_scanner():
    upper_cards, lower_cards = "", ""
    for ticker in watchlist:
        try:
            df = yf.download(ticker, period="20d", progress=False)
            df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
            vol_avg = df['Volume'].mean()
            o, i = df.iloc[-1], df.iloc[-2]
            is_buy = (o['Close'] > i['High']) and (o['Volume'] > vol_avg * 1.1)
            is_sell = (o['Close'] < i['Low']) and (o['Volume'] > vol_avg * 1.1)
            name = ticker.replace("=F","").replace("^","").replace(".MI","")
            card = f'<div style="background:{"#112a1d" if is_buy else "#2a1111" if is_sell else "#1c2128"}; border:1px solid {"#00ff7f" if is_buy else "#ff4b4b" if is_sell else "#333"}; border-radius:15px; padding:15px; margin-bottom:10px; display:flex; justify-content:space-between; align-items:center;"><div><b style="color:#ffd700;">{name}</b><br><small style="color:#666;">Vol: {o["Volume"]/vol_avg:.1f}x</small></div><div style="text-align:right;"><span style="color:{"#00ff7f" if is_buy else "#ff4b4b" if is_sell else "#555"}; font-weight:bold;">{"BUY 🟢" if is_buy else "SELL 🔴" if is_sell else "ATTESA ⚪"}</span><br><b style="color:white;">${o["Close"]:.2f}</b></div></div>'
            if is_buy or is_sell: upper_cards += card
            else: lower_cards += card
        except: continue

    html_final = f"""<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1.0"><meta http-equiv="refresh" content="300"></head><body style="background:#000; margin:0; padding:15px; font-family:sans-serif;"><h2 style="color:#ffd700; text-align:center;">🌍 POCKET SCANNER</h2>{upper_cards}<hr style="border:0; border-top:1px solid #222; margin:15px 0;">{lower_cards}<p style="text-align:center; color:#333; font-size:0.7em;">Auto-Update: {pd.Timestamp.now().strftime('%d/%m %H:%M:%S')}</p></body></html>"""
    
    with open("index.html", "w") as f:
        f.write(html_final)

if __name__ == "__main__":
    run_scanner()
