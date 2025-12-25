def get_futures_advice(self, res, balance, risk_percent=2):
        """
        Kalkulator Manajemen Risiko khusus Futures
        risk_percent: berapa % dari modal yang rela hilang jika kena SL
        """
        # Menghitung jarak ke Stop Loss
        stop_distance = abs(res['curr'] - res['sl']) / res['curr']
        
        # Menghitung ukuran posisi (Position Size)
        # Rumus: (Modal * % Risiko) / Jarak SL
        if stop_distance == 0: return None
        
        pos_size = (balance * (risk_percent / 100)) / stop_distance
        
        # Rekomendasi Leverage agar tidak kena likuidasi sebelum SL
        recommended_leverage = math.floor(0.8 / stop_distance)
        if recommended_leverage > 20: recommended_leverage = 20 # Limit aman
        
        return {
            "pos_size_usd": pos_size,
            "leverage": recommended_leverage,
            "max_risk_usd": balance * (risk_percent / 100)
        }
