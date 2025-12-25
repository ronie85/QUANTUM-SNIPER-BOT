import streamlit as st
import yfinance as yf
import pandas as pd
import streamlit.components.v1 as components
from bot_brain import TradingBrain

st.set_page_config(page_title="Quantum Sniper PRO+", layout="wide")
brain = TradingBrain()

# --- SIDEBAR NAVIGASI ---
st.sidebar.title("🚀 Quantum Menu")
menu = st.sidebar.radio("Navigasi", ["🎯 Analisa Detail", "🔍 Scanner 10 Aset"])

if menu == "🎯 Analisa Detail":
    ticker = st.sidebar.text_input("Simbol", "XRP-USD")
    tf = st.sidebar.selectbox("Timeframe", ["15m", "1h", "4h", "1d"], index=1)
    
    if st.sidebar.button("JALANKAN ANALISA"):
        raw_data = yf.download(ticker, period="200d", interval=tf)
        df = brain.process_data(raw_data)
        
        if not df.empty:
            res = brain.get_analysis(df)
            
            # SIDEBAR STATS & NEWS
            st.sidebar.divider()
            st.sidebar.metric("Harga Live", f"{res['curr']:,.4f}")
            st.sidebar.metric("Volume", f"{res['vol_now']:,.0f}")
            st.sidebar.subheader("📰 Berita Terkini")
            try:
                news = yf.Ticker(ticker).news
                for n in news[:3]: st.sidebar.markdown(f"**[{n['title']}]({n['link']})**")
            except: st.sidebar.write("Berita tidak tersedia.")

            # MAIN DASHBOARD
            st.title(f"Analisa Quantum: {ticker}")
            if "BUY" in res['signal']: st.success(f"### 📢 SINYAL: {res['signal']} (Skor: {res['score']})")
            else: st.warning(f"### 📢 SINYAL: {res['signal']} (Skor: {res['score']})")

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("ENTRY", f"{res['curr']:,.4f}")
            c2.metric("TAKE PROFIT", f"{res['tp']:,.4f}")
            c3.metric("STOP LOSS", f"{res['sl']:,.4f}")
            c4.metric("VOL Z-SCORE", f"{res['zscore']:.2f}")

            # TRADINGVIEW CHART (DIPERBESAR)
            st.subheader("📈 Interactive TradingView Chart")
            tv_symbol = ticker.replace("-", "") if "-" in ticker else ticker.replace(".JK", "")
            if ".JK" in ticker: tv_symbol = f"IDX:{tv_symbol}"
            else: tv_symbol = f"BINANCE:{tv_symbol}T"
            
            tv_tf = "240" if tf == "4h" else "60" if tf == "1h" else "D" if tf == "1d" else "15"
            
            components.html(f"""
                <div style="height:600px;">
                    <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
                    <script type="text/javascript">
                    new TradingView.widget({{
                        "width": "100%", "height": 600, "symbol": "{tv_symbol}",
                        "interval": "{tv_tf}", "theme": "dark", "style": "1",
                        "locale": "en", "container_id": "tv_chart"
                    }});
                    </script>
                    <div id="tv_chart"></div>
                </div>
            """, height=620)

elif menu == "🔍 Scanner 10 Aset":
    st.title("Top 10 High Probability Scanner")
    mkt = st.selectbox("Pilih Market", ["Crypto", "Saham IDX"])
    assets = ["BTC-USD","ETH-USD","XRP-USD","SOL-USD","BNB-USD","ADA-USD","DOGE-USD","MATIC-USD","DOT-USD","LTC-USD"] if mkt == "Crypto" else ["BBCA.JK","BBRI.JK","TLKM.JK","ASII.JK","GOTO.JK","BMRI.JK","ADRO.JK","UNTR.JK","AMRT.JK","BBNI.JK"]
    
    if st.button("MULAI SCANNING"):
        results = []
        prog = st.progress(0)
        for i, s in enumerate(assets):
            d = yf.download(s, period="100d", interval="1h", progress=False)
            df_s = brain.process_data(d)
            if not df_s.empty:
                r = brain.get_analysis(df_s)
                results.append({"Simbol": s, "Signal": r['signal'], "Skor": r['score'], "Harga": f"{r['curr']:,.4f}", "Angle": f"{r['angle']:.1f}°"})
            prog.progress((i + 1) / len(assets))
        st.table(pd.DataFrame(results).sort_values(by="Skor", ascending=False))
