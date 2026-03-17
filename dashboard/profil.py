"""
CACAO INTELLIGENT — Page Profil Agriculteur
Affiche ID Digital, infos metier, GPS, conformite EUDR et historique.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
import pandas as pd
from components.widgets import header_banner, card, badge
from auth_manager import get_profil_etendu, sauvegarder_config
from gps_manager import (
    charger_profil,
    sauvegarder_gps,
    sauvegarder_eudr,
    verifier_deforestation,
)
from dds_generator import generer_dds


def afficher(authenticator, config):
    username = st.session_state.get("username", "")
    name = st.session_state.get("name", "")
    digital_id = "CI-" + username[:8].upper()

    header_banner("Profil Agriculteur", name + " — " + digital_id)

    profil_auth = get_profil_etendu(username)
    profil_gps = charger_profil(username)

    # ---- ID Digital ----
    st.markdown(
        "<div class='card' style='text-align:center;padding:32px'>"
        "<div style='font-size:13px;color:#B0A090;margin-bottom:8px'>Votre identifiant Digital ID Africa</div>"
        "<div style='font-family:Playfair Display,serif;font-size:38px;font-weight:700;color:#2C1810;letter-spacing:3px'>"
        + digital_id
        + "</div>"
        "<div style='font-size:13px;color:#6B3A2A;margin-top:8px'>"
        + name
        + "</div>"
        "</div>",
        unsafe_allow_html=True,
    )

    # ---- Cards identite ----
    col1, col2 = st.columns(2)

    parcelle = profil_gps.get("parcelle", {})
    lat_val = parcelle.get("latitude", profil_auth.get("latitude", ""))
    lon_val = parcelle.get("longitude", profil_auth.get("longitude", ""))
    sup_val = parcelle.get("superficie", profil_auth.get("superficie", ""))
    coop_val = profil_gps.get("cooperative", profil_auth.get("cooperative", "-"))

    with col1:
        lat_display = str(lat_val) if lat_val else "-"
        lon_display = str(lon_val) if lon_val else "-"
        sup_display = str(sup_val) + " ha" if sup_val else "- ha"
        card("Informations Parcelle", [
            ("Cooperative", "<b>" + coop_val + "</b>"),
            ("Latitude", "<b>" + lat_display + "</b>"),
            ("Longitude", "<b>" + lon_display + "</b>"),
            ("Superficie", "<b>" + sup_display + "</b>"),
        ], couleur="green")

    with col2:
        historique = profil_auth.get("historique", profil_gps.get("historique", []))
        total = len(historique)
        irrigations = sum(1 for h in historique if h.get("action") == "IRRIGUER")
        pulverisations = sum(1 for h in historique if h.get("action") == "PULVERISER")
        card("Statistiques Decisions", [
            ("Total decisions", "<b>" + str(total) + "</b>"),
            ("Irrigations", "<b>" + str(irrigations) + "</b>"),
            ("Pulverisations", "<b>" + str(pulverisations) + "</b>"),
        ], couleur="blue")

    # ============================================================
    # SECTION GEOLOCALISATION & CONFORMITE EUDR
    # ============================================================
    st.markdown(
        "<div style='font-family:Playfair Display,serif;font-size:18px;font-weight:700;color:#2C1810;margin:28px 0 12px 0'>"
        "Geolocalisation et Conformite EUDR</div>",
        unsafe_allow_html=True,
    )

    # ---- Badge statut EUDR ----
    eudr = profil_gps.get("eudr", {})
    statut_eudr = eudr.get("statut")
    verifie = eudr.get("verifie", False)

    if not verifie or statut_eudr is None:
        badge_class = "badge-warn"
        badge_text = "EUDR : Non verifie"
        badge_msg = "Aucune verification de deforestation effectuee pour cette parcelle."
    elif statut_eudr == "CONFORME":
        badge_class = "badge-ok"
        badge_text = "EUDR : CONFORME"
        date_verif = eudr.get("date_verification", "")
        badge_msg = "Parcelle conforme au reglement EUDR 2023/1115. Verification : " + date_verif
    elif statut_eudr == "NON_CONFORME":
        badge_class = "badge-err"
        badge_text = "EUDR : NON CONFORME"
        badge_msg = "Deforestation detectee apres le 31/12/2020. Parcelle non conforme."
    else:
        badge_class = "badge-warn"
        badge_text = "EUDR : INDETERMINE"
        badge_msg = "Statut indetermine. Verification manuelle recommandee."

    st.markdown(
        "<div class='card' style='padding:20px'>"
        "<div style='display:flex;align-items:center;gap:12px;margin-bottom:8px'>"
        "<span class='" + badge_class + "'>" + badge_text + "</span>"
        "</div>"
        "<div style='font-size:13px;color:#6B3A2A'>" + badge_msg + "</div>"
        "</div>",
        unsafe_allow_html=True,
    )

    # ---- Formulaire GPS ----
    st.markdown("<div style='margin-top:24px;margin-bottom:8px;font-weight:600;color:#2C1810;'>Mise à jour de la localisation GPS de votre parcelle</div>", unsafe_allow_html=True)
    with st.expander("Cliquez ici pour modifier les coordonnées (Latitude, Longitude, Superficie)", expanded=False):
        default_lat = float(lat_val) if lat_val else 5.7833
        default_lon = float(lon_val) if lon_val else -6.5833
        default_sup = float(sup_val) if sup_val else 1.0

        new_lat = st.number_input(
            "Latitude",
            min_value=4.0,
            max_value=11.0,
            value=default_lat,
            format="%.4f",
            key="gps_lat",
        )
        new_lon = st.number_input(
            "Longitude",
            min_value=-9.0,
            max_value=-2.0,
            value=default_lon,
            format="%.4f",
            key="gps_lon",
        )
        new_sup = st.number_input(
            "Superficie (ha)",
            min_value=0.1,
            max_value=500.0,
            value=default_sup,
            format="%.2f",
            key="gps_sup",
        )

        # Carte temps reel
        map_data = pd.DataFrame({"lat": [new_lat], "lon": [new_lon]})
        st.map(map_data, zoom=10)

        if st.button("Enregistrer GPS", key="btn_save_gps"):
            sauvegarder_gps(username, new_lat, new_lon, new_sup)
            st.success("Coordonnees GPS enregistrees avec succes.")
            st.rerun()

    # ---- Bouton verification EUDR ----
    has_coords = bool(lat_val) and bool(lon_val)

    if has_coords:
        if st.button("Verifier non-deforestation (EUDR)", key="btn_eudr"):
            check_lat = float(lat_val)
            check_lon = float(lon_val)
            with st.spinner("Verification en cours via Global Forest Watch..."):
                resultat = verifier_deforestation(check_lat, check_lon)

            stat = resultat.get("statut", "INDETERMINE")
            detail = resultat.get("detail", "")
            src = resultat.get("source", "")
            api_ok = resultat.get("api_ok", False)

            if stat == "CONFORME":
                st.success("CONFORME — " + detail)
            elif stat == "NON_CONFORME":
                st.error("NON CONFORME — " + detail)
            else:
                st.warning("INDETERMINE — " + detail)

            if not api_ok:
                st.info("Note : resultat base sur le fallback geographique (API indisponible).")

            sauvegarder_eudr(username, stat, src)
            st.rerun()

    # ---- Telechargement du DDS ----
    if verifie and statut_eudr == "CONFORME":
        prenom_val = profil_auth.get("prenom", name.split()[0] if " " in name else name)
        nom_val = profil_auth.get("nom", name.split()[1] if " " in name else "")
        profil_dds = {
            "id": digital_id,
            "prenom": prenom_val,
            "nom": nom_val,
            "telephone": username,
            "cooperative": coop_val,
            "parcelle": {"latitude": lat_val, "longitude": lon_val, "superficie": sup_val},
            "eudr": eudr
        }
        pdf_bytes = generer_dds(profil_dds)
        file_nom = "DDS_" + digital_id + ".pdf"
        st.markdown("<div style='margin-top:16px'></div>", unsafe_allow_html=True)
        st.download_button(
            label="Telecharger le DDS (PDF)",
            data=pdf_bytes,
            file_name=file_nom,
            mime="application/pdf",
            type="primary"
        )
    elif verifie and statut_eudr == "NON_CONFORME":
        msg_err = "Telechargement impossible — parcelle non conforme EUDR"
        st.markdown("<div style='color:#B71C1C;font-size:14px;font-weight:600;margin-top:16px'>" + msg_err + "</div>", unsafe_allow_html=True)


    # ============================================================
    # HISTORIQUE DES DECISIONS
    # ============================================================
    st.markdown(
        "<div style='font-family:Playfair Display,serif;font-size:18px;font-weight:700;color:#2C1810;margin:24px 0 12px 0'>"
        "Historique des decisions</div>",
        unsafe_allow_html=True,
    )

    if historique:
        for h in historique[:50]:
            action_type = h.get("action", "-")
            badge_type = "ok" if action_type == "AUCUNE_ACTION" else "warn"
            action_badge = badge(action_type, badge_type)
            ctx = h.get("contexte", {})
            saison = ctx.get("saison", "-") if isinstance(ctx, dict) else "-"
            date_str = h.get("date", "-")
            st.markdown(
                "<div class='card-row'>"
                "<span>" + date_str + "</span>"
                "<span>" + action_badge + "</span>"
                "<span style='font-size:12px;color:#B0A090'>" + saison + "</span>"
                "</div>",
                unsafe_allow_html=True,
            )
    else:
        st.markdown(
            "<div class='card' style='text-align:center;padding:32px'>"
            "<p style='color:#9E9E9E;font-size:14px'>Aucune decision enregistree</p>"
            "</div>",
            unsafe_allow_html=True,
        )

    # ---- Deconnexion ----
    st.markdown("<div style='margin-top:24px'></div>", unsafe_allow_html=True)
    authenticator.logout("Se deconnecter", key="logout_profil")
    sauvegarder_config(config)
