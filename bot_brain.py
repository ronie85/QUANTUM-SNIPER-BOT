import numpy as np
import pandas as pd
from hmmlearn import hmm

class TradingBrain:
    def __init__(self, n_states=3):
        self.n_states = n_states
        self.model = hmm.GaussianHMM(n_components=n_states, covariance_type="full", n_iter=1000)

    def calculate_zscore(self, series, window=20):
        s = series.ffill().bfill()
        return (s - s.rolling(window=window).mean()) / s.rolling(window=window).std()

    def get_volume_profile(self, df, bins=30):
        close_data = df['close'].ffill()
        volume_data = df['volume'].ffill()
        
        price_min, price_max = close_data.min(), close_data.max()
        if price_min == price_max:
            return price_min, price_min, price_min
            
        bins_edges = np.linspace(price_min, price_max, bins)
        v_profile = df.groupby(pd.cut(close_data, bins=bins_edges), observed=True)['volume'].sum()
        
        poc_price = v_profile.idxmax().mid
        sorted_v = v_profile.sort_values(ascending=False)
        support = sorted_v.index[1].mid if len(sorted_v) > 1 else poc_price * 0.98
        resistance = sorted_v.index[2].mid if len(sorted_v) > 2 else poc_price * 1.02
        return poc_price, support, resistance

    def calculate_pythagoras_slope(self, df, window=14):
        if len(df) < window: return 0
        side_a = window
        price = df['close']
        side_b = ((price.iloc[-1] - price.iloc[-window]) / price.iloc[-window]) * 100
        angle = np.degrees(np.arctan(side_b / side_a))
        return angle

    def process_data(self, df):
        # Membersihkan data nol (sering terjadi di Saham IDX)
        df = df[df['volume'] > 0].copy()
        df['log_ret'] = np.log(df['close'] / df['close'].shift(1))
        df['vol_zscore'] = self.calculate_zscore(df['volume'])
        df = df.dropna()
        
        X = df[['log_ret']].values
        self.model.fit(X)
        df['state'] = self.model.predict(X)
        
        bullish_state = np.argmax(self.model.means_)
        df['is_bullish'] = (df['state'] == bullish_state)
        return df

    def get_trade_levels(self, df, poc_price, angle):
        curr = df['close'].iloc[-1]
        entry = curr
        stop_loss = min(poc_price, entry * 0.97) # SL 3% atau di POC
        tp_multiplier = 1 + (max(abs(angle), 5) / 50) # TP dinamis berdasarkan kekuatan Pythagoras
        take_profit = entry * tp_multiplier
        return entry, stop_loss, take_profit
