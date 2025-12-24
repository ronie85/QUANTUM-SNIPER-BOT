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

    def get_snr(self, df, window=20):
        # Menghitung Support (Terendah) dan Resistance (Tertinggi) dalam periode tertentu
        lows = df['Low'].rolling(window=window).min()
        highs = df['High'].rolling(window=window).max()
        return lows.iloc[-1], highs.iloc[-1]

    def get_volume_profile(self, df, bins=50):
        close_data = df['Close'].squeeze()
        volume_data = df['Volume'].squeeze()
        bins_edges = np.linspace(close_data.min(), close_data.max(), bins)
        v_profile = df.groupby(pd.cut(close_data, bins=bins_edges), observed=False)[volume_data.name].sum()
        poc_price = v_profile.idxmax().mid
        return poc_price, v_profile

    def process_data(self, df):
        close_data = df['Close'].squeeze()
        df['Log_Ret'] = np.log(close_data / close_data.shift(1))
        df['Vol_ZScore'] = self.calculate_zscore(df['Volume'])
        df['Price_ZScore'] = self.calculate_zscore(df['Close'])
        
        # Tambahkan S&R ke dataframe untuk backtest
        df['Support'] = df['Low'].rolling(window=20).min()
        df['Resistance'] = df['High'].rolling(window=20).max()
        
        df.dropna(inplace=True)
        X = df[['Log_Ret']].values
        self.model.fit(X)
        df['State'] = self.model.predict(X)
        bullish_state = np.argmax(self.model.means_)
        df['Is_Bullish_Regime'] = (df['State'] == bullish_state)
        return df, bullish_state

    def generate_signal(self, df, poc_price):
        last_row = df.iloc[-1]
        close_p = last_row['Close'].item() if hasattr(last_row['Close'], 'item') else last_row['Close']
        support = last_row['Support']
        resistance = last_row['Resistance']
        
        # LOGIKA S&R SNIPER:
        # 1. HMM Harus Bullish
        # 2. Harga harus dekat dengan Support atau POC (Beli di Lantai)
        # 3. Z-Score Volume menunjukkan ada dorongan
        
        is_near_support = close_p <= (support * 1.01) or close_p <= (poc_price * 1.01)
        
        if last_row['Is_Bullish_Regime'] and is_near_support and last_row['Vol_ZScore'] > 0.5:
            return "🚀 BUY (At Support/POC)"
        elif close_p >= (resistance * 0.99) or not last_row['Is_Bullish_Regime']:
            return "⚠️ SELL (At Resistance/Trend Change)"
        else:
            return "⌛ WAIT"

    def perform_backtest(self, df, poc_price):
        balance = 1000
        position = 0
        entry_p = 0
        history = []

        for i in range(len(df)):
            row = df.iloc[i]
            curr_p = row['Close']
            supp = row['Support']
            ress = row['Resistance']
            
            # Entry: Bullish + Dekat Support/POC
            if row['Is_Bullish_Regime'] and (curr_p <= supp * 1.01 or curr_p <= poc_price * 1.01) and position == 0:
                position = balance / curr_p
                balance = 0
                entry_p = curr_p
                history.append({"Date": df.index[i], "Action": "BUY", "Price": f"{curr_p:.2f}"})
            
            # Exit: Sentuh Resistance atau State berubah
            elif position > 0:
                profit_loss = (curr_p - entry_p) / entry_p
                if curr_p >= ress * 0.99 or not row['Is_Bullish_Regime'] or profit_loss < -0.02:
                    balance = position * curr_p
                    position = 0
                    history.append({"Date": df.index[i], "Action": "SELL", "Price": f"{curr_p:.2f}", "P/L": f"{profit_loss*100:.2f}%"})
                    
        final_val = balance if position == 0 else position * df.iloc[-1]['Close']
        return final_val, history
