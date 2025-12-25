import numpy as np
import pandas as pd
from hmmlearn import hmm

class TradingBrain:
    def __init__(self, n_states=3):
        self.n_states = n_states
        # Inisialisasi model HMM yang stabil
        self.model = hmm.GaussianHMM(n_components=n_states, covariance_type="full", n_iter=100)

    def clean_data(self, df):
        """Memastikan data bersih dari MultiIndex yfinance"""
        new_df = pd.DataFrame(index=df.index)
        for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
            if col in df.columns:
                # Mengambil level pertama jika MultiIndex ditemukan
                series = df[col]
                if isinstance(series, pd.DataFrame):
                    series = series.iloc[:, 0]
                new_df[col.lower()] = series.values
        return new_df.ffill().dropna()

    def process_data(self, df):
        df = self.clean_data(df)
        if len(df) < 25: return pd.DataFrame()
        
        # Kalkulasi teknikal dasar
        df['log_ret'] = np.log(df['close'] / df['close'].shift(1))
        df['vol_zscore'] = (df['volume'] - df['volume'].rolling(15).mean()) / df['volume'].rolling(15).std()
        df = df.dropna()
        
        # Eksekusi Algoritma HMM
        X = df[['log_ret']].values
        self.model.fit(X)
        df['state'] = self.model.predict(X)
        bull_state = np.argmax(self.model.means_)
        df['is_bullish'] = (df['state'] == bull_state)
        return df

    def get_analysis(self, df):
        close = df['close']
        # Perhitungan Support & Resistance (POC Wall)
        bins = np.linspace(close.min(), close.max(), 15)
        v_profile = df.groupby(pd.cut(close, bins=bins), observed=True)['volume'].sum()
        poc = v_profile.idxmax().mid
        
        # Perhitungan Sudut Pythagoras (Kemiringan Tren)
        side_a = 12
        side_b = ((close.iloc[-1] - close.iloc[-12]) / close.iloc[-12]) * 100
        angle = np.degrees(np.arctan(side_b / side_a))
        
        curr = close.iloc[-1]
        sl = min(poc, curr * 0.98)
        tp = curr * (1 + abs(angle)/40) if angle > 0 else curr * 1.05
        
        # Penentuan Sinyal Akhir
        score = (50 if df['is_bullish'].iloc[-1] else 0) + (30 if angle > 5 else 0) + (20 if df['vol_zscore'].iloc[-1] > 0.5 else 0)
        signal = "STRONG BUY" if score >= 80 else "BUY" if score >= 50 else "STRONG SELL" if score <= 20 else "WAIT"
        
        return {
            "curr": curr, "poc": poc, "angle": angle, "sl": sl, "tp": tp, 
            "score": score, "zscore": df['vol_zscore'].iloc[-1], 
            "vol_now": df['volume'].iloc[-1], "signal": signal
        }
