import streamlit as st
import yfinance as yf
import pandas as pd
import streamlit.components.v1 as components
from bot_brain import TradingBrain

st.set_page_config(page_title="Quantum Sniper PRO+", layout="wide")
brain = TradingBrain()

# SIDEBAR LENGKAP
st.sidebar.title("🚀 Quantum Menu")
menu = st.sidebar.radio("Navigasi", ["🎯 Analisa Detail", "🔍 Scanner 10 Aset"])
ticker = st.sidebar.text_input("Simbol", "BTC-USD")
tf = st.sidebar.selectbox("Timeframe", ["1h", "1d", "15m"])

# --- TAMBAHAN MENU DI BAWAH TIMEFRAME ---
st.sidebar.divider()
if st.sidebar.button("JALANKAN ANALISA"):
    data = yf.download(ticker, period="60d", interval=tf)
    df = brain.process_data(data)
    
    if not df.empty:
        res = brain.get_analysis(df)
        
        # MENU LIVE HARGA & VOLUME
        st.sidebar.subheader("📊 Market Stats")
        st.sidebar.metric("Harga Live", f"{res['curr']:,.2f}")
        st.sidebar.metric("Volume Pasar", f"{res['vol_now']:,.0f}")
        
        # MENU NEWS (BERITA CRYPTO/SAHAM)
        st.sidebar.subheader("📰 Latest News")
        ticker_news = yf.Ticker(ticker)
        for news in ticker_news.news[:3]:
            st.sidebar.markdown(f"**[{news['title']}]({news['link']})**")
            st.sidebar.write(f"Source: {news['publisher']}")
        
        # --- DASHBOARD UTAMA ---
        st.title(f"🎯 Analysis: {ticker}")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("ENTRY", f"{res['curr']:,.2f}")
        c2.metric("TAKE PROFIT", f"{res['tp']:,.2f}")
        c3.metric("STOP LOSS", f"{res['sl']:,.2f}")
        c4.metric("VOL Z-SCORE", f"{res['zscore']:.2f}")

        st.info(f"🧱 POC Wall: {res['poc']:,.2f} | 📐 Sudut Pythagoras: {res['angle']:.2f}°")

        # --- TRADINGVIEW LIVE CHART (WIDGET) ---
        st.subheader("📈 Live TradingView Chart")
        tv_symbol = ticker.replace("-", "") if "-" in ticker else ticker.replace(".JK", "")
        exchange = "BINANCE" if "-" in ticker else "IDX"
        
        tradingview_html = f"""
        <div class="tradingview-widget-container">
          <div id="tradingview_12345"></div>
          <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
          <script type="text/javascript">
          new TradingView.widget({{
            "width": "100%",
            "height": 500,
            "symbol": "{exchange}:{tv_symbol}",
            "interval": "60",
            "timezone": "Etc/UTC",
            "theme": "dark",
            "style": "1",
            "locale": "en",
            "toolbar_bg": "#f1f3f6",
            "enable_publishing": false,
            "allow_symbol_change": true,
            "container_id": "tradingview_12345"
          }});
          </script>
        </div>
        """
        components.html(tradingview_html, height=520)

        if res['score'] >= 80: st.success("🚀 SIGNAL: STRONG BUY")
    else:
        st.error("Gagal memuat data.")
