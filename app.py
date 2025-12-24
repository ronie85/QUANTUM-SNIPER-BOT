import numpy as np
import pandas as pd
from hmmlearn import hmm

class TradingBrain:
    def __init__(self, n_states=3):
        self.n_states = n_states
        self.model = hmm.GaussianHMM(n_components=n_states, covariance_type="full", n_iter=1000)

    def calculate_zscore(self, series, window=20):
        s = series.squeeze()
        return (s - s.rolling(window=window).mean()) / s.rolling(window=window).std()

    def get_volume_profile(self, df, bins=30):
        close_data = df['Close'].squeeze()
        volume_data = df['Volume'].squeeze()
        price_min, price_max = close_data.min(), close_data.max()
        bins_edges = np.linspace(price_min, price_max, bins)
        v_profile = df.groupby(pd.cut(close_data, bins=bins_edges))[volume_data.name].sum()
        poc_price = v_profile.idxmax().mid
        
        # S&R berdasarkan High Volume Nodes (HVN)
        sorted_v = v_profile.sort_values(ascending=False)
        support = sorted_v.index[1].mid if len(sorted_v) > 1 else poc_price * 0.95
        resistance = sorted_v.index[2].mid if len(sorted_v) > 2 else poc_price * 1.05
        return poc_price, support, resistance

    def calculate_pythagoras_slope(self, df, window=14):
        side_a = window
        price = df['Close'].squeeze()
        side_b = ((price.iloc[-1] - price.iloc[-window]) / price.iloc[-window]) * 100
        angle = np.degrees(np.arctan(side_b / side_a))
        return angle

    def process_data(self, df):
        close_s = df['Close'].squeeze()
        df['Log_Ret'] = np.log(close_s / close_s.shift(1))
        df['Vol_ZScore'] = self.calculate_zscore(df['Volume'])
        df.dropna(inplace=True)
        X = df[['Log_Ret']].values
        self.model.fit(X)
        df['State'] = self.model.predict(X)
        bullish_state = np.argmax(self.model.means_)
        df['Is_Bullish_Regime'] = (df['State'] == bullish_state)
        return df

    def get_trade_levels(self, df, poc_price, angle):
        current_price = df['Close'].squeeze().iloc[-1]
        # Entry di harga sekarang jika sinyal valid
        entry = current_price
        # Stop Loss di bawah POC atau 2% dari entry
        stop_loss = min(poc_price, entry * 0.98)
        # Take Profit berdasarkan risk/reward 1:3 atau sudut Pythagoras
        tp_multiplier = 1 + (max(angle, 10) / 100)
        take_profit = entry * tp_multiplier
        return entry, stop_loss, take_profit
