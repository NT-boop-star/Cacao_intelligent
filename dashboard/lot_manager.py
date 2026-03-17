import json
import os
import random
import qrcode
from io import BytesIO
from datetime import datetime

FICHIER_AGRICULTEURS = os.path.join(os.path.dirname(__file__), "agriculteurs.json")

def _lire_donnees():
    with open(FICHIER_AGRICULTEURS, "r", encoding="utf-8") as f:
        return json.load(f)

def _ecrire_donnees(data):
    with open(FICHIER_AGRICULTEURS, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def charger_lots(username):
    data = _lire_donnees()
    return data.get(username, {}).get("lots", [])

def creer_lot(username, date_recolte, poids_kg):
    data = _lire_donnees()
    if username not in data:
        return None
    
    agriculteur = data[username]
    if "lots" not in agriculteur:
        agriculteur["lots"] = []
    
    rand_id = f"{random.randint(1000, 9999)}"
    lot_id = f"LOT-CI-2026-{rand_id}"
    date_jour = datetime.now().strftime("%Y-%m-%d")
    heure_jour = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    nouveau_lot = {
        "id": lot_id,
        "date_creation": date_jour,
        "date_recolte": str(date_recolte),
        "poids_kg": float(poids_kg),
        "statut": "EN_ATTENTE",
        "cooperative": agriculteur.get("cooperative", ""),
        "exportateur": None,
        "historique_statuts": [
            {"statut": "EN_ATTENTE", "date": heure_jour}
        ]
    }
    
    agriculteur["lots"].append(nouveau_lot)
    _ecrire_donnees(data)
    
    return nouveau_lot

def changer_statut(username, lot_id, nouveau_statut):
    data = _lire_donnees()
    if username not in data or "lots" not in data[username]:
        return False
    
    for lot in data[username]["lots"]:
        if lot["id"] == lot_id:
            lot["statut"] = nouveau_statut
            lot["historique_statuts"].append({
                "statut": nouveau_statut,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M")
            })
            _ecrire_donnees(data)
            return True
            
    return False

def generer_qr_bytes(lot_id, profil):
    qr_data = f"http://192.168.1.89:8502/?lot={lot_id}"
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()
