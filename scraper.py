import json
import os
import pandas as pd
from datetime import datetime, timedelta
from tefas import Crawler

def fetch_latest_tefas_data():
    # Varsayılan 50 limitini kaldırıp 2000'e yükseltiyoruz
    tefas = Crawler(fund_limit=2000)
    
    # Yabancı fon fiyatlarındaki (T+1/T+2) değerleme gecikmelerini de yakalamak için 7 gün geriye gidiyoruz
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7) 
    
    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")
    
    try:
        print(f"Yatırım ve BES fonları çekiliyor: {start_str} - {end_str}")
        
        # 1. Yatırım Fonlarını Çek (YAT)
        df_yatirim = tefas.fetch(start=start_str, end=end_str, kind="YAT")
        
        # 2. BES / Emeklilik Fonlarını Çek (EMK)
        df_emeklilik = tefas.fetch(start=start_str, end=end_str, kind="EMK")
        
        # Çekilen verileri birleştir
        frames = []
        if df_yatirim is not None and not df_yatirim.empty:
            frames.append(df_yatirim)
        if df_emeklilik is not None and not df_emeklilik.empty:
            frames.append(df_emeklilik)
            
        if not frames:
            raise ValueError("TEFAS'tan hiçbir veri alınamadı.")
            
        df = pd.concat(frames, ignore_index=True)
        
        # Tarihe göre azalan sırala ve fon koduna göre tekrar edenleri at (en güncel tarihli veri kalır)
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
            
        print(f"Başarılı: Toplam {len(fonlar)} adet fon (Yatırım + BES) kaydedildi.")
        
    except Exception as e:
        print(f"Kritik Hata: {e}")
        exit(1)

if __name__ == "__main__":
    fetch_latest_tefas_data()
