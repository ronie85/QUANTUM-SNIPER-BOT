import streamlit as st
import yfinance as yf
from bot_brain import TradingBrain

st.set_page_config(page_title="Quantum Sniper Fix", layout="wide")
brain = TradingBrain()

st.title("🚀 Quantum Sniper Dashboard")

# Input di sidebar
symbol = st.sidebar.text_input("Simbol Aset", "XRP-USD")
interval = st.sidebar.selectbox("Timeframe", ["15m", "1h", "4h", "1d"], index=1)

if st.sidebar.button("ANALISA SEKARANG"):
    try:
        # Tarik data dengan penanganan khusus
        df_raw = yf.download(symbol, period="60d", interval=interval)
        
        if not df_raw.empty:
            df = brain.process_data(df_raw)
            result = brain.get_analysis(df)
            
            if result:
                # Tampilkan angka besar
                c1, c2, c3 = st.columns(3)
                c1.metric("SINYAL", result['signal'])
                c2.metric("HARGA", f"{result['price']:.4f}")
                c3.metric("VOL Z-SCORE", f"{result['vz']:.2f}")
                
                st.divider()
                
                # Tampilkan area S&R
                st.write(f"**Lantai (Support):** {result['support']:.4f}")
                st.write(f"**Atap (Resistance):** {result['resistance']:.4f}")
                
                # Tampilkan tabel untuk bukti data masuk
                st.subheader("Data Market Terakhir")
                st.dataframe(df.tail(10))
            else:
                st.error("Data masuk tapi gagal diproses. Coba simbol lain.")
        else:
            st.error("Gagal menarik data dari Yahoo Finance.")
            
    except Exception as e:
        st.error(f"Sistem Error: {str(e)}")
