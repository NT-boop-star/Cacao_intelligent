import streamlit as st
import json
import os

ORDRE_STATUTS = ["EN_ATTENTE", "COLLECTÉ", "EN_TRANSIT", "EXPORTÉ"]

COULEURS_STATUTS = {
    "EN_ATTENTE": "#FFC107",
    "COLLECTÉ": "#17A2B8",
    "EN_TRANSIT": "#6F42C1",
    "EXPORTÉ": "#28A745"
}

def afficher(lot_id):
    st.markdown(
        f"<div class='header-banner' style='text-align: center'>"
        f"<p class='header-title'>Vérification de lot — Cacao Intelligent</p>"
        f"<p class='header-sub'>Portail public de traçabilité</p></div>",
        unsafe_allow_html=True,
    )
    
    if not lot_id:
        st.error("Aucun lot spécifié.")
        return
        
    fichier = os.path.join(os.path.dirname(os.path.dirname(__file__)), "agriculteurs.json")
    try:
        with open(fichier, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        data = {}
        
    lot_trouve = None
    eudr_statut = "NON_VERIFIE"
    for ag_id, profil in data.items():
        for lot in profil.get("lots", []):
            if lot.get("id") == lot_id:
                lot_trouve = lot
                eudr_statut = profil.get("eudr", {}).get("statut", "NON_VERIFIE")
                break
        if lot_trouve:
            break
            
    if not lot_trouve:
        st.error("Lot introuvable — ID invalide")
        return
        
    # Render Data
    statut_actuel = lot_trouve.get("statut", "EN_ATTENTE")
    couleur = COULEURS_STATUTS.get(statut_actuel, "#999999")
    coop = lot_trouve.get("cooperative", "").strip()
    if not coop or coop == "-":
        coop = "Indépendante"
    
    html_card = f"""
    <div style="background-color: white; padding: 25px; border-radius: 12px; border-left: 8px solid {couleur}; box-shadow: 0 4px 12px rgba(0,0,0,0.08); margin-bottom: 30px;">
        <div style="text-align: center; margin-bottom: 20px;">
            <h2 style="margin: 0; color: #2C1810; font-family: 'Playfair Display', serif; font-size: 28px;">{lot_id}</h2>
            <div style="margin-top: 10px;">
                <span style="background-color: {couleur}; color: white; padding: 6px 16px; border-radius: 20px; font-size: 15px; font-weight: bold; letter-spacing: 1px;">
                    {statut_actuel.replace('_', ' ')}
                </span>
            </div>
        </div>
        <div style="display: flex; flex-direction: column; gap: 12px; font-size: 15px; color: #4A3B32;">
            <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #f0f0f0; padding-bottom: 8px;">
                <strong>Date de récolte :</strong> <span>{lot_trouve.get('date_recolte', 'N/A')}</span>
            </div>
            <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #f0f0f0; padding-bottom: 8px;">
                <strong>Poids :</strong> <span>{lot_trouve.get('poids_kg', 0)} kg</span>
            </div>
            <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #f0f0f0; padding-bottom: 8px;">
                <strong>Coopérative :</strong> <span>{coop}</span>
            </div>
            <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #f0f0f0; padding-bottom: 8px;">
                <strong>Conformité EUDR :</strong> <span style="font-weight:bold; color: {'#28A745' if eudr_statut == 'CONFORME' else '#DC3545'};">{eudr_statut.replace('_', ' ')}</span>
            </div>
        </div>
    </div>
    """
    st.markdown(html_card, unsafe_allow_html=True)
    
    # Timeline
    try:
        current_idx = ORDRE_STATUTS.index(statut_actuel)
    except ValueError:
        current_idx = 0
    
    st.markdown("<h3 style='text-align:center; font-family:Playfair Display, serif; color:#2C1810; margin-bottom: 20px;'>Historique Logistique</h3>", unsafe_allow_html=True)
    
    timeline_html = "<div style='display: flex; align-items: flex-start; justify-content: space-between; padding: 25px 15px; background: white; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); overflow-x: auto;'>"
    
    # Map historiques for dates
    hist_dates = {}
    for entry in lot_trouve.get("historique_statuts", []):
        hist_dates[entry["statut"]] = entry["date"]
        
    for i, etat in enumerate(ORDRE_STATUTS):
        is_past = i <= current_idx
        bg_color = "#28A745" if is_past else "#E9ECEF"
        text_color = "white" if is_past else "#6C757D"
        label = etat.replace("_", " ")
        date_str = hist_dates.get(etat, "En attente") if is_past else "À venir"
        
        timeline_html += f"""
        <div style='display: flex; flex-direction: column; align-items: center; z-index: 2; min-width: 80px;'>
            <div style='width: 36px; height: 36px; border-radius: 18px; background-color: {bg_color}; color: {text_color}; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 15px; margin-bottom: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
                {i+1}
            </div>
            <span style='font-size: 13px; font-weight: 700; color: #2C1810; text-align:center; margin-bottom: 4px;'>{label}</span>
            <span style='font-size: 11px; color: #888; text-align:center;'>{date_str}</span>
        </div>
        """
        
        if i < len(ORDRE_STATUTS) - 1:
            line_color = "#28A745" if i < current_idx else "#E9ECEF"
            timeline_html += f"<div style='flex-grow: 1; height: 5px; background-color: {line_color}; margin: 15px -15px 0 -15px; z-index: 1;'></div>"
            
    timeline_html += "</div>"
    st.markdown(timeline_html, unsafe_allow_html=True)
