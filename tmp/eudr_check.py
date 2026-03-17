import json, os, sys
from pathlib import Path

# Load agriculteurs.json
base = Path(r'C:/Users/netha/Downloads/cacao_intelligent/dashboard')
with open(base/'agriculteurs.json', encoding='utf-8') as f:
    data = json.load(f)

# Add project path for import
sys.path.append(str(base))
import gps_manager

non_conforme = []
for username, profil in data.items():
    parcelle = profil.get('parcelle')
    if not parcelle:
        continue
    lat = parcelle.get('latitude')
    lon = parcelle.get('longitude')
    # Verify deforestation
    res = gps_manager.verifier_deforestation(lat, lon)
    if res.get('statut') == 'NON_CONFORME':
        non_conforme.append({
            'username': username,
            'latitude': lat,
            'longitude': lon,
            'detail': res.get('detail'),
            'source': res.get('source')
        })

print(json.dumps(non_conforme, ensure_ascii=False, indent=2))
