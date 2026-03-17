import requests

import os
from dotenv import load_dotenv

load_dotenv()
# ⚠️ Remplace par ta vraie clé API (via variable d'environnement)
API_KEY = os.environ.get("OPENWEATHER_API_KEY", "VOTRE_CLE_METEO")

VILLE = "Abidjan"
PAYS = "CI"


def get_meteo_actuelle():
    """
    Appelle OpenWeatherMap et retourne les données
    météo actuelles d'Abidjan sous forme de dictionnaire
    """

    # Construction de l'URL avec les paramètres
    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?q={VILLE},{PAYS}"
        f"&appid={API_KEY}"
        f"&units=metric"
        f"&lang=fr"
    )

    # Envoi de la requête vers l'API
    reponse = requests.get(url)

    # 200 = succès, autre code = erreur
    if reponse.status_code == 200:

        # Conversion de la réponse JSON en dictionnaire Python
        donnees = reponse.json()

        # On extrait uniquement les données utiles pour notre IA
        meteo = {
            "ville"        : donnees["name"],
            "temperature"  : donnees["main"]["temp"],
            "humidite_air" : donnees["main"]["humidity"],
            "description"  : donnees["weather"][0]["description"],
            "vitesse_vent" : donnees["wind"]["speed"],
            "pluie"        : donnees.get("rain", {}).get("1h", 0)
        }

        return meteo

    else:
        print(f"Erreur API : code {reponse.status_code}")
        return None


# Ce bloc s'exécute uniquement si tu lances ce fichier directement
if __name__ == "__main__":
    print(" Récupération météo en cours...")
    resultat = get_meteo_actuelle()

    if resultat:
        print("\n Météo actuelle à Abidjan :")
        for cle, valeur in resultat.items():
            print(f"   {cle:15} : {valeur}")