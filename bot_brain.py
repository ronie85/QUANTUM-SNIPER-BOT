import pandas as pd
import numpy as np

class TradingBrain:
    def __init__(self):
        self.len_sr = 30
        
    def process_data(self, df):
        if df.empty: return df
        
        # PERBAIKAN KRUSIAL: Menghapus Multi-index agar kolom terbaca
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        
        # Standarisasi Nama Kolom
        df.columns = [str(c).capitalize() for c in df.columns]

        # Rumus S&R (Support & Resistance) Dasar
        df['Support'] = df['Low'].rolling(window=self.len_sr).min()
        df['Resistance'] = df['High'].rolling(window=self.len_sr).max()
        
        # Indikator Momentum Dasar
        df['SMA_Fast'] = df['Close'].rolling(10).mean()
        df['SMA_Slow'] = df['Close'].rolling(30).mean()
        
        return df

    def get_analysis(self, df):
        if df.empty or len(df) < 30: return None
        
        last = df.iloc[-1]
        
        # Logika Sinyal Sederhana (Sebelum diubah-ubah)
        signal = "WAITING"
        if last['Close'] > last['SMA_Fast'] and last['Close'] > last['Support']:
            signal = "🟢 BULLISH"
        elif last['Close'] < last['SMA_Fast'] and last['Close'] < last['Resistance']:
            signal = "🔴 BEARISH"
            
        return {
            "signal": signal,
            "price": float(last['Close']),
            "support": float(last['Support']),
            "resistance": float(last['Resistance'])
        }
