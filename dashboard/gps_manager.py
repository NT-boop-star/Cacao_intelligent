"""
CACAO INTELLIGENT — GPS Manager
Gestion des coordonnees GPS parcelle et verification EUDR (deforestation).
"""
import os
import json
import requests
from datetime import datetime

_DIR = os.path.dirname(__file__)
_AGRICULT_JSON = os.path.join(_DIR, "agriculteurs.json")


# ============================================================
# LECTURE / ECRITURE agriculteurs.json
# ============================================================
def _charger_tous():
    if not os.path.exists(_AGRICULT_JSON):
        return {}
    with open(_AGRICULT_JSON, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}


def _sauver_tous(data):
    with open(_AGRICULT_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ============================================================
# 1. charger_profil
# ============================================================
def charger_profil(username):
    """Retourne le profil complet d'un agriculteur ou un dict vide."""
    tous = _charger_tous()
    return tous.get(username, {})


# ============================================================
# 2. sauvegarder_gps
# ============================================================
def sauvegarder_gps(username, latitude, longitude, superficie):
    """
    Met a jour les coordonnees GPS de la parcelle.
    Remet eudr.verifie a False quand le GPS change.
    """
    tous = _charger_tous()
    profil = tous.get(username, {})

    # Creer parcelle si absente
    if "parcelle" not in profil:
        profil["parcelle"] = {}

    profil["parcelle"]["latitude"] = latitude
    profil["parcelle"]["longitude"] = longitude
    profil["parcelle"]["superficie"] = superficie

    # Reset EUDR quand GPS change
    if "eudr" not in profil:
        profil["eudr"] = {}
    profil["eudr"]["verifie"] = False
    profil["eudr"]["statut"] = None
    profil["eudr"]["date_verification"] = None
    profil["eudr"]["source"] = None

    tous[username] = profil
    _sauver_tous(tous)


# ============================================================
# 3. sauvegarder_eudr
# ============================================================
def sauvegarder_eudr(username, statut, source):
    """
    Enregistre le resultat de la verification EUDR.
    statut : CONFORME | NON_CONFORME | INDETERMINE
    """
    tous = _charger_tous()
    profil = tous.get(username, {})

    if "eudr" not in profil:
        profil["eudr"] = {}

    profil["eudr"]["verifie"] = True
    profil["eudr"]["statut"] = statut
    profil["eudr"]["date_verification"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    profil["eudr"]["source"] = source

    tous[username] = profil
    _sauver_tous(tous)


# ============================================================
# 4. verifier_deforestation
# ============================================================
from dotenv import load_dotenv
load_dotenv()

_GFW_API_KEY = os.environ.get("GFW_API_KEY", "VOTRE_CLE_GFW")
_GFW_URL = "https://data-api.globalforestwatch.org/dataset/umd_tree_cover_loss/latest/query/json"


def verifier_deforestation(latitude, longitude):
    """
    Interroge l'API Global Forest Watch (Hansen UMD Tree Cover Loss)
    via POST avec un polygone GeoJSON de 0.05 deg autour du point.
    Filtre les lignes avec perte > 0.5 ha.
    Retourne un dict avec statut, source, detail, annees, api_ok.
    """
    source = "Global Forest Watch / Hansen GFC"

    # Bornes du carre de recherche
    lat_min = latitude - 0.05
    lat_max = latitude + 0.05
    lon_min = longitude - 0.05
    lon_max = longitude + 0.05

    # Polygone GeoJSON (sens anti-horaire, ferme)
    geometry = {
        "type": "Polygon",
        "coordinates": [[
            [lon_min, lat_min],
            [lon_max, lat_min],
            [lon_max, lat_max],
            [lon_min, lat_max],
            [lon_min, lat_min],
        ]]
    }

    headers = {
        "x-api-key": _GFW_API_KEY,
        "Origin": "localhost",
        "Content-Type": "application/json",
    }

    body = {
        "sql": (
            "SELECT umd_tree_cover_loss__year, SUM(umd_tree_cover_loss__ha) as area_ha "
            "FROM data "
            "WHERE umd_tree_cover_loss__year > 2020 "
            "GROUP BY umd_tree_cover_loss__year "
            "ORDER BY umd_tree_cover_loss__year"
        ),
        "geometry": geometry,
    }

    try:
        resp = requests.post(
            _GFW_URL,
            headers=headers,
            json=body,
            timeout=30,
            allow_redirects=True,
        )

        if resp.status_code == 200:
            data = resp.json()
            rows = data.get("data", [])

            # Filtrer : ne garder que les lignes avec perte > 0.5 ha
            rows = [r for r in rows if r.get("area_ha", 0) > 0.5]

            if not rows:
                return {
                    "statut": "CONFORME",
                    "source": source,
                    "detail": "Aucune perte forestiere significative detectee apres 2020 dans cette zone.",
                    "annees": [],
                    "api_ok": True,
                }

            annees = [r.get("umd_tree_cover_loss__year") for r in rows]
            total_ha = sum(r.get("area_ha", 0) for r in rows)
            detail = f"Perte de {total_ha:.2f} ha detectee apres 2020 (annees: {annees})."

            return {
                "statut": "NON_CONFORME",
                "source": source,
                "detail": detail,
                "annees": annees,
                "api_ok": True,
            }

        # API retourne un code non-200 : fallback
        return _fallback_geographique(latitude, longitude, source)

    except (requests.RequestException, ValueError, KeyError):
        return _fallback_geographique(latitude, longitude, source)


def _fallback_geographique(latitude, longitude, source):
    """
    Quand l'API GFW est indisponible, verification geographique simple.
    Zone cacaoyere ivoirienne : 4.0 N - 8.0 N / -9.0 W - -2.0 W
    """
    dans_zone = (4.0 <= latitude <= 8.0) and (-9.0 <= longitude <= -2.0)

    if dans_zone:
        return {
            "statut": "CONFORME",
            "source": source + " (fallback geographique)",
            "detail": (
                "API Global Forest Watch indisponible. "
                "Les coordonnees sont dans la zone cacaoyere ivoirienne. "
                "Statut provisoire : CONFORME. "
                "Une verification complete sera necessaire."
            ),
            "annees": [],
            "api_ok": False,
        }

    return {
        "statut": "INDETERMINE",
        "source": source + " (fallback geographique)",
        "detail": (
            "API Global Forest Watch indisponible. "
            "Les coordonnees sont hors de la zone cacaoyere ivoirienne standard. "
            "Verification manuelle necessaire."
        ),
        "annees": [],
        "api_ok": False,
    }
