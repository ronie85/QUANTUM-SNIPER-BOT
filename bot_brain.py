import pandas as pd
import numpy as np

class TradingBrain:
    def __init__(self):
        self.len_sr = 30
        
    def process_data(self, df):
        # Memastikan data tidak kosong
        if df.empty: return df
        
        # 1. DYNAMIC S&R (LOGIKA LANTAI & ATAP)
        df['support_level'] = df['low'].rolling(window=self.len_sr).min()
        df['resistance_level'] = df['high'].rolling(window=self.len_sr).max()
        
        # POC Wall (Garis Tengah Keseimbangan)
        df['hlc3'] = (df['high'] + df['low'] + df['close']) / 3
        df['poc_wall'] = df['hlc3'].rolling(window=50).mean()

        # 2. FILTER VOLUME (Z-SCORE)
        v_ma = df['volume'].rolling(window=20).mean()
        v_std = df['volume'].rolling(window=20).std()
        df['v_zscore'] = (df['volume'] - v_ma) / v_std
        
        # 3. KALKULUS: PREDIKSI HARGA REAL-TIME
        df['dy'] = df['close'].diff() # Kecepatan
        df['d2y'] = df['dy'].diff()   # Percepatan
        
        # 4. LOGIKA ENTRY (ZERO LAG)
        # Buy: Harga nyentuh lantai, percepatan balik positif, volume tinggi
        df['is_high_vol'] = df['v_zscore'] > 1.2
        df['buy_zone'] = df['low'] <= (df['support_level'] * 1.002)
        df['is_reversing_up'] = (df['d2y'] > 0) & (df['dy'].shift(1) < 0)
        
        # Sell: Harga nyentuh atap, percepatan turun, volume tinggi
        df['sell_zone'] = df['high'] >= (df['resistance_level'] * 0.998)
        df['is_reversing_down'] = df['d2y'] < 0
        
        return df

    def get_analysis(self, df):
        last = df.iloc[-1]
        prev = df.iloc[-2]
        
        signal = "NEUTRAL"
        score = 0
        
        # Penentuan Signal Berdasarkan Logika Zero Lag
        if last['buy_zone'] and last['is_reversing_up'] and last['is_high_vol']:
            signal = "STRONG BUY (ZERO LAG)"
            score = 95
        elif last['sell_zone'] and last['is_reversing_down'] and last['is_high_vol']:
            signal = "STRONG SELL (ZERO LAG)"
            score = 95
        elif last['close'] > last['poc_wall']:
            signal = "BULLISH (ABOVE POC)"
            score = 60
        else:
            signal = "BEARISH (BELOW POC)"
            score = 40
            
        return {
            "signal": signal,
            "score": score,
            "curr": last['close'],
            "tp": last['close'] * 1.03, # Target 3%
            "sl": last['support_level'] if last['close'] > last['poc_wall'] else last['close'] * 0.98,
            "poc": last['poc_wall'],
            "vol_z": last['v_zscore']
        }
