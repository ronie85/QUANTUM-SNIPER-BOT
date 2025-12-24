import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from bot_brain import TradingBrain

st.set_page_config(page_title="Quantum Sniper Bot", layout="wide")

st.title("🎯 Quantum Sniper: HMM + Volume Profile")
st.markdown("---")

# SIDEBAR SETTINGS
st.sidebar.header("Konfigurasi Bot")
asset_type = st.sidebar.selectbox("Jenis Aset", ["Crypto", "Saham"])

if asset_type == "Crypto":
    ticker = st.sidebar.text_input("Simbol (ex: BTC-USD)", "BTC-USD")
else:
    ticker = st.sidebar.text_input("Simbol (ex: BBCA.JK atau NVDA)", "NVDA")

timeframe = st.sidebar.selectbox("Timeframe", ["15m", "1h", "4h", "1d"], index=1)
period = "100d" if timeframe in ["15m", "1h"] else "2y"

# TOMBOL EKSEKUSI
if st.sidebar.button("Jalankan Analisa"):
    try:
        with st.spinner(f"Sedang menarik data {ticker} dan menghitung probabilitas..."):
            # 1. Download Data
            df = yf.download(ticker, period=period, interval=timeframe)
            
            if df.empty:
                st.error("Data tidak ditemukan. Pastikan simbol ticker benar.")
            else:
                # 2. Pembersihan Multi-index (Fix Error 1D)
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)
                
                # 3. Inisialisasi Otak Bot
                brain = TradingBrain(n_states=3)
                
                # 4. Hitung Volume Profile & HMM
                poc_price, v_profile = brain.get_volume_profile(df)
                df_processed, bull_state = brain.process_data(df)
                signal = brain.generate_signal(df_processed, poc_price)

                # 5. TAMPILKAN METRIK
                col1, col2, col3 = st.columns(3)
                col1.metric("SIGNAL", signal)
                col2.metric("POC (Whale Level)", f"{poc_price:.2f}")
                
                current_state = df_processed['State'].iloc[-1]
                state_desc = "Bullish" if current_state == bull_state else "Bearish/Neutral"
                col3.metric("Current Market State", f"{current_state} ({state_desc})")

                # 6. VISUALISASI CHART
                fig = go.Figure()
                
                # Candlestick
                fig.add_trace(go.Candlestick(
                    x=df_processed.index,
                    open=df_processed['Open'],
                    high=df_processed['High'],
                    low=df_processed['Low'],
                    close=df_processed['Close'],
                    name="Market Price"
                ))

                # Garis POC (Whale Wall)
                fig.add_hline(y=poc_price, line_dash="dash", line_color="gold", 
                             annotation_text="POC (High Volume Node)", annotation_position="top left")

                fig.update_layout(title=f"Analisa Teknikal Kuantitatif {ticker}", yaxis_title="Harga", height=600)
                st.plotly_chart(fig, use_container_width=True)

                st.success("Analisa Selesai. Gunakan sinyal ini sebagai pendukung keputusan, bukan satu-satunya acuan.")

    except Exception as e:
        st.error(f"Terjadi kesalahan teknis: {e}")
        st.info("Saran: Coba refresh halaman atau cek penulisan Simbol Aset.")

else:
    st.info("Silakan klik tombol 'Jalankan Analisa' di sidebar untuk memulai.")
