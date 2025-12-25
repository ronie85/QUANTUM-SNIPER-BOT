import streamlit as st
import yfinance as yf
from bot_brain import TradingBrain
import pandas as pd

st.set_page_config(page_title="Quantum Sniper PRO+", layout="wide")
brain = TradingBrain()

st.sidebar.title("🚀 Quantum Master")
ticker = st.sidebar.text_input("Simbol (Contoh: XRP-USD)", "XRP-USD")
tf = st.sidebar.selectbox("Timeframe", ["15m", "1h", "4h", "1d"], index=1)

if st.sidebar.button("JALANKAN ANALISA"):
    try:
        # 1. Download Data
        data = yf.download(ticker, period="60d", interval=tf)
        
        if data.empty:
            st.error("Gagal mengambil data. Pastikan simbol benar.")
        else:
            # 2. Proses Data
            df = brain.process_data(data)
            res = brain.get_analysis(df)
            
            if res:
                # 3. Tampilkan UI
                st.header(f"Hasil Analisa: {ticker}")
                
                m1, m2, m3 = st.columns(3)
                m1.metric("SINYAL", res['signal'])
                m2.metric("AKURASI", f"{res['score']}%")
                m3.metric("Z-SCORE VOL", round(res['vol_z'], 2))
                
                st.subheader("Detail Eksekusi")
                c1, c2, c3 = st.columns(3)
                c1.info(f"Entry: {res['curr']:.4f}")
                c2.success(f"Target: {res['tp']:.4f}")
                c3.error(f"Stop Loss: {res['sl']:.4f}")
                
                # Tampilkan Tabel Data untuk memastikan data masuk
                st.write("Preview Data Terakhir:")
                st.dataframe(df.tail(5))
            else:
                st.warning("Data tidak cukup untuk menghitung S&R. Coba timeframe lain.")
                
    except Exception as e:
        st.error(f"Error Terdeteksi: {str(e)}")
else:
    st.info("Silakan klik 'Jalankan Analisa' untuk memulai.")
