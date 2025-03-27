#!/usr/bin/env python3
import requests
import os
import csv
from datetime import datetime

# Configuration
API_KEY = os.getenv('FRED_API_KEY', 'd271ac317f11acb5bcb553e96070ea0e')  # Votre clé
BASE_URL = "https://api.stlouisfed.org/fred"
SERIES = {
    'UNRATE': 'Taux de chômage US',
    'GDP': 'Produit Intérieur Brut',
    'CPIAUCSL': 'Indice des prix à la consommation'
}
OUTPUT_FILE = "fred_data.csv"

def get_fred_data(series_id):
    """Récupère les données d'une série FRED"""
    url = f"{BASE_URL}/series/observations"
    params = {
        'series_id': series_id,
        'api_key': API_KEY,
        'file_type': 'json',
        'observation_start': '2024-01-01',
        'sort_order': 'desc'
    }
    
    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        if 'observations' not in data:
            print(f"Structure inattendue pour {series_id}: {data.get('error_message', 'Pas de données')}")
            return None
            
        return {
            'id': series_id,
            'title': SERIES[series_id],
            'unit': 'Percent' if series_id == 'UNRATE' else 'USD',
            'data': [(obs['date'], obs['value']) for obs in data['observations']]
        }
    except Exception as e:
        print(f"Erreur {series_id}: {str(e)}")
        return None

def save_to_csv(data):
    """Sauvegarde les données en CSV"""
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Series ID', 'Title', 'Date', 'Value', 'Unit'])
        
        for series in data:
            for date, value in series['data']:
                writer.writerow([
                    series['id'],
                    series['title'],
                    date,
                    value,
                    series['unit']
                ])

if __name__ == "__main__":
    print("Récupération des données FRED...")
    all_data = []
    
    for series_id in SERIES.keys():
        series_data = get_fred_data(series_id)
        if series_data:
            all_data.append(series_data)
    
    if all_data:
        save_to_csv(all_data)
        print(f"✅ Données sauvegardées dans {OUTPUT_FILE}")
        print(f"Exemple de données :")
        with open(OUTPUT_FILE, 'r') as f:
            print(''.join(f.readlines()[:5]))  # Affiche les 5 premières lignes
    else:
        print("❌ Aucune donnée valide récupérée")

    # Vérification de la clé API
    print("\nVérification de la clé API...")
    test_url = f"{BASE_URL}/series?series_id=UNRATE&api_key={API_KEY}"
    test_res = requests.get(test_url)
    print(f"Statut de test : {test_res.status_code}")
    if test_res.status_code == 403:
        print("ERREUR : Clé API invalide ou désactivée")
