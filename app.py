import streamlit as st
import yfinance as yf
import pandas as pd
import streamlit.components.v1 as components
from bot_brain import TradingBrain

st.set_page_config(page_title="Quantum Sniper PRO+", layout="wide")
brain = TradingBrain()

# Navigasi Sidebar
st.sidebar.title("🚀 Sniper Control")
menu = st.sidebar.radio("Navigasi", ["🎯 Analisa Detail", "🔍 Scanner 10 Aset"])

if menu == "🎯 Analisa Detail":
    ticker = st.sidebar.text_input("Simbol (ex: BBCA.JK / BTC-USD)", "BBCA.JK")
    tf = st.sidebar.selectbox("Timeframe", ["15m", "1h", "4h", "1d"], index=1)
    
    if st.sidebar.button("JALANKAN ANALISA"):
        raw_data = yf.download(ticker, period="250d", interval=tf)
        df = brain.process_data(raw_data)
        
        if not df.empty:
            res = brain.get_analysis(df)
            
            # SIDEBAR: HARGA, VOLUME, NEWS
            st.sidebar.divider()
            st.sidebar.metric("Harga Live", f"{res['curr']:,.2f}")
            st.sidebar.metric("Volume", f"{res['vol_now']:,.0f}")
            st.sidebar.subheader("📰 Berita Terkini")
            try:
                t_news = yf.Ticker(ticker).news
                for n in t_news[:3]: st.sidebar.markdown(f"**[{n['title']}]({n['link']})**")
            except: st.sidebar.write("Gagal memuat berita.")

            # DASHBOARD UTAMA
            st.title(f"Analisa: {ticker}")
            st.subheader(f"📢 SIGNAL: {res['signal']} (Score: {res['score']})")

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("ENTRY", f"{res['curr']:,.2f}")
            c2.metric("TAKE PROFIT", f"{res['tp']:,.2f}")
            c3.metric("STOP LOSS", f"{res['sl']:,.2f}")
            c4.metric("VOL Z-SCORE", f"{res['zscore']:.2f}")

            # MENAMPILKAN S&R DAN PYTHAGORAS KEMBALI
            st.info(f"🧱 POC Wall (S&R): {res['poc']:,.2f} | 📐 Sudut Pythagoras: {res['angle']:.2f}°")

            # TRADINGVIEW (FIX KECIL & SAHAM)
            st.subheader("📈 TradingView Chart")
            tv_symbol = ticker.replace("-", "") if "-" in ticker else ticker.replace(".JK", "")
            exchange = "IDX" if ".JK" in ticker else "BINANCE"
            tv_tf = "240" if tf == "4h" else "60" if tf == "1h" else "D" if tf == "1d" else "15"
            
            components.html(f"""
                <div id="tv_chart" style="height:600px;">
                    <script src="https://s3.tradingview.com/tv.js"></script>
                    <script>
                    new TradingView.widget({{
                        "width": "100%", "height": 600, "symbol": "{exchange}:{tv_symbol}",
                        "interval": "{tv_tf}", "theme": "dark", "style": "1",
                        "locale": "en", "container_id": "tv_chart"
                    }});
                    </script>
                </div>
            """, height=620)
        else: st.error("Data Saham/Crypto tidak ditemukan.")

elif menu == "🔍 Scanner 10 Aset":
    st.title("Scanner Saham & Crypto")
    mkt = st.selectbox("Pilih Market", ["Saham Indonesia (IDX)", "Crypto"])
    assets = ["BBCA.JK","BBRI.JK","TLKM.JK","ASII.JK","GOTO.JK","BMRI.JK","ADRO.JK","UNTR.JK","AMRT.JK","BBNI.JK"] if mkt == "Saham Indonesia (IDX)" else ["BTC-USD","ETH-USD","XRP-USD","SOL-USD","BNB-USD","ADA-USD","DOGE-USD","DOT-USD","MATIC-USD","LTC-USD"]
    
    if st.button("MULAI SCAN"):
        results = []
        prog = st.progress(0)
        for i, s in enumerate(assets):
            d = yf.download(s, period="100d", interval="1h", progress=False)
            df_s = brain.process_data(d)
            if not df_s.empty:
                r = brain.get_analysis(df_s)
                results.append({"Simbol": s, "Signal": r['signal'], "Skor": r['score'], "Harga": f"{r['curr']:,.2f}"})
            prog.progress((i + 1) / len(assets))
        st.table(pd.DataFrame(results).sort_values(by="Skor", ascending=False))
