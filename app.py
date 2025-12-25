import streamlit as st
import yfinance as yf
from bot_brain import TradingBrain

st.set_page_config(page_title="Quantum Sniper PRO+", layout="wide")
brain = TradingBrain()

# --- SIDEBAR ---
st.sidebar.title("🚀 Quantum Sniper")
ticker = st.sidebar.text_input("Simbol Aset", "BTC-USD")
tf = st.sidebar.selectbox("Timeframe", ["15m", "1h", "4h", "1d"], index=1)

if st.sidebar.button("JALANKAN ANALISA"):
    try:
        # Menarik data
        with st.spinner('Mengambil data pasar...'):
            data = yf.download(ticker, period="100d", interval=tf)
        
        if data.empty:
            st.error("Data tidak ditemukan. Cek kembali simbol asetnya.")
        else:
            df = brain.process_data(data)
            res = brain.get_analysis(df)
            
            if res:
                # --- PANEL UTAMA ---
                st.title(f"Analisis: {ticker}")
                
                col1, col2, col3 = st.columns(3)
                col1.metric("SINYAL", res['signal'])
                col2.metric("SCORE", f"{res['score']}%")
                col3.metric("VOL Z-SCORE", f"{res['vol_z']:.2f}")
                
                st.divider()
                
                # Info Harga & S&R
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("HARGA SAAT INI", f"{res['curr']:.2f}")
                c2.metric("POC WALL (S&R)", f"{res['poc']:.2f}")
                c3.metric("TARGET PROFIT", f"{res['tp']:.2f}")
                c4.metric("STOP LOSS", f"{res['sl']:.2f}")
                
                if "BUY" in res['signal']:
                    st.balloons()
                    st.success("Konfirmasi: Harga di area Support + Percepatan naik!")
                elif "SELL" in res['signal']:
                    st.warning("Konfirmasi: Harga di area Resistance + Percepatan turun!")
                    
            else:
                st.warning("Data belum cukup untuk analisis S&R. Tunggu beberapa bar lagi.")
                
    except Exception as e:
        st.error(f"Terjadi kesalahan teknis: {e}")

else:
    st.info("Masukkan simbol aset di sidebar dan klik 'Jalankan Analisa'")
