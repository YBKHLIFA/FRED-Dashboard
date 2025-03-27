#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime

# Configuration
URL = "https://tradingeconomics.com/calendar"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    'Accept-Language': 'en-US,en;q=0.9'
}
OUTPUT_FILE = "economic_data.csv"

def fetch_data():
    """Récupère les données du calendrier économique"""
    try:
        response = requests.get(URL, headers=HEADERS, timeout=30)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Erreur de requête : {str(e)}")
        return None

def parse_html(html):
    """Extrait les données du HTML"""
    if not html:
        return None
        
    soup = BeautifulSoup(html, 'html.parser')
    events = []
    
    for row in soup.select('tr[data-url*="/calendar/"]'):
        try:
            time = row.select_one('td:nth-child(1)').get_text(strip=True)
            country = row.select_one('td:nth-child(2)').get_text(strip=True)
            event = row.select_one('td:nth-child(3) a').get_text(strip=True)
            actual = row.select_one('td:nth-child(5)').get_text(strip=True)
            forecast = row.select_one('td:nth-child(6)').get_text(strip=True)
            
            events.append({
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'time': time,
                'country': country,
                'event': event,
                'actual': actual,
                'forecast': forecast
            })
        except Exception as e:
            print(f"Erreur parsing : {str(e)}")
            continue
            
    return events

def save_to_csv(data):
    """Sauvegarde en CSV"""
    if not data:
        return
        
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Timestamp', 'Time', 'Country', 'Event', 'Actual', 'Forecast'])
        
        for event in data:
            writer.writerow([
                event['timestamp'],
                event['time'],
                event['country'],
                event['event'],
                event['actual'],
                event['forecast']
            ])

if __name__ == "__main__":
    print("Début du scraping...")
    html = fetch_data()
    
    if html:
        events = parse_html(html)
        if events:
            save_to_csv(events)
            print(f"✅ {len(events)} événements sauvegardés dans {OUTPUT_FILE}")
        else:
            print("❌ Aucun événement trouvé")
    else:
        print("❌ Échec de la récupération des données")
