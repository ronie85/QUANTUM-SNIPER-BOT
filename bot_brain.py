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

    def get_volume_profile(self, df, bins=50):
        close_data = df['Close'].squeeze()
        volume_data = df['Volume'].squeeze()
        price_min = close_data.min()
        price_max = close_data.max()
        bins_edges = np.linspace(price_min, price_max, bins)
        v_profile = df.groupby(pd.cut(close_data, bins=bins_edges), observed=False)[volume_data.name].sum()
        poc_price = v_profile.idxmax().mid
        return poc_price, v_profile

    def process_data(self, df):
        close_data = df['Close'].squeeze()
        df['Log_Ret'] = np.log(close_data / close_data.shift(1))
        df['Vol_ZScore'] = self.calculate_zscore(df['Volume'])
        df.dropna(inplace=True)
        X = df[['Log_Ret']].values
        self.model.fit(X)
        df['State'] = self.model.predict(X)
        bullish_state = np.argmax(self.model.means_)
        df['Is_Bullish_Regime'] = (df['State'] == bullish_state)
        return df, bullish_state

    def generate_signal(self, df, poc_price):
        last_row = df.iloc[-1]
        close_price = last_row['Close'].item() if hasattr(last_row['Close'], 'item') else last_row['Close']
        condition_hmm = last_row['Is_Bullish_Regime']
        condition_vol = last_row['Vol_ZScore'] > 1.0
        condition_price = close_price >= poc_price
        
        if condition_hmm and condition_vol and condition_price:
            return "🚀 BUY"
        elif not condition_hmm and close_price < poc_price:
            return "⚠️ SELL"
        else:
            return "⌛ WAIT"

    def perform_backtest(self, df, poc_price, initial_balance=1000):
        balance = initial_balance
        position = 0
        history = []

        for i in range(len(df)):
            row = df.iloc[i]
            close_price = row['Close'].item() if hasattr(row['Close'], 'item') else row['Close']
            
            # Logika Konfluens
            is_bullish = row['Is_Bullish_Regime']
            vol_high = row['Vol_ZScore'] > 1.0
            above_poc = close_price >= poc_price

            # BUY Logic
            if is_bullish and vol_high and above_poc and position == 0:
                position = balance / close_price
                balance = 0
                history.append({"Date": df.index[i], "Action": "BUY", "Price": f"{close_price:.2f}", "Balance": "Holding"})

            # SELL Logic
            elif (not is_bullish or close_price < poc_price) and position > 0:
                balance = position * close_price
                position = 0
                history.append({"Date": df.index[i], "Action": "SELL", "Price": f"{close_price:.2f}", "Balance": f"{balance:.2f}"})

        final_value = balance if position == 0 else position * df.iloc[-1]['Close'].item()
        return final_value, history
