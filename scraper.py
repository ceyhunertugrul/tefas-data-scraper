import requests
import json
import os

def fetch_tefas_data():
    url = "https://www.tefas.gov.tr/api/Teftas/GetFundMarketData"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        fonlar = []
        for item in data.get('data', []):
            fonlar.append({
                "kod": item['FundCode'],
                "isim": item['FundName'],
                "fiyat": item['Price'],
                "tarih": item['Date']
            })
            
        # Yapısal Düzeltme: data klasörü yoksa oluştur
        os.makedirs('data', exist_ok=True)
        
        with open('data/fon_verileri.json', 'w', encoding='utf-8') as f:
            json.dump(fonlar, f, ensure_ascii=False, indent=4)
            
        print("Veri başarıyla çekildi ve kaydedildi.")
        
    except Exception as e:
        print(f"Kritik Hata: {e}")
        exit(1) # Hata varsa GitHub Action'ı durdur

if __name__ == "__main__":
    fetch_tefas_data()
