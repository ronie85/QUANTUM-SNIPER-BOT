import numpy as np
import pandas as pd
from hmmlearn import hmm

class TradingBrain:
    def __init__(self, n_states=3):
        self.n_states = n_states
        # Model HMM untuk mendeteksi rezim pasar (Bullish/Bearish)
        self.model = hmm.GaussianHMM(n_components=n_states, covariance_type="full", n_iter=100)

    def flatten_df(self, df):
        # Perbaikan krusial untuk error "Input array must be 1 dimensional"
        df = df.copy()
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df.columns = df.columns.str.lower()
        return df

    def process_data(self, df):
        df = self.flatten_df(df)
        # Menghapus data kosong agar tidak error saat perhitungan
        df = df[df['volume'] > 0].ffill().dropna()
        if len(df) < 30: return pd.DataFrame()
        
        # Log Returns untuk input HMM
        df['log_ret'] = np.log(df['close'] / df['close'].shift(1))
        # Z-Score Volume untuk mendeteksi anomali (Whale activity)
        df['vol_zscore'] = (df['volume'] - df['volume'].rolling(20).mean()) / df['volume'].rolling(20).std()
        df = df.dropna()
        
        # Training HMM menggunakan Algoritma Viterbi
        X = df[['log_ret']].values
        self.model.fit(X)
        df['state'] = self.model.predict(X)
        bull_state = np.argmax(self.model.means_)
        df['is_bullish'] = (df['state'] == bull_state)
        return df

    def get_analysis(self, df):
        close = df['close']
        # 1. Volume Profile (Mencari Tembok Besar/POC)
        bins = np.linspace(close.min(), close.max(), 15)
        v_profile = df.groupby(pd.cut(close, bins=bins), observed=True)['volume'].sum()
        poc = v_profile.idxmax().mid
        
        # 2. Pythagoras (Menghitung kemiringan/Slope tren)
        side_a = 14 # Jendela waktu
        side_b = ((close.iloc[-1] - close.iloc[-14]) / close.iloc[-14]) * 100
        angle = np.degrees(np.arctan(side_b / side_a))
        
        # 3. Menentukan Titik Entry, SL, dan TP
        curr = close.iloc[-1]
        sl = min(poc, curr * 0.97) # Stop Loss di bawah tembok volume
        tp = curr * (1 + abs(angle)/50) if angle > 0 else curr * 1.05
        
        # Perhitungan Skor Akhir (0-100)
        score = 0
        if df['is_bullish'].iloc[-1]: score += 50
        if angle > 20: score += 30
        if df['vol_zscore'].iloc[-1] > 1: score += 20
        
        return {
            "curr": curr, "poc": poc, "angle": angle, 
            "sl": sl, "tp": tp, "score": score,
            "zscore": df['vol_zscore'].iloc[-1]
        }
