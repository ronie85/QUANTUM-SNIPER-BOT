import streamlit as st
import yfinance as yf
import pandas as pd
import streamlit.components.v1 as components
from bot_brain import TradingBrain

st.set_page_config(page_title="Quantum Sniper PRO+", layout="wide")
brain = TradingBrain()

# Sidebar: Navigasi Menu
st.sidebar.title("🚀 Quantum Sniper Menu")
menu = st.sidebar.radio("Navigasi Utama", ["🎯 Analisa Detail", "🔍 Scanner 10 Aset"])

if menu == "🎯 Analisa Detail":
    ticker = st.sidebar.text_input("Simbol (ex: BTC-USD / BBCA.JK)", "XRP-USD")
    tf = st.sidebar.selectbox("Timeframe", ["15m", "1h", "4h", "1d"], index=1)
    
    if st.sidebar.button("JALANKAN ANALISA"):
        # Penarikan data diperpanjang (250 hari) agar TF 4H tidak kosong
        raw_data = yf.download(ticker, period="250d", interval=tf)
        df = brain.process_data(raw_data)
        
        if not df.empty:
            res = brain.get_analysis(df)
            
            # Sidebar: Status & Berita
            st.sidebar.divider()
            st.sidebar.subheader("📊 Market Stats")
            st.sidebar.metric("Harga Live", f"{res['curr']:,.4f}")
            st.sidebar.metric("Volume Pasar", f"{res['vol_now']:,.0f}")
            
            st.sidebar.subheader("📰 Berita Terkini")
            try:
                t_obj = yf.Ticker(ticker)
                for n in t_obj.news[:5]:
                    st.sidebar.markdown(f"**[{n['title']}]({n['link']})**")
            except:
                st.sidebar.write("Berita tidak tersedia.")

            # Main Panel: Sinyal & Metrik
            st.title(f"Analisa Quantum: {ticker}")
            if "BUY" in res['signal']: st.success(f"### 📢 SINYAL: {res['signal']} (Skor: {res['score']})")
            else: st.warning(f"### 📢 SINYAL: {res['signal']} (Skor: {res['score']})")

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("ENTRY POINT", f"{res['curr']:,.4f}")
            c2.metric("TAKE PROFIT", f"{res['tp']:,.4f}")
            c3.metric("STOP LOSS", f"{res['sl']:,.4f}")
            c4.metric("VOL Z-SCORE", f"{res['zscore']:.2f}")

            st.info(f"🧱 POC Wall (S&R): {res['poc']:,.4f} | 📐 Sudut Pythagoras: {res['angle']:.2f}°")

            # TradingView Widget (Besar & Interaktif)
            st.subheader("📈 TradingView Real-time Chart")
            tv_symbol = ticker.replace("-", "") if "-" in ticker else ticker.replace(".JK", "")
            if ".JK" in ticker: tv_symbol = f"IDX:{tv_symbol}"
            else: tv_symbol = f"BINANCE:{tv_symbol}T"
            
            # Konversi TF untuk TradingView
            tv_tf = "240" if tf == "4h" else "60" if tf == "1h" else "D" if tf == "1d" else "15"
            
            components.html(f"""
                <div id="tv_chart_box" style="height:600px;">
                    <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
                    <script type="text/javascript">
                    new TradingView.widget({{
                        "width": "100%", "height": 600, "symbol": "{tv_symbol}",
                        "interval": "{tv_tf}", "theme": "dark", "style": "1",
                        "locale": "en", "toolbar_bg": "#f1f3f6", "enable_publishing": false,
                        "allow_symbol_change": true, "container_id": "tv_chart_box"
                    }});
                    </script>
                </div>
            """, height=620)
        else:
            st.error("Data tidak cukup atau simbol salah. Coba aset lain.")

elif menu == "🔍 Scanner 10 Aset":
    st.title("Top 10 High Probability Assets")
    mkt = st.selectbox("Pilih Market Scanner", ["Crypto", "Saham Indonesia (IDX)"])
    
    # Daftar Aset Pilihan
    if mkt == "Crypto":
        assets = ["BTC-USD","ETH-USD","XRP-USD","SOL-USD","BNB-USD","ADA-USD","DOGE-USD","MATIC-USD","DOT-USD","LTC-USD"]
    else:
        assets = ["BBCA.JK","BBRI.JK","TLKM.JK","ASII.JK","GOTO.JK","BMRI.JK","ADRO.JK","UNTR.JK","AMRT.JK","BBNI.JK"]
    
    if st.button("MULAI SCAN SEKARANG"):
        results = []
        prog = st.progress(0)
        for i, s in enumerate(assets):
            d = yf.download(s, period="100d", interval="1h", progress=False)
            df_s = brain.process_data(d)
            if not df_s.empty:
                r = brain.get_analysis(df_s)
                results.append({"Simbol": s, "Signal": r['signal'], "Skor": r['score'], "Harga": f"{r['curr']:,.4f}"})
            prog.progress((i + 1) / len(assets))
        
        st.table(pd.DataFrame(results).sort_values(by="Skor", ascending=False))
