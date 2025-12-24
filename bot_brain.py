def get_volume_profile(self, df, bins=50):
        # Memastikan data Close dan Volume adalah 1D
        close_data = df['Close'].squeeze()
        volume_data = df['Volume'].squeeze()
        
        price_min = close_data.min()
        price_max = close_data.max()
        
        bins_edges = np.linspace(price_min, price_max, bins)
        # Menggunakan data yang sudah di-squeeze
        v_profile = df.groupby(pd.cut(close_data, bins=bins_edges))[volume_data.name].sum()
        
        poc_price = v_profile.idxmax().mid
        return poc_price, v_profile
