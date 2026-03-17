"""
CACAO INTELLIGENT — Gestionnaire d'authentification
Centralise la logique auth (streamlit-authenticator) et les profils metier.
"""
import os
import json
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
from datetime import datetime

# ---- Chemins ----
_DIR           = os.path.dirname(__file__)
_AUTH_YAML     = os.path.join(_DIR, "config_auth.yaml")
_AGRICULT_JSON = os.path.join(_DIR, "agriculteurs.json")

# ============================================================
# AUTHENTICATOR
# ============================================================
def get_authenticator():
    """
    Charge le fichier YAML et retourne (config_dict, authenticator).
    """
    with open(_AUTH_YAML, "r", encoding="utf-8") as f:
        config = yaml.load(f, Loader=SafeLoader)

    authenticator = stauth.Authenticate(
        config["credentials"],
        config["cookie"]["name"],
        config["cookie"]["key"],
        config["cookie"]["expiry_days"],
    )
    return config, authenticator


def sauvegarder_config(config):
    """
    Reecrit le fichier YAML (obligatoire apres register_user / logout).
    """
    with open(_AUTH_YAML, "w", encoding="utf-8") as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)


# ============================================================
# PROFIL ETENDU (agriculteurs.json)
# ============================================================
def _charger_agriculteurs():
    if not os.path.exists(_AGRICULT_JSON):
        return {}
    with open(_AGRICULT_JSON, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}


def _sauver_agriculteurs(data):
    with open(_AGRICULT_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_profil_etendu(username):
    """
    Retourne le profil metier d'un agriculteur (cooperative, parcelle, etc.)
    ou un dict vide si inconnu.
    """
    all_data = _charger_agriculteurs()
    return all_data.get(username, {})


def sauvegarder_profil_etendu(username, data):
    """
    Cree ou met a jour le profil metier d'un agriculteur.
    """
    all_data = _charger_agriculteurs()
    all_data[username] = data
    _sauver_agriculteurs(all_data)


def enregistrer_decision(username, action, contexte):
    """
    Ajoute une decision dans l'historique du profil etendu (max 50).
    """
    if not username:
        return
    profil = get_profil_etendu(username)
    historique = profil.get("historique", [])
    historique.insert(0, {
        "date":      datetime.now().strftime("%Y-%m-%d %H:%M"),
        "action":    action,
        "contexte":  contexte,
    })
    profil["historique"] = historique[:50]
    sauvegarder_profil_etendu(username, profil)
