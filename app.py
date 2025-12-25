st.sidebar.subheader("📰 Berita Terkini")
            try:
                # Menggunakan link pencarian Google News yang lebih stabil
                ticker_clean = ticker.split('.')[0] # Menghilangkan .JK untuk pencarian berita
                news_link = f"https://www.google.com/search?q={ticker_clean}+stock+crypto+news&tbm=nws"
                
                # Menampilkan link berita utama
                st.sidebar.info(f"Dapatkan info terbaru untuk {ticker}:")
                st.sidebar.markdown(f"🚀 [KLIK: Baca Berita {ticker_clean} di Google News]({news_link})")
                
                # Opsi tambahan portal berita besar
                st.sidebar.divider()
                if ".JK" in ticker:
                    st.sidebar.markdown("🔗 [CNBC Indonesia - Market](https://www.cnbcindonesia.com/market)")
                    st.sidebar.markdown("🔗 [Kontan Online](https://www.kontan.co.id/)")
                else:
                    st.sidebar.markdown("🔗 [CoinDesk News](https://www.coindesk.com/)")
                    st.sidebar.markdown("🔗 [CryptoPanic Aggregator](https://cryptopanic.com/)")
            except:
                st.sidebar.write("Gunakan pencarian Google News manual.")
