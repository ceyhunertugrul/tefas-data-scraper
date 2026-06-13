import requests
import json
import pandas as pd

def fetch_tefas_data():
    # TEFAS'ın güncel verilerini barındıran API uç noktası
    url = "https://www.tefas.gov.tr/api/Teftas/GetFundMarketData"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        # Gelen veriyi işleyelim: Sadece kod, isim ve fiyatı alalım
        # TEFAS API yanıtı "data" anahtarı altında listeler sunar
        fonlar = []
        for item in data.get('data', []):
            fonlar.append({
                "kod": item['FundCode'],
                "isim": item['FundName'],
                "fiyat": item['Price'],
                "tarih": item['Date']
            })
            
        # JSON olarak kaydet
        with open('data/fon_verileri.json', 'w', encoding='utf-8') as f:
            json.dump(fonlar, f, ensure_ascii=False, indent=4)
            
        print("Veri başarıyla güncellendi.")
        
    except Exception as e:
        print(f"Hata oluştu: {e}")

if __name__ == "__main__":
    fetch_tefas_data()
