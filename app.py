import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from bot_brain import TradingBrain

st.set_page_config(page_title="Quantum Sniper Pro", layout="wide")
st.title("🎯 Quantum Sniper: HMM & Pythagoras")

# Sidebar
st.sidebar.header("Market Settings")
market = st.sidebar.selectbox("Market", ["Saham IDX", "Crypto"])
if market == "Saham IDX":
    ticker = st.sidebar.text_input("Ticker (e.g., BBCA.JK)", "BBCA.JK")
else:
    ticker = st.sidebar.text_input("Ticker (e.g., BTC-USD)", "BTC-USD")
tf = st.sidebar.selectbox("Timeframe", ["15m", "1h", "1d"], index=1)

if st.sidebar.button("RUN ANALYSIS"):
    try:
        # 1. Download & Fix yfinance format
        data = yf.download(ticker, period="60d", interval=tf)
        if data.empty:
            st.error("Data tidak ditemukan! Pastikan ticker benar.")
        else:
            # Flattening Multi-index Columns
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)
            
            brain = TradingBrain()
            df = brain.process_data(data)
            
            if not df.empty:
                poc, angle, curr, sl, tp = brain.get_levels(df)
                is_bull = df['is_bullish'].iloc[-1]

                # Tampilan Metrics
                c1, c2, c3 = st.columns(3)
                c1.metric("ENTRY POINT", f"{curr:,.0f}" if market=="Saham IDX" else f"{curr:,.2f}")
                c2.metric("STOP LOSS (POC)", f"{sl:,.0f}" if market=="Saham IDX" else f"{sl:,.2f}")
                c3.metric("TAKE PROFIT", f"{tp:,.0f}" if market=="Saham IDX" else f"{tp:,.2f}")

                # Tabel Angka Petunjuk di Sidebar
                st.sidebar.divider()
                st.sidebar.write(f"**POC Wall:** {poc:,.0f}")
                st.sidebar.write(f"**Trend Angle:** {angle:.2f}°")

                # Line Chart (Plotly - Anti Error)
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=df.index, y=df['close'], mode='lines', name='Price', line=dict(color='#00ff00')))
                fig.add_hline(y=poc, line_dash="dash", line_color="yellow", annotation_text="POC")
                fig.update_layout(template="plotly_dark", height=500, margin=dict(l=20, r=20, t=20, b=20))
                st.plotly_chart(fig, use_container_width=True)

                # Final Signal
                if is_bull and angle > 20:
                    st.success(f"🚀 **STRONG BUY!** Pythagoras & HMM Konfirmasi.")
                elif not is_bull:
                    st.error("⚠️ **MARKET BEARISH.** Hati-hati jebakan Paus.")
                else:
                    st.warning("⏳ **SIDEWAYS.** Menunggu konfirmasi volume.")
            else:
                st.warning("Data kurang untuk perhitungan HMM.")
    except Exception as e:
        st.error(f"Terjadi kesalahan teknis: {e}")
