import pickle
import requests
import pandas as pd
import numpy as np
from flask import Flask, request, jsonify
from datetime import datetime
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import sys
import io
import base64
from PIL import Image

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = Flask(__name__)

# -- CONFIGURATION --------------------------------------------
from dotenv import load_dotenv
load_dotenv()

API_KEY_METEO         = os.environ.get("OPENWEATHER_API_KEY", "VOTRE_CLE_METEO")
LAT_DEFAUT            = 5.3096
LON_DEFAUT            = -4.0126
DELAI_PULVERISATION_H = 48

CHEMIN_MODELE_IRRIGATION = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "model", "modele_irrigation.pkl"
)
CHEMIN_MODELE_PESTICIDE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "model", "modele_pesticide.pkl"
)
CHEMIN_MODELE_MALADIE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "model", "modele_maladie.keras"
)

IMG_SIZE        = 224
SEUIL_CONFIANCE = 0.60
CLASSES_MALADIE = ["BLACKPOD", "FROSTYPOD", "HEALTHY", "MIRID"]

MESSAGES_MALADIE = {
    "HEALTHY"   : {
        "statut"  : "Cabosse saine",
        "action"  : "Aucun traitement necessaire",
        "gravite" : 0,
        "source"  : "Detection visuelle MobileNetV2"
    },
    "BLACKPOD"  : {
        "statut"  : "Pourriture brune (Phytophthora palmivora)",
        "action"  : "Pulveriser fongicide dans les 24h",
        "gravite" : 3,
        "source"  : "Cahiers Agricultures 2024 / Yara CI"
    },
    "FROSTYPOD" : {
        "statut"  : "Moniliose (Moniliophthora roreri)",
        "action"  : "Retirer et bruler les cabosses atteintes",
        "gravite" : 2,
        "source"  : "ICCO / FAO"
    },
    "MIRID"     : {
        "statut"  : "Attaque mirides (insectes capsides)",
        "action"  : "Pulveriser insecticide si conditions meteo OK",
        "gravite" : 2,
        "source"  : "Diallo 2023 / IRD"
    }
}

# Dict borne : max 500 entrees, les plus anciennes sont supprimees automatiquement
MAX_HISTORIQUE = 500
historique_pulverisation = OrderedDict()

# Derniere lecture ESP32 — mise a jour par /predire, /pulveriser, /decider
derniere_lecture = {}

# -- IMPORT MODULE SMS ----------------------------------------
try:
    from sms import (
        sms_maladie_detectee,
        sms_irrigation,
        sms_pulverisation,
        sms_frostypod,
        sms_conflit
    )
    SMS_DISPONIBLE = True
    print("Module SMS charge avec succes")
except Exception as e:
    SMS_DISPONIBLE = False
    print(f"Module SMS non charge : {e}")


# -- FONCTIONS UTILITAIRES ------------------------------------

def get_saison(mois):
    if mois in [11, 12, 1, 2, 3]: return 0
    elif mois in [4, 5, 6, 7]:    return 1
    elif mois in [8, 9]:           return 2
    else:                          return 3

def get_nom_saison(code):
    return {
        0: "Grande saison seche",
        1: "Grande saison des pluies",
        2: "Petite saison seche",
        3: "Petite saison des pluies"
    }[code]

def charger_modele_pkl(chemin, nom):
    try:
        with open(chemin, "rb") as f:
            modele = pickle.load(f)
        print(f"Modele {nom} charge avec succes")
        return modele
    except FileNotFoundError:
        print(f"Erreur : modele {nom} introuvable a {chemin}")
        return None

def get_pluie_prevue_24h(lat, lon):
    try:
        url = (f"https://api.openweathermap.org/data/2.5/forecast"
               f"?lat={lat}&lon={lon}&appid={API_KEY_METEO}&units=metric&cnt=8")
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            for p in r.json()["list"]:
                if p.get("rain", {}).get("3h", 0) >= 2: return 1
            return 0
        return 0
    except: return 0

def get_pluie_prevue_3h(lat, lon):
    try:
        url = (f"https://api.openweathermap.org/data/2.5/forecast"
               f"?lat={lat}&lon={lon}&appid={API_KEY_METEO}&units=metric&cnt=1")
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            return 1 if r.json()["list"][0].get("rain", {}).get("3h", 0) >= 2 else 0
        return 0
    except: return 0


def get_meteo_parallele(lat, lon, need_24h=True, need_3h=True, need_meteo=False):
    """
    Execute les appels meteo en parallele au lieu de sequentiel.
    Reduit la latence de 15s max a 5s max.
    """
    resultats = {"pluie_prevue_24h": 0, "pluie_prevue_3h": 0, "meteo": None}
    taches = {}
    with ThreadPoolExecutor(max_workers=3) as executor:
        if need_24h:
            taches[executor.submit(get_pluie_prevue_24h, lat, lon)] = "pluie_prevue_24h"
        if need_3h:
            taches[executor.submit(get_pluie_prevue_3h, lat, lon)] = "pluie_prevue_3h"
        if need_meteo:
            taches[executor.submit(get_meteo_coordonnees, lat, lon)] = "meteo"
        for future in as_completed(taches):
            cle = taches[future]
            try:
                resultats[cle] = future.result()
            except Exception:
                pass
    return resultats

def get_meteo_coordonnees(lat, lon):
    try:
        url = (f"https://api.openweathermap.org/data/2.5/weather"
               f"?lat={lat}&lon={lon}&appid={API_KEY_METEO}&units=metric&lang=fr")
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            d = r.json()
            return {
                "temperature"  : d["main"]["temp"],
                "humidite_air" : d["main"]["humidity"],
                "vitesse_vent" : d["wind"]["speed"] * 3.6,
                "description"  : d["weather"][0]["description"],
                "pluie"        : d.get("rain", {}).get("1h", 0),
                "ville"        : d.get("name", "Inconnue")
            }
        return None
    except: return None

def get_risques_maladies(saison, humidite_air):
    return int(saison in [1, 3] and humidite_air > 75), int(saison in [0, 2])

def cle_parcelle(lat, lon):
    return f"{round(lat, 4)}_{round(lon, 4)}"

def enregistrer_pulverisation(lat, lon):
    cle = cle_parcelle(lat, lon)
    # Si la cle existe deja, la supprimer pour la remettre en fin (MRU)
    if cle in historique_pulverisation:
        del historique_pulverisation[cle]
    historique_pulverisation[cle] = datetime.now()
    # Nettoyer les entrees trop anciennes (> 48h) et limiter la taille
    maintenant = datetime.now()
    cles_a_supprimer = [
        k for k, v in historique_pulverisation.items()
        if (maintenant - v).total_seconds() / 3600 > DELAI_PULVERISATION_H
    ]
    for k in cles_a_supprimer:
        del historique_pulverisation[k]
    # Securite : limiter la taille max
    while len(historique_pulverisation) > MAX_HISTORIQUE:
        historique_pulverisation.popitem(last=False)

def heures_depuis_pulverisation(lat, lon):
    cle = cle_parcelle(lat, lon)
    if cle not in historique_pulverisation: return None
    return (datetime.now() - historique_pulverisation[cle]).total_seconds() / 3600

def preparer_image_depuis_bytes(image_bytes):
    with Image.open(io.BytesIO(image_bytes)) as img:
        img_rgb   = img.convert("RGB").resize((IMG_SIZE, IMG_SIZE))
    img_array = np.array(img_rgb, dtype=np.float32)
    img_array /= 255.0  # Normalisation in-place, evite une copie
    return img_array[np.newaxis, ...]  # Equivalent a expand_dims sans copie


# -- CHARGEMENT DES MODELES ----------------------------------
modele_irrigation = charger_modele_pkl(CHEMIN_MODELE_IRRIGATION, "irrigation")
modele_pesticide  = charger_modele_pkl(CHEMIN_MODELE_PESTICIDE,  "pesticide")

try:
    from tensorflow.keras.models import load_model
    modele_maladie = load_model(CHEMIN_MODELE_MALADIE)
    print("Modele maladie charge avec succes")
except Exception as e:
    modele_maladie = None
    print(f"Modele maladie non charge : {e}")


# -- ROUTES --------------------------------------------------

@app.route("/", methods=["GET"])
def accueil():
    mois = datetime.now().month
    return jsonify({
        "statut"          : "ok",
        "message"         : "API Cacao Intelligent operationnelle",
        "version"         : "v6",
        "modeles"         : {
            "irrigation" : "charge" if modele_irrigation else "non charge",
            "pesticide"  : "charge" if modele_pesticide  else "non charge",
            "maladie"    : "charge" if modele_maladie    else "non charge",
        },
        "sms"             : "actif" if SMS_DISPONIBLE else "inactif",
        "contexte_actuel" : {
            "mois"        : mois,
            "saison"      : get_nom_saison(get_saison(mois)),
            "zone_defaut" : {"ville": "Abidjan", "latitude": LAT_DEFAUT, "longitude": LON_DEFAUT}
        },
        "routes" : {
            "GET  /"           : "verification statut API",
            "GET  /meteo"      : "meteo actuelle (optionnel: ?lat=&lon=)",
            "POST /predire"    : "decision irrigation uniquement",
            "POST /pulveriser" : "decision pulverisation uniquement",
            "POST /decider"    : "decision combinee avec gestion conflits",
            "POST /analyser"   : "analyse photo cabosse smartphone"
        }
    })


@app.route("/meteo", methods=["GET"])
def get_meteo():
    lat   = request.args.get("lat", LAT_DEFAUT, type=float)
    lon   = request.args.get("lon", LON_DEFAUT, type=float)
    meteo = get_meteo_coordonnees(lat, lon)
    if meteo:
        mois = datetime.now().month
        # Appels meteo en parallele (optimisation latence)
        previsions = get_meteo_parallele(lat, lon, need_24h=True, need_3h=True)
        meteo.update({
            "pluie_prevue_24h" : previsions["pluie_prevue_24h"],
            "pluie_prevue_3h"  : previsions["pluie_prevue_3h"],
            "mois"             : mois,
            "saison"           : get_nom_saison(get_saison(mois)),
            "latitude"         : lat,
            "longitude"        : lon
        })
        return jsonify({"statut": "ok", "meteo": meteo})
    return jsonify({"statut": "erreur", "message": "Impossible de recuperer la meteo"}), 500


@app.route("/predire", methods=["POST"])
def predire():
    if modele_irrigation is None:
        return jsonify({"statut": "erreur", "message": "Modele irrigation non charge"}), 500
    donnees = request.get_json()
    for champ in ["temperature", "humidite_air", "humidite_sol", "vitesse_vent", "pluie"]:
        if champ not in donnees:
            return jsonify({"statut": "erreur", "message": f"Champ manquant : {champ}"}), 400

    lat          = donnees.get("latitude",  LAT_DEFAUT)
    lon          = donnees.get("longitude", LON_DEFAUT)
    mois         = datetime.now().month
    saison       = get_saison(mois)
    previsions   = get_meteo_parallele(lat, lon, need_24h=True, need_3h=False)
    pluie_prevue = previsions["pluie_prevue_24h"]

    heures = heures_depuis_pulverisation(lat, lon)
    if heures is not None and heures < DELAI_PULVERISATION_H:
        heures_restantes = int(DELAI_PULVERISATION_H - heures)
        return jsonify({
            "statut"                          : "ok",
            "decision"                        : 0,
            "confiance"                       : 100.0,
            "message"                         : (f"Irrigation bloquee — pulverisation il y a {int(heures)}h. "
                                                  f"Attendre encore {heures_restantes}h."),
            "irrigation_bloquee_par_pesticide": True,
            "heures_restantes"                : heures_restantes,
            "sms_envoye"                      : False,
            "contexte"                        : {
                "mois": mois, "saison": get_nom_saison(saison),
                "pluie_prevue": pluie_prevue, "latitude": lat, "longitude": lon
            }
        })

    donnees_ia = pd.DataFrame([{
        "mois": mois, "saison": saison,
        "temperature": donnees["temperature"], "humidite_air": donnees["humidite_air"],
        "humidite_sol": donnees["humidite_sol"], "vitesse_vent": donnees["vitesse_vent"],
        "pluie": donnees["pluie"], "pluie_prevue": pluie_prevue
    }])
    # Optimisation : un seul appel predict_proba au lieu de predict + predict_proba
    proba_irr   = modele_irrigation.predict_proba(donnees_ia)[0]
    decision    = int(np.argmax(proba_irr))
    probabilite = float(proba_irr[decision])

    if decision == 1:             message = "Irrigation recommandee — activer la pompe"
    elif pluie_prevue:            message = "Pas d'irrigation — pluie prevue dans 24h"
    elif donnees["pluie"] >= 2:   message = "Pas d'irrigation — pluie en cours"
    else:                         message = "Pas d'irrigation — conditions optimales"

    sms_envoye = False
    if SMS_DISPONIBLE and decision == 1:
        sms_envoye = sms_irrigation(
            decision=1, confiance=round(probabilite*100,1),
            humidite_sol=donnees["humidite_sol"], saison=get_nom_saison(saison)
        )

    # Sauvegarder la derniere lecture ESP32
    derniere_lecture.update({
        "temperature"  : donnees["temperature"],
        "humidite_air" : donnees["humidite_air"],
        "humidite_sol" : donnees["humidite_sol"],
        "vitesse_vent" : donnees["vitesse_vent"],
        "pluie"        : donnees["pluie"],
        "horodatage"   : datetime.now().strftime("%H:%M:%S"),
        "source"       : "ESP32"
    })

    return jsonify({
        "statut": "ok", "decision": decision, "message": message,
        "confiance": round(probabilite*100,1), "sms_envoye": sms_envoye,
        "contexte": {"mois": mois, "saison": get_nom_saison(saison),
                     "pluie_prevue": pluie_prevue, "latitude": lat, "longitude": lon}
    })


@app.route("/pulveriser", methods=["POST"])
def pulveriser():
    if modele_pesticide is None:
        return jsonify({"statut": "erreur", "message": "Modele pesticide non charge"}), 500
    donnees = request.get_json()
    for champ in ["temperature", "humidite_air", "vitesse_vent", "pluie"]:
        if champ not in donnees:
            return jsonify({"statut": "erreur", "message": f"Champ manquant : {champ}"}), 400

    lat             = donnees.get("latitude",  LAT_DEFAUT)
    lon             = donnees.get("longitude", LON_DEFAUT)
    mois            = datetime.now().month
    saison          = get_saison(mois)
    previsions      = get_meteo_parallele(lat, lon, need_24h=False, need_3h=True)
    pluie_prevue_3h = previsions["pluie_prevue_3h"]
    risque_pourriture, risque_mirides = get_risques_maladies(saison, donnees["humidite_air"])

    donnees_ia = pd.DataFrame([{
        "mois": mois, "saison": saison,
        "temperature": donnees["temperature"], "humidite_air": donnees["humidite_air"],
        "vitesse_vent": donnees["vitesse_vent"], "pluie": donnees["pluie"],
        "pluie_prevue_3h": pluie_prevue_3h,
        "risque_pourriture_brune": risque_pourriture, "risque_mirides": risque_mirides
    }])
    # Optimisation : un seul appel predict_proba
    proba_pest  = modele_pesticide.predict_proba(donnees_ia)[0]
    decision    = int(np.argmax(proba_pest))
    probabilite = float(proba_pest[decision])

    if decision == 1:
        enregistrer_pulverisation(lat, lon)
        message = "Pulverisation recommandee — activer le pulverisateur"
    elif donnees["pluie"] > 0:          message = "Pas de pulverisation — pluie en cours"
    elif pluie_prevue_3h:               message = "Pas de pulverisation — pluie prevue dans 3h"
    elif donnees["vitesse_vent"] >= 12: message = "Pas de pulverisation — vent trop fort"
    elif donnees["temperature"] >= 30:  message = "Pas de pulverisation — temperature trop elevee"
    elif donnees["humidite_air"] < 60:  message = "Pas de pulverisation — humidite trop basse"
    else:                               message = "Pas de pulverisation — conditions non reunies"

    sms_envoye = False
    if SMS_DISPONIBLE and decision == 1:
        sms_envoye = sms_pulverisation(
            decision=1, confiance=round(probabilite*100,1), saison=get_nom_saison(saison)
        )

    # Sauvegarder la derniere lecture ESP32
    derniere_lecture.update({
        "temperature"  : donnees["temperature"],
        "humidite_air" : donnees["humidite_air"],
        "humidite_sol" : donnees.get("humidite_sol", None),
        "vitesse_vent" : donnees["vitesse_vent"],
        "pluie"        : donnees["pluie"],
        "horodatage"   : datetime.now().strftime("%H:%M:%S"),
        "source"       : "ESP32"
    })

    return jsonify({
        "statut": "ok", "decision": decision, "message": message,
        "confiance": round(probabilite*100,1), "sms_envoye": sms_envoye,
        "risques": {"pourriture_brune": risque_pourriture, "mirides": risque_mirides},
        "contexte": {"mois": mois, "saison": get_nom_saison(saison),
                     "pluie_prevue_3h": pluie_prevue_3h, "latitude": lat, "longitude": lon}
    })


@app.route("/decider", methods=["POST"])
def decider():
    """
    Route principale ESP32.
    MODE AUTOMATIQUE : risques calcules depuis saison CI (sans photo).
    MODE MANUEL      : maladie_detectee envoyee depuis /analyser.
    FROSTYPOD        : action manuelle, pas de pulverisation chimique. (ICCO/FAO)
    PRIORITE         : pulverisation > irrigation.
    DELAI            : 48h apres pulverisation avant irrigation. (CCHST)
    """
    if modele_irrigation is None or modele_pesticide is None:
        return jsonify({"statut": "erreur", "message": "Un ou plusieurs modeles non charges"}), 500
    donnees = request.get_json()
    for champ in ["temperature", "humidite_air", "humidite_sol", "vitesse_vent", "pluie"]:
        if champ not in donnees:
            return jsonify({"statut": "erreur", "message": f"Champ manquant : {champ}"}), 400

    lat              = donnees.get("latitude",  LAT_DEFAUT)
    lon              = donnees.get("longitude", LON_DEFAUT)
    mois             = datetime.now().month
    saison           = get_saison(mois)
    maladie_detectee = donnees.get("maladie_detectee", None)
    # Appels meteo en parallele (optimisation latence 15s -> 5s)
    previsions       = get_meteo_parallele(lat, lon, need_24h=True, need_3h=True)
    pluie_prevue_24h = previsions["pluie_prevue_24h"]
    pluie_prevue_3h  = previsions["pluie_prevue_3h"]

    # ============================================================
    # CALCUL RISQUES MALADIES
    # ============================================================
    message_frostypod = None
    frostypod_detecte = False
    mode_risque       = "automatique"

    if maladie_detectee == "BLACKPOD":
        risque_pourriture, risque_mirides = 1, 0
        mode_risque = "visuel — BLACKPOD confirme"
    elif maladie_detectee == "MIRID":
        risque_pourriture, risque_mirides = 0, 1
        mode_risque = "visuel — MIRID confirme"
    elif maladie_detectee == "FROSTYPOD":
        risque_pourriture, risque_mirides = 0, 0
        frostypod_detecte = True
        mode_risque       = "visuel — FROSTYPOD confirme"
        message_frostypod = ("FROSTYPOD detecte — Action manuelle requise : "
                             "retirer et bruler les cabosses atteintes immediatement. "
                             "Aucune pulverisation chimique efficace contre "
                             "Moniliophthora roreri. Source : ICCO / FAO")
    elif maladie_detectee == "HEALTHY":
        risque_pourriture, risque_mirides = get_risques_maladies(saison, donnees["humidite_air"])
        mode_risque = "automatique — cabosse saine confirmee"
    else:
        risque_pourriture, risque_mirides = get_risques_maladies(saison, donnees["humidite_air"])
        mode_risque = "automatique — saison CI"

    # ============================================================
    # DECISION IRRIGATION
    # ============================================================
    di = pd.DataFrame([{
        "mois": mois, "saison": saison,
        "temperature": donnees["temperature"], "humidite_air": donnees["humidite_air"],
        "humidite_sol": donnees["humidite_sol"], "vitesse_vent": donnees["vitesse_vent"],
        "pluie": donnees["pluie"], "pluie_prevue": pluie_prevue_24h
    }])
    # Optimisation : un seul appel predict_proba
    proba_irr       = modele_irrigation.predict_proba(di)[0]
    dec_irrigation  = int(np.argmax(proba_irr))
    conf_irrigation = float(proba_irr[dec_irrigation])

    # ============================================================
    # DECISION PULVERISATION
    # ============================================================
    if frostypod_detecte:
        dec_pesticide, conf_pesticide = 0, 100.0
    else:
        dp = pd.DataFrame([{
            "mois": mois, "saison": saison,
            "temperature": donnees["temperature"], "humidite_air": donnees["humidite_air"],
            "vitesse_vent": donnees["vitesse_vent"], "pluie": donnees["pluie"],
            "pluie_prevue_3h": pluie_prevue_3h,
            "risque_pourriture_brune": risque_pourriture, "risque_mirides": risque_mirides
        }])
        # Optimisation : un seul appel predict_proba
        proba_pest     = modele_pesticide.predict_proba(dp)[0]
        dec_pesticide  = int(np.argmax(proba_pest))
        conf_pesticide = float(proba_pest[dec_pesticide])

        # REGLE METIER : maladie visuellement confirmee = pulverisation forcee
        # Une confirmation visuelle BLACKPOD ou MIRID est plus fiable
        # que les conditions meteo seules. Source : ICCO / Cahiers Agricultures 2024
        if maladie_detectee in ["BLACKPOD", "MIRID"] and dec_pesticide == 0:
            dec_pesticide  = 1
            conf_pesticide = 95.0  # confiance elevee car confirmation visuelle directe

    # ============================================================
    # GESTION DES CONFLITS
    # ============================================================
    conflit = irrigation_bloquee_par_pesticide = irrigation_bloquee_par_delai = False
    message_conflit = None

    heures = heures_depuis_pulverisation(lat, lon)
    if heures is not None and heures < DELAI_PULVERISATION_H:
        heures_restantes = int(DELAI_PULVERISATION_H - heures)
        if dec_irrigation == 1:
            dec_irrigation = 0
            irrigation_bloquee_par_delai = conflit = True
            message_conflit = (f"Irrigation bloquee — pulverisation il y a {int(heures)}h. "
                               f"Attendre encore {heures_restantes}h (delai securite 48h — source CCHST)")

    if dec_irrigation == 1 and dec_pesticide == 1:
        dec_irrigation = 0
        conflit = irrigation_bloquee_par_pesticide = True
        message_conflit = ("CONFLIT DETECTE — Pulverisation prioritaire sur irrigation. "
                           "Irrigation bloquee (maladie non traitee = risque recolte 100%). "
                           "Relancer irrigation apres 48h.")

    if dec_pesticide == 1:
        enregistrer_pulverisation(lat, lon)

    # ============================================================
    # ACTION FINALE
    # ============================================================
    if frostypod_detecte:             action = "ACTION_MANUELLE"
    elif dec_irrigation == 1:         action = "IRRIGUER"
    elif dec_pesticide == 1:          action = "PULVERISER"
    else:                             action = "AUCUNE_ACTION"

    # ============================================================
    # ENVOI SMS
    # ============================================================
    sms_envoye = False
    if SMS_DISPONIBLE:
        if action == "IRRIGUER":
            sms_envoye = sms_irrigation(
                decision=1, confiance=round(conf_irrigation*100,1),
                humidite_sol=donnees["humidite_sol"], saison=get_nom_saison(saison)
            )
        elif action == "PULVERISER":
            sms_envoye = sms_pulverisation(
                decision=1, confiance=round(conf_pesticide,1),
                maladie=maladie_detectee, saison=get_nom_saison(saison)
            )
        elif action == "ACTION_MANUELLE":
            sms_envoye = sms_frostypod(confiance=100.0, parcelle_gps=f"{lat},{lon}")
        if conflit and message_conflit:
            sms_conflit(
                message_conflit=message_conflit,
                heures_restantes=int(DELAI_PULVERISATION_H-heures) if heures else None
            )

    # Sauvegarder la derniere lecture ESP32
    derniere_lecture.update({
        "temperature"  : donnees["temperature"],
        "humidite_air" : donnees["humidite_air"],
        "humidite_sol" : donnees["humidite_sol"],
        "vitesse_vent" : donnees["vitesse_vent"],
        "pluie"        : donnees["pluie"],
        "horodatage"   : datetime.now().strftime("%H:%M:%S"),
        "source"       : "ESP32"
    })

    return jsonify({
        "action"  : action,
        "conflit" : conflit,
        "irrigation" : {
            "decision"              : dec_irrigation,
            "confiance"             : round(conf_irrigation*100,1),
            "bloquee_par_pesticide" : irrigation_bloquee_par_pesticide,
            "bloquee_par_delai"     : irrigation_bloquee_par_delai
        },
        "pulverisation" : {
            "decision"  : dec_pesticide,
            "confiance" : round(conf_pesticide,1),
            "risques"   : {"pourriture_brune": risque_pourriture, "mirides": risque_mirides}
        },
        "maladie" : {
            "detectee"    : maladie_detectee,
            "mode_risque" : mode_risque,
            "frostypod"   : frostypod_detecte,
            "message"     : message_frostypod
        },
        "sms_envoye"      : sms_envoye,
        "message_conflit" : message_conflit,
        "contexte" : {
            "mois"             : mois,
            "saison"           : get_nom_saison(saison),
            "pluie_prevue_24h" : pluie_prevue_24h,
            "pluie_prevue_3h"  : pluie_prevue_3h,
            "latitude"         : lat,
            "longitude"        : lon
        },
        "donnees_recues" : {
            "temperature"      : donnees["temperature"],
            "humidite_air"     : donnees["humidite_air"],
            "humidite_sol"     : donnees["humidite_sol"],
            "vitesse_vent"     : donnees["vitesse_vent"],
            "pluie"            : donnees["pluie"],
            "maladie_detectee" : maladie_detectee
        }
    })


@app.route("/derniere_lecture", methods=["GET"])
def get_derniere_lecture():
    """
    Retourne la derniere lecture enregistree par l'ESP32.
    Mise a jour a chaque appel de /predire, /pulveriser ou /decider.
    Le dashboard lit cette route pour afficher les donnees en temps reel.
    """
    if not derniere_lecture:
        return jsonify({
            "statut"    : "vide",
            "message"   : "Aucune lecture ESP32 recue pour l'instant",
            "disponible": False
        })
    return jsonify({
        "statut"     : "ok",
        "disponible" : True,
        "lecture"    : derniere_lecture
    })


@app.route("/analyser", methods=["POST"])
def analyser():
    """
    Analyse photo cabosse depuis smartphone.
    Format 1 : multipart/form-data -> champ 'image'
    Format 2 : JSON               -> champ 'image_base64'
    SMS automatique si maladie detectee (sauf HEALTHY).
    """
    if modele_maladie is None:
        return jsonify({"statut": "erreur", "message": "Modele maladie non charge"}), 500
    try:
        if "image" in request.files:
            image_bytes = request.files["image"].read()
            lat = float(request.form.get("latitude",  LAT_DEFAUT))
            lon = float(request.form.get("longitude", LON_DEFAUT))
        elif request.is_json:
            donnees = request.get_json()
            if "image_base64" not in donnees:
                return jsonify({"statut": "erreur", "message": "Champ manquant : image ou image_base64"}), 400
            image_bytes = base64.b64decode(donnees["image_base64"])
            lat = donnees.get("latitude",  LAT_DEFAUT)
            lon = donnees.get("longitude", LON_DEFAUT)
        else:
            return jsonify({"statut": "erreur", "message": "Envoyer image en multipart ou image_base64 en JSON"}), 400

        img_array    = preparer_image_depuis_bytes(image_bytes)
        probabilites = modele_maladie.predict(img_array, verbose=0)[0]
        idx_max      = int(np.argmax(probabilites))
        classe_pred  = CLASSES_MALADIE[idx_max]
        confiance    = float(probabilites[idx_max])
        proba_toutes = {CLASSES_MALADIE[i]: round(float(probabilites[i])*100,1) for i in range(len(CLASSES_MALADIE))}
        info         = MESSAGES_MALADIE[classe_pred]

        if confiance < SEUIL_CONFIANCE:
            return jsonify({
                "statut"           : "ok",
                "detection_fiable" : False,
                "message"          : "Confiance insuffisante — reprendre la photo plus pres de la cabosse",
                "conseils_photo"   : ["Cadrer uniquement la cabosse", "Distance 20-30cm",
                                      "Bonne luminosite sans ombre", "Eviter le flou"],
                "classe_probable"  : classe_pred,
                "confiance"        : round(confiance*100,1),
                "probabilites"     : proba_toutes
            })

        sms_envoye = False
        if SMS_DISPONIBLE and classe_pred != "HEALTHY":
            if classe_pred == "FROSTYPOD":
                sms_envoye = sms_frostypod(confiance=round(confiance*100,1), parcelle_gps=f"{lat},{lon}")
            else:
                sms_envoye = sms_maladie_detectee(
                    maladie=classe_pred, confiance=round(confiance*100,1),
                    action=info["action"], parcelle_gps=f"{lat},{lon}"
                )

        return jsonify({
            "statut"                : "ok",
            "detection_fiable"      : True,
            "maladie"               : classe_pred,
            "statut_maladie"        : info["statut"],
            "action"                : info["action"],
            "gravite"               : info["gravite"],
            "confiance"             : round(confiance*100,1),
            "probabilites"          : proba_toutes,
            "source"                : info["source"],
            "recommande_traitement" : info["gravite"] >= 2,
            "sms_envoye"            : sms_envoye,
            "message"               : (
                f"{info['statut']} detecte avec {confiance*100:.1f}% de confiance. Action : {info['action']}"
                if classe_pred != "HEALTHY" else "Cabosse saine — aucun traitement necessaire"
            ),
            "contexte" : {
                "latitude"  : lat,
                "longitude" : lon,
                "saison"    : get_nom_saison(get_saison(datetime.now().month))
            }
        })
    except Exception as e:
        return jsonify({"statut": "erreur", "message": f"Erreur analyse image : {str(e)}"}), 500


# -- DEMARRAGE -----------------------------------------------
if __name__ == "__main__":
    print("=" * 55)
    print("   API CACAO INTELLIGENT v6 - Demarrage")
    print("=" * 55)
    print(f"SMS        : {'actif' if SMS_DISPONIBLE else 'inactif'}")
    print("Routes     :")
    print("   GET  /  |  GET  /meteo")
    print("   POST /predire  |  POST /pulveriser")
    print("   POST /decider  |  POST /analyser")
    print("=" * 55)
    app.run(debug=True, host="0.0.0.0", port=5000)
