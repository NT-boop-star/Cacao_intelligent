"""
CACAO INTELLIGENT — Widgets
UN seul st.markdown() par widget. HTML compact (pas d'indentation 4 espaces).
"""
import streamlit as st

def header_banner(titre, sous_titre):
    st.markdown(f"<div class='header-banner'><p class='header-title'>{titre}</p><p class='header-sub'>{sous_titre}</p></div>", unsafe_allow_html=True)

def badge(texte, type="ok"):
    return f"<span class='badge-{type}'>{texte}</span>"

def card(titre, lignes, couleur="caramel", extra_html=""):
    """Affiche une card complete en UN seul st.markdown(). lignes = liste de (label, valeur_html)."""
    classes = {"caramel": "card", "green": "card card-green", "red": "card card-red", "blue": "card card-blue"}
    cls  = classes.get(couleur, "card")
    rows = "".join(f"<div class='card-row'><span>{l}</span><span>{v}</span></div>" for l, v in lignes)
    st.markdown(f"<div class='{cls}'><div class='card-title'>{titre}</div>{extra_html}{rows}</div>", unsafe_allow_html=True)

def barre_confiance(valeur, couleur="green"):
    fills = {"green": "confiance-fill", "red": "confiance-fill-red", "blue": "confiance-fill-blue"}
    f = fills.get(couleur, "confiance-fill")
    st.markdown(f"<div class='confiance-label'>Confiance : {valeur:.1f}%</div><div class='confiance-bar'><div class='{f}' style='width:{valeur}%'></div></div>", unsafe_allow_html=True)

def barres_probabilites(probabilites):
    couleurs = {"BLACKPOD": "confiance-fill-red", "FROSTYPOD": "confiance-fill-red", "HEALTHY": "confiance-fill", "MIRID": "confiance-fill-blue"}
    items  = sorted(probabilites.items(), key=lambda x: x[1], reverse=True)
    barres = ""
    for cls, val in items:
        fill = couleurs.get(cls, "confiance-fill")
        barres += f"<div class='confiance-label'>{cls} — {val:.1f}%</div><div class='confiance-bar'><div class='{fill}' style='width:{val}%'></div></div>"
    st.markdown(f"<div class='card'><div class='card-title'>Probabilites par classe</div>{barres}</div>", unsafe_allow_html=True)

def action_box(action, message=""):
    configs = {
        "IRRIGUER":        ("action-irriguer",   "IRRIGUER",       "#1A5276", message or "Activer la pompe maintenant",         "#2874A6"),
        "PULVERISER":      ("action-pulveriser",  "PULVERISER",     "#784212", message or "Activer le pulverisateur maintenant", "#935116"),
        "ACTION_MANUELLE": ("action-manuelle",    "ACTION MANUELLE","#78281F", message or "Intervention humaine requise",        "#922B21"),
        "AUCUNE_ACTION":   ("action-rien",        "AUCUNE ACTION",  "#1E8449", message or "Conditions optimales",               "#27AE60"),
    }
    classe, titre, couleur, sous, sous_col = configs.get(action, configs["AUCUNE_ACTION"])
    st.markdown(f"<div class='action-box {classe}'><p class='action-title' style='color:{couleur}'>{titre}</p><p class='action-sub' style='color:{sous_col}'>{sous}</p></div>", unsafe_allow_html=True)

def alerte_conflit(message):
    st.markdown(f"<div class='alerte-conflit'><b>Conflit detecte</b><br>{message}</div>", unsafe_allow_html=True)

def erreur_api(message):
    st.markdown(f"<div class='api-error'><b>API non disponible</b><br>{message}</div>", unsafe_allow_html=True)

def placeholder_vide(texte="Remplissez les donnees et cliquez sur Analyser"):
    st.markdown(f"<div class='card' style='text-align:center;padding:60px 24px'><p style='color:#9E9E9E;font-size:15px'>{texte}</p></div>", unsafe_allow_html=True)

def statut_esp32(en_ligne, horodatage=""):
    if en_ligne:
        st.markdown(f"<div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:16px'><span style='font-size:13px;color:#5D4037'>Derniere lecture — {horodatage}</span><span class='badge-ok'>ESP32 connecte</span></div>", unsafe_allow_html=True)
    else:
        st.markdown("<div style='margin-bottom:12px'><span class='badge-warn'>ESP32 hors ligne — saisie manuelle</span></div>", unsafe_allow_html=True)

def conseils_photo():
    st.markdown("<div style='margin-top:12px;padding:14px;background:#FFF8E1;border-radius:10px;font-size:13px;color:#5D4037'><b>Conseils photo</b><br>Cadrer uniquement la cabosse<br>Distance 20-30 cm — bonne luminosite<br>Eviter ombre et flou</div>", unsafe_allow_html=True)