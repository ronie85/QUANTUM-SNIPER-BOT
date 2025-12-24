import numpy as np
import pandas as pd
from hmmlearn import hmm

class TradingBrain:
    def __init__(self, n_states=3):
        self.n_states = n_states
        self.model = hmm.GaussianHMM(n_components=n_states, covariance_type="full", n_iter=1000)

    def calculate_zscore(self, series, window=20):
        return (series - series.rolling(window=window).mean()) / series.rolling(window=window).std()

    def get_volume_profile(self, df, bins=50):
        # Menghitung POC (Point of Control)
        price_min = df['Low'].min()
        price_max = df['High'].max()
        bins_edges = np.linspace(price_min, price_max, bins)
        v_profile = df.groupby(pd.cut(df['Close'], bins=bins_edges))['Volume'].sum()
        poc_price = v_profile.idxmax().mid
        return poc_price, v_profile

    def process_data(self, df):
        # 1. Feature Engineering: Log Returns
        df['Log_Ret'] = np.log(df['Close'] / df['Close'].shift(1))
        df['Vol_ZScore'] = self.calculate_zscore(df['Volume'])
        df.dropna(inplace=True)

        # 2. Fit HMM & Viterbi Decoding
        X = df[['Log_Ret']].values
        self.model.fit(X)
        df['State'] = self.model.predict(X)

        # 3. Identify Bullish State (State dengan mean return tertinggi)
        bullish_state = np.argmax(self.model.means_)
        df['Is_Bullish_Regime'] = (df['State'] == bullish_state)
        
        return df, bullish_state

    def generate_signal(self, df, poc_price):
        last_row = df.iloc[-1]
        
        # LOGIKA KONFLUENS (Akurasi Tinggi)
        # 1. Rezim Bullish (HMM)
        # 2. Volume di atas rata-rata (Z-Score > 1)
        # 3. Harga dekat atau di atas POC (Volume Profile)
        
        condition_hmm = last_row['Is_Bullish_Regime']
        condition_vol = last_row['Vol_ZScore'] > 1.0
        condition_price = last_row['Close'] >= poc_price
        
        if condition_hmm and condition_vol and condition_price:
            return "BUY"
        elif not condition_hmm and last_row['Close'] < poc_price:
            return "SELL / EXIT"
        else:
            return "WAIT"
