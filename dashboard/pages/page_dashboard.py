"""
CACAO INTELLIGENT — Page Dashboard
Statut modules + meteo + jauges temps reel. Refresh auto 30s.
"""
import streamlit as st
from streamlit_autorefresh import st_autorefresh
import plotly.graph_objects as go
from components.widgets import header_banner, card, badge, erreur_api
from api_client import get_meteo, get_derniere_lecture
from config import LAT_DEFAUT, LON_DEFAUT


def couleur_seuil(valeur, seuils):
    for max_val, c_barre, c_fond, label in seuils:
        if valeur <= max_val:
            return c_barre, c_fond, label
    return seuils[-1][1], seuils[-1][2], seuils[-1][3]

def jauge(valeur, titre, unite, min_val, max_val, seuils):
    c_barre, c_fond, label = couleur_seuil(valeur, seuils)
    fig = go.Figure(go.Indicator(
        mode  = "gauge+number",
        value = valeur,
        number = {"font": {"size": 36, "family": "Playfair Display", "color": "#2C1810"}, "suffix": f" {unite}"},
        title  = {"text": f"<b>{titre}</b><br><span style='font-size:11px;color:{c_barre}'>{label}</span>", "font": {"size": 13, "color": "#2C1810"}},
        gauge  = {
            "axis":      {"range": [min_val, max_val], "tickfont": {"size": 9, "color": "#B0A090"}, "nticks": 5},
            "bar":       {"color": c_barre, "thickness": 0.3},
            "bgcolor":   c_fond,
            "borderwidth": 2, "bordercolor": "#E8DDD0",
            "steps":     [{"range": [min_val, max_val], "color": "#F5ECD7"}],
            "threshold": {"line": {"color": "#2C1810", "width": 3}, "thickness": 0.85, "value": valeur},
        }
    ))
    fig.update_layout(height=220, margin={"t": 80, "b": 5, "l": 15, "r": 15}, paper_bgcolor=c_fond, plot_bgcolor=c_fond)
    return fig

def afficher_jauges(titre_section, liste_jauges):
    st.markdown(f"<div style='text-align:center;font-family:Playfair Display,serif;font-size:18px;font-weight:700;color:#2C1810;margin:24px 0 12px 0'>{titre_section}</div>", unsafe_allow_html=True)
    cols = st.columns(len(liste_jauges))
    for i, (col, d) in enumerate(zip(cols, liste_jauges)):
        with col:
            st.plotly_chart(jauge(d["valeur"], d["titre"], d["unite"], d["min"], d["max"], d["seuils"]), use_container_width=True, key=f"j{i}{titre_section[:3]}")

def afficher():
    header_banner("Dashboard", "Systeme IoT cacao — Abidjan, Cote d'Ivoire")

    # Rafraichissement automatique non-bloquant (120 000 ms = 2 min)
    st_autorefresh(interval=120000, key="dash_refresh")

    data_meteo,   err_meteo   = get_meteo(LAT_DEFAUT, LON_DEFAUT)
    data_lecture, _           = get_derniere_lecture()

    meteo   = data_meteo.get("meteo",    {}) if data_meteo   else {}
    lecture = data_lecture.get("lecture", {}) if data_lecture else {}
    esp32   = data_lecture.get("disponible", False) if data_lecture else False

    if err_meteo:
        erreur_api(err_meteo)
    else:
        # On centre la carte Contexte Actuel pour un meilleur UX
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            card("Contexte Actuel", [
                ("Zone",             f"<b>{meteo.get('ville', 'Abidjan')}, Cote d'Ivoire</b>"),
                ("Saison",           f"<b>{meteo.get('saison', '-')}</b>"),
                ("ESP32",            badge("Connecte", "ok") if esp32 else badge("Hors ligne", "warn")),
                ("Pluie prevue 24h", badge("Oui", "warn") if meteo.get("pluie_prevue_24h") else badge("Non", "ok")),
            ], couleur="green")

    SEUILS_TEMP  = [(20,"#2E86C1","#EBF5FB","Frais"),(30,"#27AE60","#E8F5E9","Optimal"),(38,"#F39C12","#FFF8E1","Chaud"),(50,"#E74C3C","#FFEBEE","Critique")]
    SEUILS_HUM   = [(40,"#E74C3C","#FFEBEE","Trop sec"),(60,"#F39C12","#FFF8E1","Acceptable"),(80,"#27AE60","#E8F5E9","Optimal"),(100,"#2E86C1","#EBF5FB","Sature")]
    SEUILS_VENT  = [(12,"#27AE60","#E8F5E9","Calme"),(25,"#F39C12","#FFF8E1","Modere"),(60,"#E74C3C","#FFEBEE","Fort")]
    SEUILS_PLUIE = [(2,"#27AE60","#E8F5E9","Sec"),(10,"#2E86C1","#EBF5FB","Pluie legere"),(30,"#1A5276","#D6EAF8","Pluie forte")]
    SEUILS_SOL   = [(25,"#E74C3C","#FFEBEE","Sol sec"),(50,"#F39C12","#FFF8E1","Acceptable"),(75,"#27AE60","#E8F5E9","Optimal"),(100,"#2E86C1","#EBF5FB","Sature")]

    if not err_meteo and meteo:
        afficher_jauges("Meteo en temps reel", [
            {"valeur": round(float(meteo.get("temperature",  0)), 1), "titre": "Temperature",  "unite": "°C",   "min": 0, "max": 50,  "seuils": SEUILS_TEMP},
            {"valeur": round(float(meteo.get("humidite_air", 0)), 1), "titre": "Humidite air", "unite": "%",    "min": 0, "max": 100, "seuils": SEUILS_HUM},
            {"valeur": round(float(meteo.get("vitesse_vent", 0)), 1), "titre": "Vent",         "unite": "km/h", "min": 0, "max": 60,  "seuils": SEUILS_VENT},
            {"valeur": round(float(meteo.get("pluie",        0)), 1), "titre": "Pluie",        "unite": "mm",   "min": 0, "max": 30,  "seuils": SEUILS_PLUIE},
        ])

    if esp32 and lecture:
        afficher_jauges("Capteurs ESP32 en temps reel", [
            {"valeur": round(float(lecture.get("humidite_sol", 0)), 1), "titre": "Humidite sol",  "unite": "%",  "min": 0, "max": 100, "seuils": SEUILS_SOL},
            {"valeur": round(float(lecture.get("temperature",  0)), 1), "titre": "Temperature",   "unite": "°C", "min": 0, "max": 50,  "seuils": SEUILS_TEMP},
            {"valeur": round(float(lecture.get("humidite_air", 0)), 1), "titre": "Humidite air",  "unite": "%",  "min": 0, "max": 100, "seuils": SEUILS_HUM},
            {"valeur": round(float(lecture.get("pluie",        0)), 1), "titre": "Pluie capteur", "unite": "mm", "min": 0, "max": 30,  "seuils": SEUILS_PLUIE},
        ])
    elif not esp32:
        st.markdown("<div class='card' style='text-align:center;padding:24px'><p style='color:#9E9E9E;font-size:14px'>ESP32 hors ligne — jauges capteurs indisponibles.</p></div>", unsafe_allow_html=True)

    # Bouton de rafraichissement manuel (non-bloquant pour la sidebar)
    col_r1, col_r2, col_r3 = st.columns([1, 1, 1])
    with col_r2:
        if st.button("Rafraichir les donnees", key="refresh_dashboard"):
            st.rerun()
