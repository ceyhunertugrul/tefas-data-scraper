import json
import os
import pandas as pd
from datetime import datetime, timedelta
from tefas import Crawler

def fetch_latest_tefas_data():
    tefas = Crawler(fund_limit=2000)
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7) 
    
    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")
    
    try:
        print(f"Yatırım ve BES fonları çekiliyor: {start_str} - {end_str}")
        
        # 1. Standart YAT ve EMK Fonları (Toplu Çekim)
        df_yatirim = tefas.fetch(start=start_str, end=end_str, kind="YAT")
        df_emeklilik = tefas.fetch(start=start_str, end=end_str, kind="EMK")
        
        # 2. OKS Fonları İçin Bypass (Manuel İsimle Çekim)
        # tefas-crawler 'OKS' kind parametresini desteklemediği için OKS fonlarını ismen zorla çekiyoruz.
        oks_fonlari = ["AER", "CHG", "AJR", "AMR", "BHR", "VEO"] # Yaygın OKS fonları
        df_oks_list = []
        
        for kod in oks_fonlari:
            try:
                df_ozel = tefas.fetch(start=start_str, end=end_str, name=kod)
                if df_ozel is not None and not df_ozel.empty:
                    df_oks_list.append(df_ozel)
            except Exception as e:
                print(f"Uyarı: {kod} fonu çekilemedi - {e}")
                
        # 3. Verileri Birleştirme
        frames = []
        if df_yatirim is not None and not df_yatirim.empty:
            frames.append(df_yatirim)
        if df_emeklilik is not None and not df_emeklilik.empty:
            frames.append(df_emeklilik)
            
        frames.extend(df_oks_list)
        
        if not frames:
            raise ValueError("TEFAS'tan hiçbir veri alınamadı.")
            
        df = pd.concat(frames, ignore_index=True)
        
        # En güncel tarihi üste al ve fon kodu tekrar edenleri (eski tarihleri) at
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
            
        print(f"Başarılı: Toplam {len(fonlar)} adet fon (YAT + EMK + OKS) kaydedildi.")
        
    except Exception as e:
        print(f"Kritik Hata: {e}")
        exit(1)

if __name__ == "__main__":
    fetch_latest_tefas_data()
