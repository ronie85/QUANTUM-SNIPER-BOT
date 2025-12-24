import numpy as np
import pandas as pd
from hmmlearn import hmm

class TradingBrain:
    def __init__(self, n_states=3):
        self.n_states = n_states
        # Menggunakan covariance 'diag' untuk stabilitas pada data multi-feature
        self.model = hmm.GaussianHMM(n_components=n_states, covariance_type="diag", n_iter=2000)

    def calculate_zscore(self, series, window=20):
        s = series.squeeze()
        return (s - s.rolling(window=window).mean()) / (s.rolling(window=window).std() + 1e-9)

    def calculate_rsi(self, series, period=14):
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / (loss + 1e-9)
        return 100 - (100 / (1 + rs))

    def get_volume_profile(self, df, bins=50):
        close_data = df['Close'].squeeze()
        volume_data = df['Volume'].squeeze()
        bins_edges = np.linspace(close_data.min(), close_data.max(), bins)
        v_profile = df.groupby(pd.cut(close_data, bins=bins_edges), observed=False)[volume_data.name].sum()
        poc_price = v_profile.idxmax().mid
        return poc_price, v_profile

    def process_data(self, df):
        close_p = df['Close'].squeeze()
        # Rumus Diperbarui: HMM sekarang melihat Perubahan Harga DAN Perubahan Volatilitas
        df['Log_Ret'] = np.log(close_p / close_p.shift(1))
        df['Vol_Change'] = np.log(df['Volume'] / df['Volume'].shift(1)).replace([np.inf, -np.inf], 0)
        
        df['Vol_ZScore'] = self.calculate_zscore(df['Volume'])
        df['RSI'] = self.calculate_rsi(close_p)
        df['ATR'] = (df['High'] - df['Low']).rolling(window=14).mean() # Volatility feature
        
        # S&R Dinamis
        df['Support'] = df['Low'].rolling(window=30).min()
        df['Resistance'] = df['High'].rolling(window=30).max()
        
        df.dropna(inplace=True)

        # Matriks Input HMM: Menggabungkan Return dan Volatilitas
        X = df[['Log_Ret', 'Vol_Change']].values
        self.model.fit(X)
        
        # Algoritma Viterbi: Decoding State yang paling mungkin
        df['State'] = self.model.predict(X)
        
        # Cari State Bullish (Mean Return tertinggi)
        # Indeks 0 dari model.means_ adalah Log_Ret
        bullish_state = np.argmax(self.model.means_[:, 0])
        df['Is_Bullish_Regime'] = (df['State'] == bullish_state)
        
        return df, bullish_state

    def generate_signal(self, df, poc_price):
        last_row = df.iloc[-1]
        close_p = last_row['Close']
        
        # Sniper Strategy:
        # 1. Viterbi State = Bullish
        # 2. RSI di area 'Spring' (40-65), bukan Overbought
        # 3. Harga di atas Support/POC dengan konfirmasi volume
        
        cond_hmm = last_row['Is_Bullish_Regime']
        cond_rsi = 40 < last_row['RSI'] < 75
        cond_price = close_p >= (last_row['Support'] * 0.995) # Harga kuat di support
        cond_vol = last_row['Vol_ZScore'] > 0.5
        
        if cond_hmm and cond_rsi and cond_price and cond_vol:
            return "🚀 BUY"
        elif last_row['RSI'] > 85 or close_p < (poc_price * 0.97) or not cond_hmm:
            return "⚠️ SELL"
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
            
            # Entry Logic (Buy)
            if row['Is_Bullish_Regime'] and 40 < row['RSI'] < 70 and \
               curr_p >= row['Support'] and position == 0:
                
                position = balance / curr_p
                balance = 0
                entry_p = curr_p
                history.append({"Date": df.index[i], "Action": "BUY", "Price": f"{curr_p:.2f}"})

            # Exit Logic (Sell)
            elif position > 0:
                p_l = (curr_p - entry_p) / entry_p
                # Stop Loss Dinamis: 1.5x ATR di bawah Entry
                stop_loss = entry_p - (1.5 * row['ATR'])
                
                if curr_p <= stop_loss or row['RSI'] > 85 or not row['Is_Bullish_Regime']:
                    balance = position * curr_p
                    position = 0
                    history.append({"Date": df.index[i], "Action": "SELL", "Price": f"{curr_p:.2f}", "P/L": f"{p_l*100:.2f}%"})
                    
        final_val = balance if position == 0 else position * df.iloc[-1]['Close']
        return final_val, history
