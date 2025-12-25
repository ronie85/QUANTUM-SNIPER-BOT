import numpy as np
import pandas as pd
from hmmlearn import hmm
import math  # <--- Ini wajib ada agar Pythagoras tidak error

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
        if len(df) < 35: return pd.DataFrame()
        
        df['log_ret'] = np.log(df['close'] / df['close'].shift(1))
        # Filter Paus: Z-Score dihitung dari 30 bar terakhir
        df['vol_zscore'] = (df['volume'] - df['volume'].rolling(30).mean()) / df['volume'].rolling(30).std()
        
        df = df.dropna()
        X = df[['log_ret']].values
        self.model.fit(X)
        df['state'] = self.model.predict(X)
        
        bull_state = np.argmax(self.model.means_)
        df['is_bullish'] = (df['state'] == bull_state)
        return df

    def get_analysis(self, df):
        close = df['close']
        
        # Lapis 3: Pythagoras Angle (Akselerasi)
        side_a = 14 
        side_b = ((close.iloc[-1] - close.iloc[-14]) / close.iloc[-14]) * 100
        angle = math.degrees(math.atan(side_b / side_a))
        
        # Lapis 4: POC Wall (S&R)
        bins = np.linspace(close.min(), close.max(), 20)
        v_profile = df.groupby(pd.cut(close, bins=bins), observed=True)['volume'].sum()
        poc = v_profile.idxmax().mid
        
        curr = close.iloc[-1]
        sl = poc if poc < curr else curr * 0.97
        tp = curr * (1 + abs(angle)/30) if angle > 0 else curr * 1.05
        
        # Skor Ketat untuk Menaikkan Win Rate ke 75-80%
        score = 0
        if df['is_bullish'].iloc[-1]: score += 40
        if angle > 8: score += 35 
        if df['vol_zscore'].iloc[-1] > 1.0: score += 25 
        
        signal = "STRONG BUY" if score >= 85 else "BUY" if score >= 60 else "WAIT/SELL"
        
        return {
            "curr": curr, "poc": poc, "angle": angle, "sl": sl, "tp": tp, 
            "score": score, "zscore": df['vol_zscore'].iloc[-1], 
            "vol_now": df['volume'].iloc[-1], "signal": signal
        }
