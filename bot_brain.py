import numpy as np
import pandas as pd
from hmmlearn import hmm

class TradingBrain:
    def __init__(self, n_states=3):
        self.n_states = n_states
        self.model = hmm.GaussianHMM(n_components=n_states, covariance_type="full", n_iter=100)

    def calculate_zscore(self, series, window=20):
        if len(series) < window: return pd.Series(0, index=series.index)
        return (series - series.rolling(window=window).mean()) / series.rolling(window=window).std()

    def get_volume_profile(self, df, bins=20):
        close = df['close'].ffill()
        vol = df['volume'].ffill()
        if close.min() == close.max(): return close.min(), close.min(), close.min()
        bins_edges = np.linspace(close.min(), close.max(), bins)
        v_profile = df.groupby(pd.cut(close, bins=bins_edges), observed=True)['volume'].sum()
        poc = v_profile.idxmax().mid
        return poc, poc * 0.98, poc * 1.02

    def calculate_pythagoras_slope(self, df, window=10):
        if len(df) < window: return 0
        side_a = window
        p = df['close']
        side_b = ((p.iloc[-1] - p.iloc[-window]) / p.iloc[-window]) * 100
        return np.degrees(np.arctan(side_b / side_a))

    def process_data(self, df):
        df = df.copy()
        df.columns = df.columns.str.lower()
        df = df[df['volume'] > 0]
        df['log_ret'] = np.log(df['close'] / df['close'].shift(1))
        df['vol_zscore'] = self.calculate_zscore(df['volume'])
        df = df.dropna()
        X = df[['log_ret']].values
        if len(X) > 10:
            self.model.fit(X)
            df['state'] = self.model.predict(X)
            bull_st = np.argmax(self.model.means_)
            df['is_bullish'] = (df['state'] == bull_st)
        else:
            df['is_bullish'] = False
        return df
