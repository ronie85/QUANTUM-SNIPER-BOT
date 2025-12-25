import streamlit as st
import yfinance as yf
import pandas as pd
import streamlit.components.v1 as components
from bot_brain import TradingBrain

st.set_page_config(page_title="Quantum Sniper PRO+", layout="wide", page_icon="🎯")
brain = TradingBrain()

# --- SIDEBAR MENU ---
st.sidebar.title("🚀 Quantum Sniper Menu")
menu = st.sidebar.radio("Navigasi", ["🎯 Analisa Detail", "🔍 Scanner 10 Aset"])
ticker = st.sidebar.text_input("Simbol (ex: BTC-USD / BBCA.JK)", "BTC-USD")
tf = st.sidebar.selectbox("Timeframe", ["1h", "1d", "15m"], index=0)

st.sidebar.divider()

if st.sidebar.button("JALANKAN ANALISA"):
    with st.spinner('Sedang menghitung algoritma...'):
        data = yf.download(ticker, period="60d", interval=tf)
        df = brain.process_data(data)
        
        if not df.empty:
            res = brain.get_analysis(df)
            
            # --- HARGA LIVE & VOLUME (DI SIDEBAR) ---
            st.sidebar.subheader("📊 Market Status")
            st.sidebar.metric("Harga Live", f"{res['curr']:,.2f}")
            st.sidebar.metric("Volume Pasar", f"{res['vol_now']:,.0f}")
            
            # --- NEWS (BERITA CRYPTO/SAHAM) ---
            st.sidebar.subheader("📰 Breaking News")
            try:
                ticker_obj = yf.Ticker(ticker)
                for news in ticker_obj.news[:3]:
                    st.sidebar.markdown(f"**[{news['title']}]({news['link']})**")
                    st.sidebar.caption(f"Source: {news['publisher']}")
            except:
                st.sidebar.write("News tidak tersedia.")

            # --- DASHBOARD UTAMA ---
            st.title(f"🎯 Analisa Quantum: {ticker}")
            
            # Matrik Utama
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("ENTRY", f"{res['curr']:,.2f}")
            m2.metric("TAKE PROFIT", f"{res['tp']:,.2f}")
            m3.metric("STOP LOSS", f"{res['sl']:,.2f}")
            m4.metric("VOL Z-SCORE", f"{res['zscore']:.2f}")

            st.info(f"🧱 POC Wall (S&R): {res['poc']:,.2f} | 📐 Sudut Pythagoras: {res['angle']:.2f}°")

            # --- TRADINGVIEW LIVE CHART ---
            st.subheader("📈 Interactive TradingView Chart")
            
            # Konversi ticker ke format TradingView
            if ".JK" in ticker:
                tv_symbol = f"IDX:{ticker.replace('.JK', '')}"
            elif "-USD" in ticker:
                tv_symbol = f"BINANCE:{ticker.replace('-USD', 'USDT')}"
            else:
                tv_symbol = ticker

            tv_widget = f"""
            <div class="tradingview-widget-container">
              <div id="tradingview_widget"></div>
              <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
              <script type="text/javascript">
              new TradingView.widget({{
                "width": "100%",
                "height": 500,
                "symbol": "{tv_symbol}",
                "interval": "60",
                "timezone": "Etc/UTC",
                "theme": "dark",
                "style": "1",
                "locale": "en",
                "toolbar_bg": "#f1f3f6",
                "enable_publishing": false,
                "hide_side_toolbar": false,
                "allow_symbol_change": true,
                "container_id": "tradingview_widget"
              }});
              </script>
            </div>
            """
            components.html(tv_widget, height=520)

            if res['score'] >= 80:
                st.success("🚀 **SINYAL: STRONG BUY.** Konfluensi HMM, Pythagoras, dan Volume tercapai!")
        else:
            st.error("Data tidak mencukupi. Coba ganti ticker atau timeframe.")
