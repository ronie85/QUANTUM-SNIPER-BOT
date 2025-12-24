import streamlit as st
import yfinance as yf
import pandas as pd
from bot_brain import TradingBrain
from streamlit_tradingview_chart_lite import chart

st.set_page_config(page_title="Quantum Sniper PRO", layout="wide")
st.title("🎯 Quantum Sniper: HMM + Pythagoras + TV Chart")

# SIDEBAR
st.sidebar.header("⚙️ Market Selector")
market = st.sidebar.selectbox("Pilih Market", ["Saham Indonesia (IDX)", "Crypto"])

if market == "Saham Indonesia (IDX)":
    ticker = st.sidebar.text_input("Kode Saham (Contoh: BBRI.JK)", "BBCA.JK")
else:
    ticker = st.sidebar.text_input("Simbol Crypto", "BTC-USD")

tf = st.sidebar.selectbox("Timeframe", ["15m", "1h", "1d"], index=1)

if st.button("RUN QUANTUM ANALYSIS"):
    with st.spinner("Processing Big Data..."):
        # 1. Load Data
        raw_df = yf.download(ticker, period="60d", interval=tf)
        
        if raw_df.empty:
            st.error("Data tidak ditemukan! Gunakan akhiran .JK untuk saham Indonesia.")
        else:
            # Fix yfinance Multi-index Columns
            df = raw_df.copy()
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            df.columns = df.columns.str.lower()

            # 2. Inisialisasi & Proses
            brain = TradingBrain()
            df_proc = brain.process_data(df)
            
            # 3. Hitung Kalkulasi Kuantitatif
            poc, sup, res = brain.get_volume_profile(df_proc)
            angle = brain.calculate_pythagoras_slope(df_proc)
            entry, sl, tp = brain.get_trade_levels(df_proc, poc, angle)
            is_bull = df_proc['is_bullish'].iloc[-1]

            # 4. Tampilan Metrik
            m1, m2, m3 = st.columns(3)
            m1.metric("ENTRY POINT", f"{entry:,.0f}" if market=="Saham Indonesia (IDX)" else f"{entry:,.2f}")
            m2.metric("STOP LOSS", f"{sl:,.0f}" if market=="Saham Indonesia (IDX)" else f"{sl:,.2f}", delta_color="inverse")
            m3.metric("TAKE PROFIT", f"{tp:,.0f}" if market=="Saham Indonesia (IDX)" else f"{tp:,.2f}")

            # 5. Sidebar Angka Petunjuk
            st.sidebar.subheader("📍 Petunjuk S&R")
            st.sidebar.info(f"Resistance: {res:,.0f}\n\nPOC (Wall): {poc:,.0f}\n\nSupport: {sup:,.0f}")
            st.sidebar.write(f"Sudut Pythagoras: **{angle:.2f}°**")

            # 6. TradingView Chart
            st.subheader(f"📈 Price Action: {ticker}")
            tv_df = df_proc.reset_index()
            tv_df = tv_df.rename(columns={tv_df.columns[0]: 'time'})
            tv_df['time'] = tv_df['time'].dt.strftime('%Y-%m-%d %H:%M:%S')
            
            # Filter kolom untuk TV Chart
            tv_data = tv_df[['time', 'open', 'high', 'low', 'close']]
            chart(tv_data, height=500, theme='dark', chart_type='line')

            # 7. Final Signal
            if is_bull and angle > 25:
                st.success(f"🚀 **STRONG BUY CONFIRMED!** Sudut Pythagoras ({angle:.2f}°) menunjukkan momentum Paus.")
            elif not is_bull and angle < 0:
                st.error("⚠️ **BEARISH STATE.** Sebaiknya Exit atau tunggu di Support.")
            else:
                st.warning("⏳ **NEUTRAL/SIDEWAYS.** Harga sedang konsolidasi di sekitar POC.")
