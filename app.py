import streamlit as st
import yfinance as yf
import pandas as pd
from bot_brain import TradingBrain
from streamlit_echarts import st_echarts

st.set_page_config(page_title="Quantum Sniper v2", layout="wide")
st.title("🎯 Quantum Sniper: HMM + Pythagoras")

ticker = st.sidebar.text_input("Ticker (e.g. BBCA.JK or BTC-USD)", "BBCA.JK")
tf = st.sidebar.selectbox("Timeframe", ["15m", "1h", "1d"], index=1)

if st.sidebar.button("RUN ANALYSIS"):
    df = yf.download(ticker, period="60d", interval=tf)
    
    if df.empty:
        st.error("Data Not Found!")
    else:
        # Fix Column Multi-index
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        
        brain = TradingBrain()
        df_proc = brain.process_data(df)
        
        if not df_proc.empty:
            poc, sup, res = brain.get_volume_profile(df_proc)
            angle = brain.calculate_pythagoras_slope(df_proc)
            curr = df_proc['close'].iloc[-1]
            entry, sl, tp = curr, min(poc, curr*0.97), curr*(1+abs(angle)/50)

            # Metrics
            m1, m2, m3 = st.columns(3)
            m1.metric("ENTRY", f"{entry:,.0f}")
            m2.metric("STOP LOSS", f"{sl:,.0f}", delta_color="inverse")
            m3.metric("TAKE PROFIT", f"{tp:,.0f}")

            # E-Charts Line Chart
            options = {
                "xAxis": {"type": "category", "data": df_proc.index.strftime('%m-%d %H:%M').tolist()},
                "yAxis": {"type": "value", "scale": True},
                "series": [{"data": df_proc['close'].tolist(), "type": "line", "smooth": True, "color": "#f39c12"}],
                "tooltip": {"trigger": "axis"}
            }
            st_echarts(options=options, height="400px")

            # Final Signal
            st.sidebar.info(f"POC: {poc:,.0f}\nAngle: {angle:.2f}°")
            if df_proc['is_bullish'].iloc[-1] and angle > 20:
                st.success("🚀 STRONG BUY")
            else:
                st.warning("⏳ WAIT / NEUTRAL")
        else:
            st.warning("Insufficient data for HMM calculation.")
