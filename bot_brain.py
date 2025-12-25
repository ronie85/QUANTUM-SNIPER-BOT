import pandas as pd
import numpy as np

class TradingBrain:
    def __init__(self):
        self.len_sr = 30
        
    def process_data(self, df):
        if df is None or len(df) < 50: 
            return pd.DataFrame()
        
        # FIX: Menghilangkan Multi-Index dari yfinance terbaru
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        
        # Memastikan nama kolom standar
        df.columns = [c.capitalize() for c in df.columns]

        # 1. DYNAMIC S&R (Support & Resistance)
        df['Support_level'] = df['Low'].rolling(window=self.len_sr).min()
        df['Resistance_level'] = df['High'].rolling(window=self.len_sr).max()
        
        # 2. VOLUME Z-SCORE
        v_ma = df['Volume'].rolling(window=20).mean()
        v_std = df['Volume'].rolling(window=20).std()
        df['V_zscore'] = (df['Volume'] - v_ma) / v_std
        
        # 3. KALKULUS (Kecepatan & Percepatan)
        df['Dy'] = df['Close'].diff()
        df['D2y'] = df['Dy'].diff()
        
        # 4. POC WALL (Garis Tengah)
        df['Poc_wall'] = ((df['High'] + df['Low'] + df['Close']) / 3).rolling(window=50).mean()
        
        return df

    def get_analysis(self, df):
        if df.empty or 'Support_level' not in df.columns:
            return None
            
        last = df.iloc[-1]
        prev = df.iloc[-2]
        
        # Logika Zero Lag
        is_high_vol = float(last['V_zscore']) > 1.2
        buy_zone = float(last['Low']) <= (float(last['Support_level']) * 1.002)
        is_reversing_up = (float(last['D2y']) > 0) and (float(prev['Dy']) < 0)
        
        signal = "WAITING"
        score = 50
        
        if buy_zone and is_reversing_up and is_high_vol:
            signal = "🟢 STRONG BUY"
            score = 95
        elif float(last['High']) >= (float(last['Resistance_level']) * 0.998) and float(last['D2y']) < 0:
            signal = "🔴 STRONG SELL"
            score = 95
            
        return {
            "signal": signal,
            "score": score,
            "curr": float(last['Close']),
            "tp": float(last['Close'] * 1.03),
            "sl": float(last['Support_level']),
            "poc": float(last['Poc_wall']),
            "vol_z": float(last['V_zscore'])
        }
