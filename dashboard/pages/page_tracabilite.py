import streamlit as st
import io
from PIL import Image
from lot_manager import charger_lots, creer_lot, changer_statut, generer_qr_bytes
from auth_manager import get_profil_etendu

# Ordre strict des statuts pour la timeline
ORDRE_STATUTS = ["EN_ATTENTE", "COLLECTÉ", "EN_TRANSIT", "EXPORTÉ"]

COULEURS_STATUTS = {
    "EN_ATTENTE": "#FFC107",
    "COLLECTÉ": "#17A2B8",
    "EN_TRANSIT": "#6F42C1",
    "EXPORTÉ": "#28A745"
}


# Cache QR codes pour eviter de les regenerer a chaque rechargement de page
@st.cache_data(ttl=300, show_spinner=False)
def _generer_qr_cache(lot_id, profil_id, profil_nom):
    """Genere et cache le QR code par lot_id. TTL=5min."""
    # On passe profil_id et profil_nom comme cles de cache (hashable)
    profil_minimal = {"id": profil_id, "nom": profil_nom}
    return generer_qr_bytes(lot_id, profil_minimal)

def header_banner(title, sub):
    st.markdown(
        f"<div class='header-banner'>"
        f"<p class='header-title'>{title}</p>"
        f"<p class='header-sub'>{sub}</p></div>",
        unsafe_allow_html=True,
    )

def afficher():
    username = st.session_state.get("username", "")
    profil = get_profil_etendu(username)
    
    header_banner("Traçabilité des Lots", "Gestion des récoltes et suivi logistique")

    # ---------------------------------------------------------
    # SECTION 1 — Créer un nouveau lot
    # ---------------------------------------------------------
    st.markdown("<h3>Déclarer une nouvelle récolte</h3>", unsafe_allow_html=True)
    with st.container():
        c1, c2, c3 = st.columns([2, 2, 1])
        with c1:
            date_recolte = st.date_input("Date de la récolte")
        with c2:
            poids_kg = st.number_input("Poids total (en kg)", min_value=1.0, max_value=10000.0, value=100.0, step=10.0)
        with c3:
            st.write("") # Spacer
            st.write("") # Spacer
            if st.button("Créer le lot", type="primary", use_container_width=True):
                lot = creer_lot(username, date_recolte, poids_kg)
                if lot:
                    st.success(f"Lot {lot['id']} créé avec succès !")
                    st.rerun()

    st.markdown("<hr style='margin: 30px 0; border-color: #E8A84C;'>", unsafe_allow_html=True)

    # ---------------------------------------------------------
    # Mettre à jour la variable lots
    # ---------------------------------------------------------
    lots = charger_lots(username)

    # ---------------------------------------------------------
    # SECTION 2 & 3 — Mes lots en cours et Chaîne de traçabilité
    # ---------------------------------------------------------
    st.markdown("<h3>Mes Lots en Cours</h3>", unsafe_allow_html=True)
    
    if not lots:
        st.info("Aucun lot déclaré pour le moment.")
    else:
        # Afficher les lots du plus récent au plus ancien (inversé)
        for lot in reversed(lots):
            lot_id = lot["id"]
            statut_actuel = lot["statut"]
            couleur = COULEURS_STATUTS.get(statut_actuel, "#999999")
            
            # Carte HTML pour les infos de base
            html_card = f"""
            <div style="background-color: white; padding: 20px; border-radius: 10px; border-left: 6px solid {couleur}; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                    <h4 style="margin: 0; color: #2C1810; font-family: 'Playfair Display', serif;">{lot_id}</h4>
                    <span style="background-color: {couleur}; color: white; padding: 5px 12px; border-radius: 20px; font-size: 13px; font-weight: bold;">
                        {statut_actuel.replace('_', ' ')}
                    </span>
                </div>
                <div style="display: flex; gap: 30px; font-size: 14px; color: #6B3A2A;">
                    <div><strong>Date de récolte :</strong> {lot['date_recolte']}</div>
                    <div><strong>Poids :</strong> {lot['poids_kg']} kg</div>
                    <div><strong>Date déclaration :</strong> {lot['date_creation']}</div>
                </div>
            """
            st.markdown(html_card + "</div>", unsafe_allow_html=True)
            
            # Timeline & Actions en dessous de la carte
            col_timeline, col_qr, col_action = st.columns([3, 1, 1])
            
            with col_timeline:
                # Générer le HTML de la timeline
                try:
                    current_idx = ORDRE_STATUTS.index(statut_actuel)
                except ValueError:
                    current_idx = 0
                
                timeline_html = "<div style='display: flex; align-items: center; justify-content: space-between; padding: 15px 10px; background: #f8f9fa; border-radius: 8px; margin-top: 5px;'>"
                
                for i, etat in enumerate(ORDRE_STATUTS):
                    is_past = i <= current_idx
                    bg_color = "#28A745" if is_past else "#E9ECEF"
                    text_color = "white" if is_past else "#6C757D"
                    label = etat.replace("_", " ")
                    
                    # Point d'étape
                    timeline_html += f"""
                    <div style='display: flex; flex-direction: column; align-items: center; z-index: 2;'>
                        <div style='width: 30px; height: 30px; border-radius: 15px; background-color: {bg_color}; color: {text_color}; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 14px; margin-bottom: 8px;'>
                            {i+1}
                        </div>
                        <span style='font-size: 11px; font-weight: 600; color: #495057;'>{label}</span>
                    </div>
                    """
                    
                    # Ligne de connexion sauf après le dernier
                    if i < len(ORDRE_STATUTS) - 1:
                        line_color = "#28A745" if i < current_idx else "#E9ECEF"
                        timeline_html += f"<div style='flex-grow: 1; height: 4px; background-color: {line_color}; margin: 0 -10px; margin-bottom: 20px; z-index: 1;'></div>"
                
                timeline_html += "</div>"
                st.markdown(timeline_html, unsafe_allow_html=True)
            
            with col_qr:
                profil_id  = profil.get("id", "")
                profil_nom = profil.get("nom", "")
                qr_bytes = _generer_qr_cache(lot_id, profil_id, profil_nom)
                img = Image.open(io.BytesIO(qr_bytes))
                st.image(img, width=120, caption="Scanner la traçabilité")
            
            with col_action:
                st.write("") # Spacer vertical
                if current_idx < len(ORDRE_STATUTS) - 1:
                    next_statut = ORDRE_STATUTS[current_idx + 1]
                    btn_label = f"Passer à 👉 {next_statut.replace('_', ' ')}"
                    if st.button(btn_label, key=f"btn_{lot_id}"):
                        changer_statut(username, lot_id, next_statut)
                        st.rerun()
                else:
                    st.success("Lot entièrement exporté")
            
            st.markdown("<br>", unsafe_allow_html=True)
