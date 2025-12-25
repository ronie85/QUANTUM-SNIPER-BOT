import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from bot_brain import TradingBrain

st.set_page_config(page_title="Quantum Sniper PRO", layout="wide")
brain = TradingBrain()

# Navigasi Menu Dashboard
menu = st.sidebar.radio("Navigasi", ["Analisa Tunggal", "Scanner 10 Aset"])

if menu == "Analisa Tunggal":
    st.title("🎯 Quantum Sniper: Analisa Kuantitatif")
    ticker = st.sidebar.text_input("Simbol (e.g. BBCA.JK / BTC-USD)", "BTC-USD")
    tf = st.sidebar.selectbox("Timeframe", ["15m", "1h", "1d"], index=1)
    
    if st.sidebar.button("JALANKAN ANALISA"):
        data = yf.download(ticker, period="60d", interval=tf)
        df = brain.process_data(data)
        
        if not df.empty:
            res = brain.get_analysis(df)
            
            # Baris 1: Level Eksekusi (Entry, TP, SL, Z-Score)
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("ENTRY POINT", f"{res['curr']:,.2f}")
            c2.metric("TAKE PROFIT", f"{res['tp']:,.2f}")
            c3.metric("STOP LOSS", f"{res['sl']:,.2f}")
            c4.metric("VOL Z-SCORE", f"{res['zscore']:.2f}")

            # Baris 2: Pythagoras & S&R Petunjuk
            st.divider()
            col_a, col_b = st.columns(2)
            with col_a:
                st.write(f"### 📐 Sudut Pythagoras: {res['angle']:.2f}°")
            with col_b:
                st.write(f"### 🧱 S&R (POC Wall): {res['poc']:,.2f}")
            
            # Tampilan Grafik Candlestick
            fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['open'], high=df['high'], low=df['low'], close=df['close'])])
            fig.add_hline(y=res['poc'], line_dash="dash", line_color="yellow", annotation_text="POC Wall")
            fig.update_layout(template="plotly_dark", height=500)
            st.plotly_chart(fig, use_container_width=True)
            
            if res['score'] >= 80: st.success("🚀 SINYAL: STRONG BUY (Siap Eksekusi)")
        else:
            st.error("Gagal menarik data. Pastikan simbol ticker benar.")

elif menu == "Scanner 10 Aset":
    st.title("🔍 Top 10 High-Probability Scanner")
    market_type = st.selectbox("Pilih Pasar", ["Saham Indonesia (IDX)", "Crypto"])
    
    # Daftar Aset untuk Di-scan
    if market_type == "Saham Indonesia (IDX)":
        assets = ["BBCA.JK", "BBRI.JK", "TLKM.JK", "ASII.JK", "GOTO.JK", "BMRI.JK", "ADRO.JK", "UNTR.JK", "AMRT.JK", "BBNI.JK"]
    else:
        assets = ["BTC-USD", "ETH-USD", "BNB-USD", "SOL-USD", "XRP-USD", "ADA-USD", "DOGE-USD", "DOT-USD", "MATIC-USD", "AVAX-USD"]

    if st.button("MULAI SCANNING"):
        scan_results = []
        progress = st.progress(0)
        
        for idx, symbol in enumerate(assets):
            data = yf.download(symbol, period="60d", interval="1h", progress=False)
            df = brain.process_data(data)
            if not df.empty:
                res = brain.get_analysis(df)
                scan_results.append({
                    "Simbol": symbol, "Skor": res['score'], "Harga": f"{res['curr']:,.2f}", 
                    "Target TP": f"{res['tp']:,.2f}", "Cut Loss": f"{res['sl']:,.2f}", "Sudut": f"{res['angle']:.1f}°"
                })
            progress.progress((idx + 1) / len(assets))
        
        # Menampilkan tabel hasil scan berdasarkan skor tertinggi
        scan_df = pd.DataFrame(scan_results).sort_values(by="Skor", ascending=False)
        st.table(scan_df)
        st.info("Pilih aset dengan Skor > 70 untuk probabilitas keuntungan 80-300%.")
