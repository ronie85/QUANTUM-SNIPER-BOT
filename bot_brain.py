import numpy as np
import pandas as pd
from hmmlearn import hmm

class TradingBrain:
    def __init__(self, n_states=3):
        self.n_states = n_states
        # Model HMM untuk mendeteksi rezim pasar (Viterbi Decoding)
        self.model = hmm.GaussianHMM(n_components=n_states, covariance_type="full", n_iter=100)

    def flatten_df(self, df):
        # SOLUSI ERROR: Meratakan MultiIndex agar menjadi 1D yang bersih
        df = df.copy()
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df.columns = df.columns.str.lower()
        return df

    def process_data(self, df):
        df = self.flatten_df(df)
        # Menghapus data volume 0 (transaksi kosong)
        df = df[df['volume'] > 0].ffill().dropna()
        if len(df) < 30: return pd.DataFrame()
        
        # Kalkulasi Log Returns untuk HMM
        df['log_ret'] = np.log(df['close'] / df['close'].shift(1))
        # Z-SCORE VOLUME: Mendeteksi anomali volume Paus
        df['vol_zscore'] = (df['volume'] - df['volume'].rolling(20).mean()) / df['volume'].rolling(20).std()
        df = df.dropna()
        
        # Training HMM
        X = df[['log_ret']].values
        self.model.fit(X)
        df['state'] = self.model.predict(X)
        
        # Menentukan State Bullish (Return rata-rata tertinggi)
        bull_state = np.argmax(self.model.means_)
        df['is_bullish'] = (df['state'] == bull_state)
        return df

    def get_analysis(self, df):
        close = df['close']
        # 1. VOLUME PROFILE (S&R): Mencari Point of Control (POC)
        bins = np.linspace(close.min(), close.max(), 15)
        v_profile = df.groupby(pd.cut(close, bins=bins), observed=True)['volume'].sum()
        poc = v_profile.idxmax().mid
        
        # 2. PYTHAGORAS: Menghitung kemiringan (Slope) tren
        side_a = 14 # Window waktu
        side_b = ((close.iloc[-1] - close.iloc[-14]) / close.iloc[-14]) * 100
        angle = np.degrees(np.arctan(side_b / side_a))
        
        # 3. TRADING LEVELS: Entry, Stop Loss (SL), Take Profit (TP)
        curr = close.iloc[-1]
        entry = curr
        # SL diletakkan di bawah POC Wall atau 3% dari Entry
        sl = min(poc, entry * 0.97)
        # TP dihitung berdasarkan momentum Pythagoras
        tp = entry * (1 + abs(angle)/50) if angle > 0 else entry * 1.05
        
        # Skor Konfluens (0-100)
        score = 0
        if df['is_bullish'].iloc[-1]: score += 50
        if angle > 20: score += 30
        if df['vol_zscore'].iloc[-1] > 1: score += 20
        
        return {
            "curr": curr, "poc": poc, "angle": angle, 
            "sl": sl, "tp": tp, "score": score,
            "zscore": df['vol_zscore'].iloc[-1]
        }
