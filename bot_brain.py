import pandas as pd
import numpy as np

class TradingBrain:
    def __init__(self):
        self.len_sr = 30
        
    def process_data(self, df):
        if df.empty: return df
        
        # 1. PAKSA DATA JADI FLAT (MENGATASI ERROR MULTI-INDEX)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        
        # S&R Logika Zero Lag
        df['Support'] = df['Low'].rolling(window=self.len_sr).min()
        df['Resistance'] = df['High'].rolling(window=self.len_sr).max()
        
        # Volume & Momentum
        df['V_Z'] = (df['Volume'] - df['Volume'].rolling(20).mean()) / df['Volume'].rolling(20).std()
        df['Dy'] = df['Close'].diff()
        df['D2y'] = df['Dy'].diff()
        
        return df

    def get_analysis(self, df):
        if df.empty or len(df) < 30: return None
        
        last = df.iloc[-1]
        prev = df.iloc[-2]
        
        # Logika Zero Lag: Masuk di Lantai
        buy_cond = (last['Low'] <= last['Support'] * 1.002) and (last['D2y'] > 0)
        sell_cond = (last['High'] >= last['Resistance'] * 0.998) and (last['D2y'] < 0)
        
        res = "WAITING"
        if buy_cond: res = "🟢 BUY AT SUPPORT"
        elif sell_cond: res = "🔴 SELL AT RESISTANCE"
            
        return {
            "signal": res,
            "price": float(last['Close']),
            "support": float(last['Support']),
            "resistance": float(last['Resistance']),
            "vz": float(last['V_Z'])
        }
