import numpy as np
import pandas as pd
from hmmlearn import hmm

class TradingBrain:
    def __init__(self, n_states=3):
        self.n_states = n_states
        self.model = hmm.GaussianHMM(n_components=n_states, covariance_type="full", n_iter=100)

    def clean_data(self, df):
        new_df = pd.DataFrame(index=df.index)
        for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
            if col in df.columns:
                series = df[col].iloc[:, 0] if isinstance(df[col], pd.DataFrame) else df[col]
                new_df[col.lower()] = series.values
        return new_df.ffill().dropna()

    def process_data(self, df):
        df = self.clean_data(df)
        if len(df) < 20: return pd.DataFrame()
        df['log_ret'] = np.log(df['close'] / df['close'].shift(1))
        df['vol_zscore'] = (df['volume'] - df['volume'].rolling(10).mean()) / df['volume'].rolling(10).std()
        df = df.dropna()
        X = df[['log_ret']].values
        self.model.fit(X)
        df['state'] = self.model.predict(X)
        bull_state = np.argmax(self.model.means_)
        df['is_bullish'] = (df['state'] == bull_state)
        return df

    def get_analysis(self, df):
        close = df['close']
        bins = np.linspace(close.min(), close.max(), 15)
        v_profile = df.groupby(pd.cut(close, bins=bins), observed=True)['volume'].sum()
        poc = v_profile.idxmax().mid
        side_a, side_b = 10, ((close.iloc[-1] - close.iloc[-10]) / close.iloc[-10]) * 100
        angle = np.degrees(np.arctan(side_b / side_a))
        curr = close.iloc[-1]
        sl = min(poc, curr * 0.98)
        tp = curr * (1 + abs(angle)/40) if angle > 0 else curr * 1.05
        
        # Logika Sinyal
        score = (50 if df['is_bullish'].iloc[-1] else 0) + (30 if angle > 5 else 0) + (20 if df['vol_zscore'].iloc[-1] > 0.5 else 0)
        signal = "STRONG BUY" if score >= 80 else "BUY" if score >= 50 else "STRONG SELL" if score <= 20 else "WAIT"
        
        return {"curr": curr, "poc": poc, "angle": angle, "sl": sl, "tp": tp, "score": score, "zscore": df['vol_zscore'].iloc[-1], "vol_now": df['volume'].iloc[-1], "signal": signal}
