"""
CACAO INTELLIGENT — Page Decision Combinee
Donnees ESP32 + upload photo maladie + irrigation + pulverisation.
"""
import streamlit as st
from components.widgets import header_banner, card, badge, barre_confiance, action_box, alerte_conflit, erreur_api, placeholder_vide, statut_esp32
from api_client import decider, get_derniere_lecture, analyser_image
from config import LAT_DEFAUT, LON_DEFAUT, SEUIL_CONFIANCE
from auth_manager import enregistrer_decision

def afficher():
    header_banner("Decision Combinee", "Irrigation + Pulverisation + Gestion conflits")

    data_lecture, _ = get_derniere_lecture()
    lecture         = data_lecture.get("lecture",    {}) if data_lecture else {}
    esp32           = data_lecture.get("disponible", False) if data_lecture else False

    col1, col2 = st.columns([1, 1])

    with col1:
        # ---- CAPTEURS
        statut_esp32(esp32, lecture.get("horodatage", ""))

        def_temp = lecture.get("temperature",  29.0)
        def_hair = lecture.get("humidite_air", 72.0)
        def_hsol = lecture.get("humidite_sol", 35.0)
        def_vent = lecture.get("vitesse_vent",  5.0)
        def_plui = lecture.get("pluie",         0.0)

        temperature  = st.number_input("Temperature (C)",     min_value=0.0, max_value=50.0,  value=float(def_temp), step=0.5, disabled=esp32, key="dec_temp")
        humidite_air = st.number_input("Humidite air (%)",    min_value=0.0, max_value=100.0, value=float(def_hair), step=1.0, disabled=esp32, key="dec_hair")
        humidite_sol = st.number_input("Humidite sol (%)",    min_value=0.0, max_value=100.0, value=float(def_hsol), step=1.0, disabled=esp32, key="dec_hsol")
        vitesse_vent = st.number_input("Vitesse vent (km/h)", min_value=0.0, max_value=100.0, value=float(def_vent), step=0.5, disabled=esp32, key="dec_vent")
        pluie        = st.number_input("Pluie actuelle (mm)", min_value=0.0, max_value=200.0, value=float(def_plui), step=0.1, disabled=esp32, key="dec_plui")

        # ---- PHOTO MALADIE
        st.markdown("<div style='margin-top:16px;font-size:13px;color:#5D4037'>Photo cabosse (optionnel)</div>", unsafe_allow_html=True)
        photo = st.file_uploader("Photo cabosse", type=["jpg","jpeg","png"], label_visibility="collapsed", key="dec_photo")
        if photo:
            st.image(photo, use_container_width=True)

        c1, c2 = st.columns(2)
        with c1:
            btn_decider = st.button("Decider",    key="dec_btn")
        with c2:
            actualiser  = st.button("Actualiser", key="dec_refresh")

    if actualiser:
        st.rerun()

    with col2:
        if btn_decider:

            # Etape 1 : analyser photo si fournie
            maladie_injectee = None
            if photo:
                photo.seek(0)
                data_img, err_img = analyser_image(photo.read(), LAT_DEFAUT, LON_DEFAUT)
                if err_img:
                    erreur_api(err_img)
                    return
                if data_img.get("detection_fiable"):
                    maladie_injectee = data_img.get("maladie")
                    conf_img         = data_img.get("confiance", 0.0)
                    card("Photo analysee", [
                        ("Maladie detectee", f"<b>{maladie_injectee}</b>"),
                        ("Confiance",        f"<b>{conf_img:.1f}%</b>"),
                    ])
                else:
                    st.markdown("<div class='alerte-conflit'>Confiance insuffisante — mode automatique</div>", unsafe_allow_html=True)

            # Etape 2 : appel /decider
            data, erreur = decider(
                temperature=temperature, humidite_air=humidite_air,
                humidite_sol=humidite_sol, vitesse_vent=vitesse_vent,
                pluie=pluie, maladie_detectee=maladie_injectee,
                lat=LAT_DEFAUT, lon=LON_DEFAUT,
            )
            if erreur:
                erreur_api(erreur)
                return

            action        = data.get("action",          "AUCUNE_ACTION")
            conflit       = data.get("conflit",         False)
            msg_conflit   = data.get("message_conflit", "")
            sms_envoye    = data.get("sms_envoye",      False)
            irrigation    = data.get("irrigation",      {})
            pulverisation = data.get("pulverisation",   {})
            maladie_data  = data.get("maladie",         {})
            contexte      = data.get("contexte",        {})

            # ---- Enregistrer la decision dans le profil ----
            enregistrer_decision(
                username = st.session_state.get("username"),
                action   = action,
                contexte = {
                    "saison":        contexte.get("saison"),
                    "irrigation":    irrigation.get("decision"),
                    "pulverisation": pulverisation.get("decision"),
                    "maladie":       maladie_injectee,
                }
            )

            action_box(action)
            if conflit and msg_conflit:
                alerte_conflit(msg_conflit)

            c1, c2 = st.columns(2)
            with c1:
                dec_irr  = irrigation.get("decision", 0)
                conf_irr = irrigation.get("confiance", 0.0)
                blq_pest = irrigation.get("bloquee_par_pesticide", False)
                blq_del  = irrigation.get("bloquee_par_delai", False)
                dec_lbl  = badge("Recommandee", "ok") if dec_irr == 1 else (badge("Bloquee pesticide","err") if blq_pest else (badge("Delai 48h","warn") if blq_del else badge("Non recommandee","warn")))
                card("Irrigation", [("Decision", dec_lbl)], couleur="blue" if dec_irr == 1 else "caramel")
                barre_confiance(conf_irr, couleur="blue" if dec_irr == 1 else "green")

            with c2:
                dec_pest  = pulverisation.get("decision", 0)
                conf_pest = pulverisation.get("confiance", 0.0)
                card("Pulverisation", [("Decision", badge("Recommandee","ok") if dec_pest == 1 else badge("Non recommandee","warn"))], couleur="caramel" if dec_pest == 1 else "green")
                barre_confiance(conf_pest, couleur="red" if dec_pest == 1 else "green")

            card("Contexte", [
                ("Saison",      f"<b>{contexte.get('saison', '-')}</b>"),
                ("Mode risque", f"<b>{maladie_data.get('mode_risque', 'automatique')}</b>"),
                ("SMS envoye",  badge("Oui","ok") if sms_envoye else badge("Non","warn")),
            ])

        else:
            placeholder_vide("Cliquez sur Decider pour obtenir une recommandation")