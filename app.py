import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from bot_brain import TradingBrain

st.set_page_config(page_title="Quantum Sniper PRO", layout="wide")
brain = TradingBrain()

menu = st.sidebar.radio("Menu Utama", ["🔍 Scanner 10 Aset", "🎯 Analisa Detail"])

if menu == "🎯 Analisa Detail":
    st.title("Quantum Sniper Detail Analysis")
    ticker = st.sidebar.text_input("Simbol", "BBCA.JK")
    tf = st.sidebar.selectbox("Timeframe", ["15m", "1h", "1d"], index=1)
    
    if st.sidebar.button("JALANKAN"):
        data = yf.download(ticker, period="60d", interval=tf)
        df = brain.process_data(data)
        if not df.empty:
            res = brain.get_analysis(df)
            # Layout Metrik
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("ENTRY", f"{res['curr']:,.2f}")
            c2.metric("TAKE PROFIT", f"{res['tp']:,.2f}")
            c3.metric("STOP LOSS", f"{res['sl']:,.2f}")
            c4.metric("VOL Z-SCORE", f"{res['zscore']:.2f}")
            
            # Info S&R & Pythagoras
            st.info(f"🧱 POC Wall (S&R): {res['poc']:,.2f} | 📐 Sudut Pythagoras: {res['angle']:.2f}°")
            
            # Chart Plotly
            fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['open'], high=df['high'], low=df['low'], close=df['close'])])
            fig.add_hline(y=res['poc'], line_dash="dash", line_color="yellow")
            fig.update_layout(template="plotly_dark", height=500)
            st.plotly_chart(fig, use_container_width=True)
        else: st.error("Data tidak cukup atau simbol salah.")

elif menu == "🔍 Scanner 10 Aset":
    st.title("Top 10 High Probability Assets")
    mkt = st.selectbox("Pilih Market", ["Saham IDX", "Crypto"])
    assets = ["BBCA.JK","BBRI.JK","TLKM.JK","ASII.JK","GOTO.JK","BMRI.JK","ADRO.JK","UNTR.JK","AMRT.JK","BBNI.JK"] if mkt == "Saham IDX" else ["BTC-USD","ETH-USD","SOL-USD","BNB-USD","XRP-USD","ADA-USD","DOGE-USD","DOT-USD","LINK-USD","AVAX-USD"]

    if st.button("MULAI SCANNING"):
        results = []
        for symbol in assets:
            d = yf.download(symbol, period="60d", interval="1h", progress=False)
            df_p = brain.process_data(d)
            if not df_p.empty:
                r = brain.get_analysis(df_p)
                results.append({"Simbol": symbol, "Skor": r['score'], "Harga": f"{r['curr']:,.2f}", "TP": f"{r['tp']:,.2f}", "SL": f"{r['sl']:,.2f}", "Angle": f"{r['angle']:.1f}°"})
        st.table(pd.DataFrame(results).sort_values(by="Skor", ascending=False))
