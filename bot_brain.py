import numpy as np
import pandas as pd
from hmmlearn import hmm
import math

class TradingBrain:
    def __init__(self, n_states=3):
        self.n_states = n_states
        # Inisialisasi model AI HMM
        self.model = hmm.GaussianHMM(n_components=n_states, covariance_type="full", n_iter=100)

    def clean_data(self, df):
        new_df = pd.DataFrame(index=df.index)
        # Menangani data multi-index dari yfinance
        for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
            if col in df.columns:
                series = df[col].iloc[:, 0] if isinstance(df[col], pd.DataFrame) else df[col]
                new_df[col.lower()] = series.values
        return new_df.ffill().dropna()

    def process_data(self, df):
        df = self.clean_data(df)
        if len(df) < 35: 
            return pd.DataFrame()
            
        # Lapis 1: Log Returns untuk deteksi Rezim Pasar
        df['log_ret'] = np.log(df['close'] / df['close'].shift(1))
        
        # Lapis 2: Z-Score Volume (Filter Paus)
        df['vol_zscore'] = (df['volume'] - df['volume'].rolling(30).mean()) / df['volume'].rolling(30).std()
        
        df = df.dropna()
        if len(df) < 10: return pd.DataFrame()
        
        X = df[['log_ret']].values
        self.model.fit(X)
        df['state'] = self.model.predict(X)
        
        # Menentukan State Bullish & Bearish
        means = self.model.means_.flatten()
        bull_state = np.argmax(means)
        bear_state = np.argmin(means)
        
        df['is_bullish'] = (df['state'] == bull_state)
        df['is_bearish'] = (df['state'] == bear_state)
        return df

    def get_analysis(self, df, balance=1000):
        close = df['close']
        vol_z = df['vol_zscore'].iloc[-1]
        
        # Lapis 3: Pythagoras Angle (Akselerasi Tren)
        side_a = 14
        side_b = ((close.iloc[-1] - close.iloc[-14]) / close.iloc[-14]) * 100
        angle = math.degrees(math.atan(side_b / side_a))
        
        # Lapis 4: POC Wall (S&R Statis)
        bins = np.linspace(close.min(), close.max(), 20)
        v_profile = df.groupby(pd.cut(close, bins=bins, include_lowest=True), observed=True)['volume'].sum()
        poc = v_profile.idxmax().mid
        
        curr = close.iloc[-1]
        
        # Skor Strategi
        score_long = 0
        if df['is_bullish'].iloc[-1]: score_long += 40
        if angle > 8: score_long += 35
        if vol_z > 1.0: score_long += 25
        
        score_short = 0
        if df['is_bearish'].iloc[-1]: score_short += 40
        if angle < -8: score_short += 35
        if vol_z > 1.0: score_short += 25

        # Penentuan Sinyal
        if score_long >= 85:
            signal = "STRONG BUY"
            final_score = score_long
        elif score_short >= 85:
            signal = "STRONG SELL"
            final_score = score_short
        else:
            signal = "WAIT / NEUTRAL"
            final_score = max(score_long, score_short)
        
        # Risk Management (SL & TP)
        dist = abs(curr - poc) / curr
        if signal == "STRONG BUY":
            sl = poc if poc < curr else curr * 0.97
            tp = curr * (1 + (abs(angle)/20))
        elif signal == "STRONG SELL":
            sl = poc if poc > curr else curr * 1.03
            tp = curr * (1 - (abs(angle)/20))
        else:
            sl, tp = curr * 0.97, curr * 1.03
            
        # Leverage Safe Calculation
        lev = math.floor(0.8 / dist) if dist > 0.005 else 5
        lev = min(max(lev, 1), 20)

        return {
            "curr": curr, "signal": signal, "score": int(final_score),
            "sl": sl, "tp": tp, "lev": lev, "angle": angle, "poc": poc
        }
