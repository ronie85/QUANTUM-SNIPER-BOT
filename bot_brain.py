import numpy as np
import pandas as pd
from hmmlearn import hmm

class TradingBrain:
    def __init__(self, n_states=3):
        self.n_states = n_states
        self.model = hmm.GaussianHMM(n_components=n_states, covariance_type="full", n_iter=100)

    def process_data(self, df):
        # 1. Bersihkan Data
        df = df.copy()
        df.columns = df.columns.str.lower()
        df = df[df['volume'] > 0].ffill().dropna()
        
        # 2. Feature Engineering
        df['log_ret'] = np.log(df['close'] / df['close'].shift(1))
        df['vol_zscore'] = (df['volume'] - df['volume'].rolling(20).mean()) / df['volume'].rolling(20).std()
        df = df.dropna()
        
        # 3. HMM & Viterbi
        if len(df) > 30:
            X = df[['log_ret']].values
            self.model.fit(X)
            df['state'] = self.model.predict(X)
            # Cari state dengan rata-rata kenaikan tertinggi (Bullish State)
            bull_state = np.argmax(self.model.means_)
            df['is_bullish'] = (df['state'] == bull_state)
        else:
            df['is_bullish'] = False
        return df

    def get_levels(self, df, window=14):
        # POC Sederhana (Volume Profile)
        close = df['close']
        vol = df['volume']
        bins = np.linspace(close.min(), close.max(), 20)
        v_profile = df.groupby(pd.cut(close, bins=bins), observed=True)['volume'].sum()
        poc = v_profile.idxmax().mid
        
        # Pythagoras Slope (Kemiringan)
        side_a = window
        side_b = ((close.iloc[-1] - close.iloc[-window]) / close.iloc[-window]) * 100
        angle = np.degrees(np.arctan(side_b / side_a))
        
        # Entry, SL, TP
        curr = close.iloc[-1]
        sl = min(poc, curr * 0.97)
        tp = curr * (1 + abs(angle)/50) if angle > 0 else curr * 1.05
        
        return poc, angle, curr, sl, tp
