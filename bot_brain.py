import numpy as np
import pandas as pd
from hmmlearn import hmm

class TradingBrain:
    def __init__(self, n_states=3):
        self.n_states = n_states
        # Model HMM untuk mendeteksi Rezim Pasar
        self.model = hmm.GaussianHMM(n_components=n_states, covariance_type="full", n_iter=1000)

    def calculate_zscore(self, series, window=20):
        # Membersihkan data dari Multi-index jika ada
        s = series.squeeze()
        return (s - s.rolling(window=window).mean()) / s.rolling(window=window).std()

    def get_volume_profile(self, df, bins=50):
        # Membersihkan data untuk memastikan 1D
        close_data = df['Close'].squeeze()
        volume_data = df['Volume'].squeeze()
        
        price_min = close_data.min()
        price_max = close_data.max()
        bins_edges = np.linspace(price_min, price_max, bins)
        
        # Menghitung Volume di setiap rentang harga
        v_profile = df.groupby(pd.cut(close_data, bins=bins_edges))[volume_data.name].sum()
        poc_price = v_profile.idxmax().mid
        return poc_price, v_profile

    def calculate_pythagoras_slope(self, df, window=14):
        # Sisi A: Waktu (Jumlah Bar)
        side_a = window
        # Sisi B: Perubahan Harga dalam % (Normalisasi)
        price_start = df['Close'].squeeze().iloc[-window]
        price_end = df['Close'].squeeze().iloc[-1]
        side_b = ((price_end - price_start) / price_start) * 100
        
        # Pythagoras: Sisi C (Hypotenuse)
        side_c = np.sqrt(side_a**2 + side_b**2)
        # Menghitung sudut kemiringan (Slope)
        angle = np.degrees(np.arctan(side_b / side_a))
        return side_c, angle

    def process_data(self, df):
        # Feature Engineering
        close_s = df['Close'].squeeze()
        df['Log_Ret'] = np.log(close_s / close_s.shift(1))
        df['Vol_ZScore'] = self.calculate_zscore(df['Volume'])
        df.dropna(inplace=True)

        # HMM Training & Viterbi Decoding
        X = df[['Log_Ret']].values
        self.model.fit(X)
        df['State'] = self.model.predict(X)

        # Identifikasi State Bullish (Return rata-rata tertinggi)
        bullish_state = np.argmax(self.model.means_)
        df['Is_Bullish_Regime'] = (df['State'] == bullish_state)
        
        return df, bullish_state

    def generate_signal(self, df, poc_price):
        last_row = df.iloc[-1]
        _, angle = self.calculate_pythagoras_slope(df)
        
        # LOGIKA KONFLUENS AKURASI TINGGI
        is_hmm_bull = last_row['Is_Bullish_Regime']
        is_vol_high = last_row['Vol_ZScore'] > 1.0
        is_above_poc = last_row['Close'].squeeze() >= poc_price
        is_slope_ok = angle > 25  # Sudut minimal 25 derajat untuk konfirmasi tren
        
        if is_hmm_bull and is_vol_high and is_above_poc and is_slope_ok:
            return "🚀 STRONG BUY", angle
        elif not is_hmm_bull and last_row['Close'].squeeze() < poc_price:
            return "⚠️ EXIT / SHORT", angle
        else:
            return "⏳ WAIT / NEUTRAL", angle
