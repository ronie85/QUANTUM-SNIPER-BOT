import streamlit as st
import yfinance as yf
from bot_brain import TradingBrain

st.set_page_config(page_title="Quantum Sniper PRO+", layout="wide")
brain = TradingBrain()

st.title("🚀 Quantum Sniper - Zero Lag Edition")

ticker = st.sidebar.text_input("Simbol", "BTC-USD")
tf = st.sidebar.selectbox("Timeframe", ["15m", "1h", "4h", "1d"], index=1)

if st.sidebar.button("JALANKAN ANALISA"):
    data = yf.download(ticker, period="100d", interval=tf)
    df = brain.process_data(data)
    res = brain.get_analysis(df)
    
    # Header Info
    c1, c2, c3 = st.columns(3)
    c1.metric("SINYAL", res['signal'])
    c2.metric("SKOR AKURASI", f"{res['score']}%")
    c3.metric("VOL Z-SCORE", f"{res['vol_z']:.2f}")

    # Panel Strategi
    st.divider()
    col_a, col_b = st.columns(2)
    with col_a:
        st.success(f"🟢 ENTRY BUY: {res['curr']:.2f}")
        st.info(f"🧱 POC WALL (SUPPORT): {res['poc']:.2f}")
    with col_b:
        st.warning(f"🎯 TARGET PROFIT: {res['tp']:.2f}")
        st.error(f"⚠️ STOP LOSS: {res['sl']:.2f}")
        
    st.balloons() if "BUY" in res['signal'] else None
