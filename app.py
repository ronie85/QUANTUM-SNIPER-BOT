import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from bot_brain import TradingBrain

st.set_page_config(page_title="Quantum Sniper Bot", layout="wide")
st.title("🎯 Quantum Sniper: HMM + Volume Profile")

st.sidebar.header("Konfigurasi Bot")
asset_type = st.sidebar.selectbox("Jenis Aset", ["Crypto", "Saham"])
ticker = st.sidebar.text_input("Simbol", "BTC-USD" if asset_type == "Crypto" else "AAPL")
timeframe = st.sidebar.selectbox("Timeframe", ["15m", "1h", "4h", "1d"], index=1)
period = "60d" if timeframe in ["15m", "1h"] else "2y"

if st.sidebar.button("Jalankan Analisa & Backtest"):
    try:
        with st.spinner("Memproses data masa lalu..."):
            df = yf.download(ticker, period=period, interval=timeframe)
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            
            brain = TradingBrain()
            poc_price, v_profile = brain.get_volume_profile(df)
            df_processed, bull_state = brain.process_data(df)
            
            # Hitung Sinyal Sekarang
            current_signal = brain.generate_signal(df_processed, poc_price)
            
            # Hitung Backtest
            final_val, history = brain.perform_backtest(df_processed, poc_price)
            roi = ((final_val - 1000) / 1000) * 100

            # Tampilan Metrik
            c1, c2, c3 = st.columns(3)
            c1.metric("SIGNAL SAAT INI", current_signal)
            c2.metric("HASIL BACKTEST (Modal $1000)", f"${final_val:.2f}", f"{roi:.2f}% ROI")
            c3.metric("POC PRICE", f"{poc_price:.2f}")

            # Grafik
            fig = go.Figure(data=[go.Candlestick(x=df_processed.index, open=df_processed['Open'], high=df_processed['High'], low=df_processed['Low'], close=df_processed['Close'])])
            fig.add_hline(y=poc_price, line_dash="dash", line_color="gold", annotation_text="POC Level")
            st.plotly_chart(fig, use_container_width=True)

            # Tabel Transaksi
            if history:
                st.subheader("📜 Riwayat Transaksi Masa Lalu")
                st.table(pd.DataFrame(history))
            else:
                st.info("Tidak ada transaksi yang ditemukan dengan kriteria konfluens ini.")

    except Exception as e:
        st.error(f"Error: {e}")
