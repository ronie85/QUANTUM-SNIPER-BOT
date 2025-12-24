import streamlit as st
import yfinance as yf
from bot_brain import TradingBrain
import plotly.graph_objects as go

st.set_page_config(page_title="Quantum Sniper Bot", layout="wide")
st.title("🎯 Quantum Sniper: HMM + Volume Profile")

# Sidebar
asset_type = st.sidebar.selectbox("Pilih Jenis Aset", ["Crypto", "Saham"])
if asset_type == "Crypto":
    ticker = st.sidebar.text_input("Simbol (ex: BTC-USD)", "BTC-USD")
else:
    ticker = st.sidebar.text_input("Simbol (ex: BBCA.JK atau AAPL)", "AAPL")

timeframe = st.sidebar.selectbox("Timeframe", ["15m", "1h", "1d"], index=1)

# Main Logic
if st.button("Jalankan Analisa"):
    with st.spinner("Menghitung Probabilitas Viterbi..."):
        # Load Data
        df = yf.download(ticker, period="60d", interval=timeframe)
        
        brain = TradingBrain()
        poc_price, v_profile = brain.get_volume_profile(df)
        df_processed, bull_state = brain.process_data(df)
        signal = brain.generate_signal(df_processed, poc_price)

        # Dashboard Metrics
        col1, col2, col3 = st.columns(3)
        col1.metric("Sinyal Utama", signal)
        col2.metric("POC Price", f"{poc_price:.2f}")
        col3.metric("Current State", f"State {df_processed['State'].iloc[-1]}")

        # Visualisasi Plotly
        fig = go.Figure()
        fig.add_trace(go.Candlestick(x=df_processed.index, open=df_processed['Open'],
                        high=df_processed['High'], low=df_processed['Low'], close=df_processed['Close'], name="Harga"))
        
        # Garis POC
        fig.add_hline(y=poc_price, line_dash="dash", line_color="gold", annotation_text="POC (Whale Wall)")
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.write("### Karakteristik Rezim (HMM States)")
        st.write("Bot mendeteksi State", bull_state, "sebagai jalur Bullish utama.")
