import json
import os
from datetime import datetime, timedelta
from tefas import Crawler

def fetch_latest_tefas_data():
    tefas = Crawler()
    
    # Hafta sonu ve resmi tatil risklerine karşı son 5 iş gününün verisini çekiyoruz
    end_date = datetime.now()
    start_date = end_date - timedelta(days=5)
    
    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")
    
    try:
        print(f"TEFAS verisi çekiliyor: {start_str} - {end_str}")
        df = tefas.fetch(start=start_str, end=end_str)
        
        if df is None or df.empty:
            raise ValueError("TEFAS'tan veri alınamadı veya tablo boş.")
        
        # En güncel fiyata ulaşmak için tarihe göre azalan sıralama yapıp, 
        # fon koduna göre tekrar edenleri siliyoruz (sadece ilk yani en güncel satır kalıyor)
        df = df.sort_values(by='date', ascending=False)
        latest_data = df.drop_duplicates(subset='code', keep='first')
        
        fonlar = []
        for index, row in latest_data.iterrows():
            fonlar.append({
                "kod": row['code'],
                "isim": row.get('title', ''),
                "fiyat": row['price'],
                "tarih": str(row['date'])
            })
            
        os.makedirs('data', exist_ok=True)
        
        with open('data/fon_verileri.json', 'w', encoding='utf-8') as f:
            json.dump(fonlar, f, ensure_ascii=False, indent=4)
            
        print(f"Başarılı: {len(fonlar)} adet güncel fon fiyatı kaydedildi.")
        
    except Exception as e:
        print(f"Kritik Hata: {e}")
        exit(1)

if __name__ == "__main__":
    fetch_latest_tefas_data()
