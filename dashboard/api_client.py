"""
CACAO INTELLIGENT — Client API
Toutes les fonctions d'appel HTTP vers l'API Flask.
Les pages n'appellent jamais requests directement — tout passe ici.
"""

import requests
import base64
from datetime import datetime
from config import ROUTES, API_TIMEOUT, LAT_DEFAUT, LON_DEFAUT

TIMEOUT_ESP32_MINUTES = 5  # ESP32 considere hors ligne apres 5 min sans donnees


# ============================================================
# FONCTIONS INTERNES
# ============================================================

def _get(route, params=None):
    """
    Requete GET vers l'API.
    Retourne (data, erreur).
    data  : dict JSON si succes  | None si erreur
    erreur: None si succes       | str message si erreur
    """
    try:
        r = requests.get(route, params=params, timeout=API_TIMEOUT)
        if r.status_code == 200:
            return r.json(), None
        return None, f"Erreur {r.status_code}"
    except requests.exceptions.ConnectionError:
        return None, "API hors ligne — lancez : python api/app.py"
    except requests.exceptions.Timeout:
        return None, f"API ne repond pas apres {API_TIMEOUT}s"
    except Exception as e:
        return None, str(e)


def _post(route, payload):
    """
    Requete POST JSON vers l'API.
    Retourne (data, erreur).
    """
    try:
        r = requests.post(route, json=payload, timeout=API_TIMEOUT)
        if r.status_code == 200:
            return r.json(), None
        return None, f"Erreur {r.status_code} : {r.text[:200]}"
    except requests.exceptions.ConnectionError:
        return None, "API hors ligne — lancez : python api/app.py"
    except requests.exceptions.Timeout:
        return None, f"API ne repond pas apres {API_TIMEOUT}s"
    except Exception as e:
        return None, str(e)


# ============================================================
# FONCTIONS PUBLIQUES
# ============================================================

def get_statut():
    """
    Statut de l'API et etat des modeles charges.
    Retourne :
    {
        "statut"  : "ok",
        "modeles" : { "irrigation": "charge", "pesticide": "charge", "maladie": "charge" },
        "sms"     : "actif"
    }
    """
    return _get(ROUTES["statut"])


def get_meteo(lat=LAT_DEFAUT, lon=LON_DEFAUT):
    """
    Meteo actuelle depuis OpenWeatherMap.
    Retourne :
    {
        "meteo": {
            "temperature", "humidite_air", "vitesse_vent",
            "pluie", "saison", "ville", "pluie_prevue_24h"
        }
    }
    """
    return _get(ROUTES["meteo"], params={"lat": lat, "lon": lon})


def get_derniere_lecture():
    """
    Derniere lecture enregistree par l'ESP32.
    Retourne disponible=False si aucune lecture
    ou si la derniere lecture date de plus de TIMEOUT_ESP32_MINUTES.
    """
    data, erreur = _get(ROUTES["derniere_lecture"])
    if erreur or not data:
        return None, erreur

    # Verifier que la lecture est recente
    if data.get("disponible") and data.get("lecture"):
        horodatage = data["lecture"].get("horodatage", "")
        if horodatage:
            try:
                derniere = datetime.fromisoformat(horodatage)
                delta    = (datetime.now() - derniere).total_seconds() / 60
                if delta > TIMEOUT_ESP32_MINUTES:
                    # Lecture trop ancienne — ESP32 considere hors ligne
                    return {"disponible": False, "lecture": {}}, None
            except Exception:
                pass  # horodatage non parsable -> on garde disponible tel quel

    return data, None


def decider(temperature, humidite_air, humidite_sol,
            vitesse_vent, pluie,
            maladie_detectee=None,
            lat=LAT_DEFAUT, lon=LON_DEFAUT):
    """
    Decision combinee : irrigation + pulverisation + gestion conflits.
    maladie_detectee : str optionnel — injecte depuis analyser_image()
    Retourne :
    {
        "action"          : "IRRIGUER" | "PULVERISER" | "ACTION_MANUELLE" | "AUCUNE_ACTION",
        "conflit"         : bool,
        "message_conflit" : str,
        "irrigation"      : { "decision", "confiance", "bloquee_par_pesticide", "bloquee_par_delai" },
        "pulverisation"   : { "decision", "confiance", "risques" },
        "maladie"         : { "detectee", "mode_risque", "frostypod", "message" },
        "contexte"        : { "saison", "pluie_prevue_24h", "pluie_prevue_3h" },
        "sms_envoye"      : bool
    }
    """
    payload = {
        "temperature"  : temperature,
        "humidite_air" : humidite_air,
        "humidite_sol" : humidite_sol,
        "vitesse_vent" : vitesse_vent,
        "pluie"        : pluie,
        "latitude"     : lat,
        "longitude"    : lon,
    }
    if maladie_detectee:
        payload["maladie_detectee"] = maladie_detectee

    return _post(ROUTES["decider"], payload)


def analyser_image(image_bytes, lat=LAT_DEFAUT, lon=LON_DEFAUT):
    """
    Analyse photo de cabosse via MobileNetV2 (82.7%).
    Encode l'image en base64 pour transport JSON.
    Retourne :
    {
        "detection_fiable" : bool,
        "maladie"          : "BLACKPOD" | "FROSTYPOD" | "HEALTHY" | "MIRID",
        "confiance"        : float,
        "probabilites"     : { "BLACKPOD": 87.3, ... },
        "action"           : str,
        "gravite"          : int 0-3,
        "sms_envoye"       : bool
    }
    """
    payload = {
        "image_base64" : base64.b64encode(image_bytes).decode("utf-8"),
        "latitude"     : lat,
        "longitude"    : lon,
    }
    return _post(ROUTES["analyser"], payload)


def tester_connexion():
    """
    Teste rapidement si l'API est joignable.
    Retourne (api_ok, sms_ok) — deux bool.
    """
    data, erreur = get_statut()
    if erreur or not data:
        return False, False
    return data.get("statut") == "ok", data.get("sms") == "actif"