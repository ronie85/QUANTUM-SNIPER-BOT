# --- MENU BERITA (NEWS) YANG SUDAH DIPERBAIKI ---
        st.sidebar.subheader("📰 Berita Terkini")
        try:
            ticker_obj = yf.Ticker(ticker)
            news_data = ticker_obj.news
            
            if news_data and len(news_data) > 0:
                for n in news_data[:5]:
                    # Menampilkan judul berita yang bisa diklik
                    st.sidebar.markdown(f"✅ **[{n['title']}]({n['link']})**")
                    st.sidebar.caption(f"Sumber: {n['publisher']}")
            else:
                # Jika berita yfinance kosong, berikan link manual ke portal berita
                st.sidebar.warning("Berita spesifik tidak ditemukan.")
                search_url = f"https://www.google.com/search?q={ticker}+news"
                st.sidebar.markdown(f"🔗 [Klik di sini untuk Berita {ticker} di Google News]({search_url})")
                
                if ".JK" in ticker:
                    st.sidebar.markdown(f"🔗 [Berita Saham IDX (CNBC)] (https://www.cnbcindonesia.com/market)")
                else:
                    st.sidebar.markdown(f"🔗 [Berita Crypto (CoinDesk)] (https://www.coindesk.com/)")
        except Exception as e:
            st.sidebar.error("Koneksi berita terputus.")
