"""
CACAO INTELLIGENT — Point d'entree
Lance avec : streamlit run dashboard/app_dashboard.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
from config import CSS
from auth_manager import get_authenticator, sauvegarder_config, sauvegarder_profil_etendu

st.set_page_config(
    page_title            = "Cacao Intelligent",
    page_icon             = "🌿",
    layout                = "wide",
    initial_sidebar_state = "expanded"
)

st.markdown(CSS, unsafe_allow_html=True)

# ---- Charger authenticator ----
config, authenticator = get_authenticator()


# ============================================================
# Fonction login / inscription  (affiche AVANT connexion)
# ============================================================
def afficher_login(authenticator, config):
    st.markdown(
        "<div style='max-width:480px;margin:60px auto'>"
        "<div class='header-banner' style='text-align:center'>"
        "<p class='header-title'>Cacao Intelligent</p>"
        "<p class='header-sub'>AgriTech Innovators — ESATIC</p></div></div>",
        unsafe_allow_html=True,
    )

    tab_login, tab_register = st.tabs(["Connexion", "Creer un compte"])

    with tab_login:
        try:
            authenticator.login(
                fields={
                    "Form name": "Connexion",
                    "Username":  "Telephone",
                    "Password":  "Mot de passe",
                    "Login":     "Se connecter",
                }
            )
        except Exception as e:
            st.error(str(e))

    with tab_register:
        st.markdown("<div style='font-size:14px;color:#5D4037;margin-bottom:12px'>Informations du compte</div>", unsafe_allow_html=True)
        try:
            (email_of_registered_user,
             username_of_registered_user,
             name_of_registered_user) = authenticator.register_user(
                merge_username_email=False,
                captcha=False,
                password_hint=False,
                fields={
                    "Form name":        "Inscription",
                    "First name":       "Prenom",
                    "Last name":        "Nom",
                    "Email":            "Email (optionnel)",
                    "Username":         "Telephone (identifiant)",
                    "Password":         "Mot de passe",
                    "Repeat password":  "Repeter le mot de passe",
                    "Register":         "Creer mon compte",
                },
            )
            if email_of_registered_user or username_of_registered_user:
                sauvegarder_config(config)
                st.success("Compte cree avec succes !")
                digital_id = "CI-" + (username_of_registered_user or "")[:8].upper()
                st.markdown(
                    f"<div class='card' style='text-align:center;padding:28px'>"
                    f"<div style='font-size:13px;color:#B0A090;margin-bottom:6px'>Votre identifiant Digital ID Africa</div>"
                    f"<div style='font-family:Playfair Display,serif;font-size:36px;font-weight:700;color:#2C1810;letter-spacing:3px'>{digital_id}</div>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

                # Champs metier supplementaires
                st.markdown("<div style='font-size:14px;color:#5D4037;margin:16px 0 8px'>Completez votre profil agriculteur</div>", unsafe_allow_html=True)
                cooperative = st.text_input("Cooperative",  key="reg_coop")
                latitude    = st.text_input("Latitude parcelle",  value="5.7833", key="reg_lat")
                longitude   = st.text_input("Longitude parcelle", value="-6.5833", key="reg_lon")
                superficie  = st.text_input("Superficie (ha)",    key="reg_sup")

                if st.button("Enregistrer le profil", key="reg_profil_btn"):
                    sauvegarder_profil_etendu(username_of_registered_user, {
                        "cooperative": cooperative,
                        "latitude":    latitude,
                        "longitude":   longitude,
                        "superficie":  superficie,
                        "historique":  [],
                    })
                    st.success("Profil enregistre ! Connectez-vous dans l'onglet Connexion.")

        except Exception as e:
            st.error(str(e))


# ============================================================
# ROUTING PRINCIPAL basé sur authentication_status
# ============================================================
lot_id_query = st.query_params.get("lot", None)

if lot_id_query:
    import pages.page_lot_public as mpl
    mpl.afficher(lot_id_query)
else:
    if st.session_state.get("authentication_status"):
        # ---- CONNECTE : sidebar + pages ----
        from api_client import tester_connexion
        from components.sidebar import afficher as afficher_sidebar
    
        @st.cache_data(ttl=30)
        def get_statut_cached():
            return tester_connexion()
    
        api_en_ligne, sms_actif = get_statut_cached()
        page = afficher_sidebar(api_en_ligne, sms_actif, authenticator, config)
    
        if page == "Dashboard":
            import pages.page_dashboard as m
            m.afficher()
        elif page == "Decision":
            import pages.page_decision as m
            m.afficher()
        elif page == "Profil":
            import profil as m
            m.afficher(authenticator, config)
        elif page == "Traçabilité":
            import pages.page_tracabilite as m
            m.afficher()
    
    elif st.session_state.get("authentication_status") is False:
        # ---- ERREUR ----
        st.error("Telephone ou mot de passe incorrect")
        afficher_login(authenticator, config)
    
    else:
        # ---- NON CONNECTE ----
        afficher_login(authenticator, config)