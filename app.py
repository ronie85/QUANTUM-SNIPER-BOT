import streamlit as st
import yfinance as yf
import pandas as pd
import streamlit.components.v1 as components
from bot_brain import TradingBrain

st.set_page_config(page_title="Quantum Sniper Futures PRO+", layout="wide")
brain = TradingBrain()

# --- SIDEBAR NAVIGASI ---
st.sidebar.title("🚀 Quantum Sniper")
menu = st.sidebar.radio("Navigasi", ["🎯 Analisa Detail", "🔍 Scanner Top 10"])

if menu == "🎯 Analisa Detail":
    ticker = st.sidebar.text_input("Simbol (ex: BTC-USD / BBCA.JK)", "BTC-USD")
    tf = st.sidebar.selectbox("Timeframe", ["15m", "1h", "4h", "1d"], index=1)
    balance = st.sidebar.number_input("Modal Trading (USD/IDR)", value=1000)
    
    if st.sidebar.button("JALANKAN ANALISA"):
        raw_data = yf.download(ticker, period="250d", interval=tf)
        df = brain.process_data(raw_data)
        
        if not df.empty:
            res = brain.get_analysis(df, balance=balance)
            
            # --- PANEL UTAMA ---
            st.title(f"Quantum Dashboard: {ticker}")
            
            # Logika Warna Sinyal
            if "BUY" in res['signal']:
                st.success(f"### 🚀 SINYAL: {res['signal']} (Skor: {res['score']})")
            elif "SELL" in res['signal']:
                st.error(f"### 📉 SINYAL: {res['signal']} (Skor: {res['score']})")
            else:
                st.warning(f"### ⚖️ STATUS: {res['signal']} (Skor: {res['score']})")

            # Metrics Row
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("ENTRY PRICE", f"{res['curr']:,.2f}")
            c2.metric("LEVERAGE", f"{res['lev']}x")
            c3.metric("TAKE PROFIT", f"{res['tp']:,.2f}")
            c4.metric("STOP LOSS", f"{res['sl']:,.2f}")

            st.info(f"💡 **Saran Strategi:** Gunakan Leverage **{res['lev']}x** dengan margin **Isolated**. Pasang SL ketat di level POC Wall.")

            # --- TRADINGVIEW CHART ---
            st.subheader("📈 Live Chart (TradingView)")
            tv_symbol = ticker.replace("-", "") if "-" in ticker else ticker.replace(".JK", "")
            exchange = "IDX" if ".JK" in ticker else "BINANCE"
            tv_tf = "240" if tf == "4h" else "60" if tf == "1h" else "D" if tf == "1d" else "15"
            
            components.html(f"""
                <div style="height:600px; width:100%;">
                    <script src="https://s3.tradingview.com/tv.js"></script>
                    <script>
                    new TradingView.widget({{
                        "width": "100%", "height": 600, "symbol": "{exchange}:{tv_symbol}",
                        "interval": "{tv_tf}", "theme": "dark", "style": "1", "container_id": "tv_chart"
                    }});
                    </script>
                    <div id="tv_chart"></div>
                </div>
            """, height=620)

elif menu == "🔍 Scanner Top 10":
    st.title("Scanner Peluang Futures & Saham")
    mkt = st.selectbox("Pilih Market", ["Crypto", "Saham IDX"])
    assets = ["BTC-USD","ETH-USD","XRP-USD","SOL-USD","BNB-USD","ADA-USD","DOGE-USD","MATIC-USD","DOT-USD","LTC-USD"] if mkt == "Crypto" else ["BBCA.JK","BBRI.JK","TLKM.JK","ASII.JK","GOTO.JK","BMRI.JK","ADRO.JK","UNTR.JK","AMRT.JK","BBNI.JK"]
    
    if st.button("MULAI SCAN"):
        results = []
        prog = st.progress(0)
        for i, s in enumerate(assets):
            d = yf.download(s, period="100d", interval="1h", progress=False)
            df_s = brain.process_data(d)
            if not df_s.empty:
                r = brain.get_analysis(df_s)
                results.append({
                    "Simbol": s, 
                    "Signal": r['signal'], 
                    "Skor": r['score'], 
                    "Lev": f"{r['lev']}x",
                    "Harga": f"{r['curr']:,.2f}"
                })
            prog.progress((i + 1) / len(assets))
        
        # Tampilkan tabel yang diurutkan berdasarkan skor tertinggi
        df_res = pd.DataFrame(results).sort_values(by="Skor", ascending=False)
        st.table(df_res)
