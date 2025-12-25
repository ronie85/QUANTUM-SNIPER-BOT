import streamlit as st
import yfinance as yf
import pandas as pd
import streamlit.components.v1 as components
from bot_brain import TradingBrain

st.set_page_config(page_title="Quantum Sniper PRO+", layout="wide")
brain = TradingBrain()

st.sidebar.title("🚀 Quantum Menu")
ticker = st.sidebar.text_input("Simbol (ex: BTC-USD / XRP-USD)", "XRP-USD")
# Menambah timeframe 4h
tf = st.sidebar.selectbox("Timeframe", ["15m", "1h", "4h", "1d"], index=1)

if st.sidebar.button("JALANKAN ANALISA"):
    # Gunakan period lebih lama (200d) agar 4h tidak kosong
    with st.spinner('Mengambil data pasar & berita...'):
        raw_data = yf.download(ticker, period="200d", interval=tf)
        df = brain.process_data(raw_data)
    
    if not df.empty:
        res = brain.get_analysis(df)
        
        # --- SIDEBAR MARKET STATUS ---
        st.sidebar.divider()
        st.sidebar.subheader("📊 Market Status")
        st.sidebar.metric("Harga Live", f"{res['curr']:,.4f}")
        st.sidebar.metric("Volume", f"{res['vol_now']:,.0f}")
        
        # --- KONEKSI BERITA (NEWS) ---
        st.sidebar.subheader("📰 Berita Terkini")
        try:
            t = yf.Ticker(ticker)
            news = t.news
            if news:
                for n in news[:5]:
                    st.sidebar.markdown(f"**[{n['title']}]({n['link']})**")
                    st.sidebar.caption(f"Sumber: {n['publisher']}")
            else:
                st.sidebar.write("Tidak ada berita untuk aset ini.")
        except:
            st.sidebar.write("Gagal koneksi ke server berita.")

        # --- DASHBOARD UTAMA ---
        st.title(f"Analisa Quantum: {ticker}")
        
        # Menampilkan Sinyal Buy/Sell yang besar
        if "BUY" in res['signal']:
            st.success(f"### 📢 SINYAL: {res['signal']} (Skor: {res['score']})")
        elif "SELL" in res['signal']:
            st.error(f"### 📢 SINYAL: {res['signal']} (Skor: {res['score']})")
        else:
            st.warning(f"### 📢 SINYAL: {res['signal']} (Skor: {res['score']})")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("ENTRY", f"{res['curr']:,.4f}")
        c2.metric("TAKE PROFIT", f"{res['tp']:,.4f}")
        c3.metric("STOP LOSS", f"{res['sl']:,.4f}")
        c4.metric("VOL Z-SCORE", f"{res['zscore']:.2f}")

        st.info(f"🧱 POC Wall (S&R): {res['poc']:,.4f} | 📐 Sudut Pythagoras: {res['angle']:.2f}°")

        # --- TRADINGVIEW CHART ---
        st.subheader("🖼️ Interactive TradingView Chart")
        tv_symbol = ticker.replace("-", "") if "-" in ticker else ticker.replace(".JK", "")
        # Konversi interval ke format TradingView (4h = 240)
        tv_tf = "240" if tf == "4h" else "60" if tf == "1h" else "D" if tf == "1d" else "15"
        
        tradingview_html = f"""
        <div class="tradingview-widget-container" style="height:500px;">
          <div id="tradingview_chart"></div>
          <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
          <script type="text/javascript">
          new TradingView.widget({{
            "autosize": true, "symbol": "BINANCE:{tv_symbol}T", "interval": "{tv_tf}",
            "timezone": "Etc/UTC", "theme": "dark", "style": "1", "locale": "en",
            "toolbar_bg": "#f1f3f6", "enable_publishing": false, "allow_symbol_change": true,
            "container_id": "tradingview_chart"
          }});
          </script>
        </div>
        """
        components.html(tradingview_html, height=520)
    else:
        st.error(f"Data untuk timeframe {tf} tidak cukup. Coba timeframe lain atau ganti aset.")
