"""
CACAO INTELLIGENT — Sidebar
Navigation Dashboard / Decision / Profil + info user connecte.
"""
import streamlit as st
from auth_manager import sauvegarder_config

PAGES_AUTH = ["Dashboard", "Decision", "Profil", "Traçabilité"]


def afficher(api_en_ligne, sms_actif, authenticator, config):
    with st.sidebar:
        # ---- Info utilisateur connecte ----
        username   = st.session_state.get("username", "")
        name       = st.session_state.get("name", "")
        digital_id = "CI-" + username[:8].upper()

        st.markdown(
            f"<div class='sidebar-logo'>"
            f"<div class='sidebar-app-name'>Cacao Intelligent</div>"
            f"<div class='sidebar-app-sub'>AgriTech Innovators — ESATIC</div>"
            f"<div style='margin-top:12px;font-size:13px;color:#E8A84C'>{name}</div>"
            f"<div style='font-size:15px;font-weight:700;color:#F5ECD7;letter-spacing:2px;margin-top:4px'>{digital_id}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )

        page = st.radio("Navigation", PAGES_AUTH, label_visibility="collapsed")

        statut_api = "en ligne"  if api_en_ligne else "hors ligne"
        statut_sms = "actif"     if sms_actif    else "inactif"
        st.markdown(
            f"<div class='sidebar-status'>API &nbsp; {statut_api}<br>SMS &nbsp; {statut_sms}<br><br>v6 · Digital ID Africa 2026</div>",
            unsafe_allow_html=True,
        )

        # ---- Bouton deconnexion ----
        authenticator.logout("Se deconnecter", key="logout_sidebar")
        sauvegarder_config(config)

    return page