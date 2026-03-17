"""
CACAO INTELLIGENT — Test visuel du dashboard
Lance avec : streamlit run dashboard/test_style.py
"""

import streamlit as st

st.set_page_config(
    page_title            = "Cacao Intelligent",
    page_icon             = "C",
    layout                = "wide",
    initial_sidebar_state = "expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=DM+Sans:wght@300;400;500&display=swap');

    :root {
        --cacao-dark    : #2C1810;
        --cacao-brown   : #6B3A2A;
        --cacao-caramel : #C17F3E;
        --cacao-gold    : #E8A84C;
        --cacao-green   : #2D5016;
        --cacao-leaf    : #4A7C2F;
        --cacao-light   : #F5ECD7;
        --cacao-cream   : #FBF5E6;
    }

    .stApp {
        background-color : var(--cacao-cream);
        font-family      : 'DM Sans', sans-serif;
    }

    section[data-testid="stSidebar"] {
        background   : linear-gradient(180deg, var(--cacao-dark) 0%, var(--cacao-brown) 100%);
        border-right : 3px solid var(--cacao-caramel);
    }
    section[data-testid="stSidebar"] * { color: var(--cacao-light) !important; }

    header[data-testid="stHeader"] { display: none; }
    #MainMenu { visibility: hidden; }
    footer    { visibility: hidden; }

    h1, h2, h3 {
        font-family : 'Playfair Display', serif !important;
        color       : var(--cacao-dark) !important;
    }

    .card {
        background    : #FFFFFF;
        border-radius : 14px;
        padding       : 24px 28px;
        border-left   : 5px solid var(--cacao-caramel);
        box-shadow    : 0 2px 16px rgba(44, 24, 16, 0.07);
        margin-bottom : 16px;
    }
    .card-green { border-left-color: var(--cacao-leaf); }
    .card-red   { border-left-color: #C0392B; }

    .card-title {
        font-family   : 'Playfair Display', serif;
        font-size     : 18px;
        font-weight   : 700;
        color         : var(--cacao-dark);
        margin-bottom : 16px;
    }
    .card-row {
        display         : flex;
        justify-content : space-between;
        align-items     : center;
        padding         : 8px 0;
        border-bottom   : 1px solid #F0E8D8;
        font-size       : 14px;
        color           : var(--cacao-dark);
    }
    .card-row:last-child { border-bottom: none; }

    .badge-ok {
        background    : #E8F5E9;
        color         : #1B5E20;
        padding       : 3px 12px;
        border-radius : 20px;
        font-size     : 13px;
        font-weight   : 500;
    }
    .badge-err {
        background    : #FFEBEE;
        color         : #B71C1C;
        padding       : 3px 12px;
        border-radius : 20px;
        font-size     : 13px;
        font-weight   : 500;
    }
    .badge-warn {
        background    : #FFF8E1;
        color         : #E65100;
        padding       : 3px 12px;
        border-radius : 20px;
        font-size     : 13px;
        font-weight   : 500;
    }

    .header-banner {
        background    : linear-gradient(135deg, var(--cacao-dark) 0%, var(--cacao-brown) 70%, var(--cacao-caramel) 100%);
        border-radius : 16px;
        padding       : 28px 36px;
        margin-bottom : 28px;
    }
    .header-title {
        font-family : 'Playfair Display', serif;
        font-size   : 32px;
        font-weight : 700;
        color       : var(--cacao-light);
        margin      : 0 0 6px 0;
    }
    .header-sub {
        font-size : 14px;
        color     : var(--cacao-gold);
        margin    : 0;
    }

    .action-box {
        border-radius : 14px;
        padding       : 28px;
        text-align    : center;
        margin-bottom : 16px;
    }
    .action-irriguer   { background:#EBF5FB; border: 2px solid #1A5276; }
    .action-pulveriser { background:#FEF9E7; border: 2px solid #784212; }
    .action-manuelle   { background:#FDEDEC; border: 2px solid #78281F; }
    .action-rien       { background:#EAFAF1; border: 2px solid #1E8449; }

    .action-title {
        font-family : 'Playfair Display', serif;
        font-size   : 26px;
        font-weight : 700;
        margin      : 0 0 6px 0;
    }
    .action-sub { font-size: 14px; margin: 0; }

    .confiance-label {
        font-size     : 14px;
        font-weight   : 500;
        color         : var(--cacao-dark);
        margin-bottom : 6px;
    }
    .confiance-bar {
        background    : #E8DDD0;
        border-radius : 8px;
        height        : 10px;
        overflow      : hidden;
        margin-bottom : 10px;
    }
    .confiance-fill {
        height        : 10px;
        border-radius : 8px;
        background    : linear-gradient(90deg, var(--cacao-leaf), var(--cacao-gold));
    }
    .confiance-fill-red {
        height        : 10px;
        border-radius : 8px;
        background    : linear-gradient(90deg, #C0392B, #E74C3C);
    }

    .stButton > button {
        background    : linear-gradient(135deg, var(--cacao-green), var(--cacao-leaf));
        color         : white !important;
        border        : none;
        border-radius : 10px;
        font-family   : 'DM Sans', sans-serif;
        font-weight   : 500;
        font-size     : 15px;
        padding       : 12px 32px;
        width         : 100%;
        transition    : all 0.2s;
        box-shadow    : 0 4px 12px rgba(45,80,22,0.25);
    }
    .stButton > button:hover {
        transform  : translateY(-2px);
        box-shadow : 0 6px 18px rgba(45,80,22,0.35);
    }

    .sidebar-logo {
        text-align    : center;
        padding       : 24px 0 16px;
        border-bottom : 1px solid #6B3A2A;
        margin-bottom : 16px;
    }
    .sidebar-app-name {
        font-family : 'Playfair Display', serif;
        font-size   : 19px;
        font-weight : 700;
        color       : var(--cacao-gold);
    }
    .sidebar-app-sub {
        font-size  : 11px;
        color      : #C17F3E;
        margin-top : 4px;
    }
    .sidebar-status {
        font-size      : 12px;
        color          : #C17F3E;
        text-align     : center;
        padding        : 16px 0;
        border-top     : 1px solid #6B3A2A;
        margin-top     : 16px;
        line-height    : 2;
    }
</style>
""", unsafe_allow_html=True)


# -- SIDEBAR --------------------------------------------------
with st.sidebar:
    st.markdown("""
    <div class='sidebar-logo'>
        <div class='sidebar-app-name'>Cacao Intelligent</div>
        <div class='sidebar-app-sub'>AgriTech Innovators — ESATIC</div>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "Navigation",
        ["Accueil", "Irrigation", "Pulverisation",
         "Detection Maladie", "Decision Combinee"],
        label_visibility = "collapsed"
    )

    st.markdown("""
    <div class='sidebar-status'>
        API &nbsp; en ligne<br>
        SMS &nbsp; actif<br>
        <br>
        v6 · Digital ID Africa 2026
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# PAGE ACCUEIL
# ============================================================
if page == "Accueil":

    st.markdown("""
    <div class='header-banner'>
        <p class='header-title'>Tableau de Bord</p>
        <p class='header-sub'>
            Systeme IoT d'irrigation et pulverisation intelligente — Soubre, Cote d'Ivoire
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class='card'>
            <div class='card-title'>Statut des Modules</div>
            <div class='card-row'>
                <span>Modele Irrigation</span>
                <span class='badge-ok'>Charge</span>
            </div>
            <div class='card-row'>
                <span>Modele Pesticide</span>
                <span class='badge-ok'>Charge</span>
            </div>
            <div class='card-row'>
                <span>Modele Maladie (82.7%)</span>
                <span class='badge-ok'>Charge</span>
            </div>
            <div class='card-row'>
                <span>SMS Twilio</span>
                <span class='badge-ok'>Actif</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class='card card-green'>
            <div class='card-title'>Contexte Actuel</div>
            <div class='card-row'>
                <span>Zone</span>
                <b>Soubre, Cote d'Ivoire</b>
            </div>
            <div class='card-row'>
                <span>Saison</span>
                <b>Grande saison seche</b>
            </div>
            <div class='card-row'>
                <span>Temperature</span>
                <b>31 C</b>
            </div>
            <div class='card-row'>
                <span>Humidite air</span>
                <b>68 %</b>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ============================================================
# PAGE IRRIGATION
# ============================================================
elif page == "Irrigation":

    st.markdown("""
    <div class='header-banner'>
        <p class='header-title'>Decision Irrigation</p>
        <p class='header-sub'>Saisir les donnees capteurs ESP32 pour obtenir une recommandation</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='card-title'>Donnees Capteurs</div>", unsafe_allow_html=True)
        temp    = st.number_input("Temperature (C)",     value=31.0, step=0.5)
        hum_air = st.number_input("Humidite air (%)",    value=68.0, step=1.0)
        hum_sol = st.number_input("Humidite sol (%)",    value=28.0, step=1.0)
        vent    = st.number_input("Vitesse vent (km/h)", value=5.0,  step=0.5)
        pluie   = st.number_input("Pluie actuelle (mm)", value=0.0,  step=0.1)
        btn     = st.button("Analyser l'irrigation")
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        if btn:
            st.markdown("""
            <div class='action-box action-irriguer'>
                <p class='action-title' style='color:#1A5276'>IRRIGUER</p>
                <p class='action-sub' style='color:#2874A6'>Activer la pompe maintenant</p>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("""
            <div class='card'>
                <div class='card-title'>Resultat</div>
                <div class='confiance-label'>Confiance : 91.2%</div>
                <div class='confiance-bar'>
                    <div class='confiance-fill' style='width:91.2%'></div>
                </div>
                <div class='card-row'><span>SMS envoye</span><span class='badge-ok'>Oui</span></div>
                <div class='card-row'><span>Parcelle</span><b>Soubre 5.7833, -6.5833</b></div>
                <div class='card-row'><span>Saison</span><b>Grande saison seche</b></div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class='card' style='text-align:center; padding:60px 24px'>
                <p style='color:#9E9E9E; font-size:15px'>
                    Remplissez les donnees capteurs<br>et cliquez sur Analyser
                </p>
            </div>
            """, unsafe_allow_html=True)


# ============================================================
# PAGE PULVERISATION
# ============================================================
elif page == "Pulverisation":

    st.markdown("""
    <div class='header-banner'>
        <p class='header-title'>Decision Pulverisation</p>
        <p class='header-sub'>Conditions meteo pour traitement phytosanitaire optimal</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='card-title'>Donnees Capteurs</div>", unsafe_allow_html=True)
        temp    = st.number_input("Temperature (C)",     value=27.0, step=0.5, key="p_temp")
        hum_air = st.number_input("Humidite air (%)",    value=72.0, step=1.0, key="p_hair")
        vent    = st.number_input("Vitesse vent (km/h)", value=5.0,  step=0.5, key="p_vent")
        pluie   = st.number_input("Pluie actuelle (mm)", value=0.0,  step=0.1, key="p_plui")
        btn_p   = st.button("Analyser la pulverisation")
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        if btn_p:
            st.markdown("""
            <div class='action-box action-pulveriser'>
                <p class='action-title' style='color:#784212'>PULVERISER</p>
                <p class='action-sub' style='color:#935116'>Conditions optimales — agir maintenant</p>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("""
            <div class='card'>
                <div class='card-title'>Resultat</div>
                <div class='confiance-label'>Confiance : 94.1%</div>
                <div class='confiance-bar'>
                    <div class='confiance-fill' style='width:94.1%'></div>
                </div>
                <div class='card-row'><span>Risque pourriture brune</span><span class='badge-warn'>Modere</span></div>
                <div class='card-row'><span>Risque mirides</span><span class='badge-ok'>Faible</span></div>
                <div class='card-row'><span>SMS envoye</span><span class='badge-ok'>Oui</span></div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class='card' style='text-align:center; padding:60px 24px'>
                <p style='color:#9E9E9E; font-size:15px'>
                    Remplissez les donnees<br>et cliquez sur Analyser
                </p>
            </div>
            """, unsafe_allow_html=True)


# ============================================================
# PAGE DETECTION MALADIE
# ============================================================
elif page == "Detection Maladie":

    st.markdown("""
    <div class='header-banner'>
        <p class='header-title'>Detection de Maladie</p>
        <p class='header-sub'>Photographier une cabosse pour analyse IA — MobileNetV2 82.7%</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='card-title'>Upload Photo</div>", unsafe_allow_html=True)
        photo = st.file_uploader(
            "Photo cabosse",
            type             = ["jpg", "jpeg", "png"],
            label_visibility = "collapsed"
        )
        if photo:
            st.image(photo, use_container_width=True)
        btn_m = st.button("Analyser la cabosse")
        st.markdown("""
        <div style='margin-top:16px; padding:14px; background:#FFF8E1;
                    border-radius:10px; font-size:13px; color:#5D4037'>
            <b>Conseils photo</b><br>
            Cadrer uniquement la cabosse<br>
            Distance 20-30 cm<br>
            Bonne luminosite, sans ombre<br>
            Eviter le flou
        </div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        if btn_m and photo:
            st.markdown("""
            <div class='action-box action-pulveriser'>
                <p class='action-title' style='color:#784212'>BLACKPOD</p>
                <p class='action-sub' style='color:#935116'>Pourriture brune detectee</p>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("""
            <div class='card card-red'>
                <div class='card-title'>Resultat Analyse</div>
                <div class='confiance-label'>Confiance : 87.3%</div>
                <div class='confiance-bar'>
                    <div class='confiance-fill-red' style='width:87.3%'></div>
                </div>
                <div class='card-row'><span>Action requise</span><b>Pulveriser fongicide 24h</b></div>
                <div class='card-row'><span>Gravite</span><span class='badge-err'>Critique</span></div>
                <div class='card-row'><span>Source</span><b>Cahiers Agricultures 2024</b></div>
                <div class='card-row'><span>SMS envoye</span><span class='badge-ok'>Oui</span></div>
            </div>
            <div class='card'>
                <div class='card-title'>Probabilites par classe</div>
                <div class='confiance-label'>BLACKPOD — 87.3%</div>
                <div class='confiance-bar'><div class='confiance-fill-red' style='width:87.3%'></div></div>
                <div class='confiance-label'>FROSTYPOD — 6.1%</div>
                <div class='confiance-bar'><div class='confiance-fill' style='width:6.1%'></div></div>
                <div class='confiance-label'>HEALTHY — 4.2%</div>
                <div class='confiance-bar'><div class='confiance-fill' style='width:4.2%'></div></div>
                <div class='confiance-label'>MIRID — 2.4%</div>
                <div class='confiance-bar'><div class='confiance-fill' style='width:2.4%'></div></div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class='card' style='text-align:center; padding:60px 24px'>
                <p style='color:#9E9E9E; font-size:15px'>
                    Uploadez une photo de cabosse<br>et cliquez sur Analyser
                </p>
            </div>
            """, unsafe_allow_html=True)


# ============================================================
# PAGE DECISION COMBINEE
# ============================================================
elif page == "Decision Combinee":

    st.markdown("""
    <div class='header-banner'>
        <p class='header-title'>Decision Combinee</p>
        <p class='header-sub'>Route principale ESP32 — Irrigation + Pulverisation + Gestion conflits</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='card-title'>Donnees Capteurs</div>", unsafe_allow_html=True)
        temp    = st.number_input("Temperature (C)",     value=29.0, step=0.5, key="d_temp")
        hum_air = st.number_input("Humidite air (%)",    value=72.0, step=1.0, key="d_hair")
        hum_sol = st.number_input("Humidite sol (%)",    value=35.0, step=1.0, key="d_hsol")
        vent    = st.number_input("Vitesse vent (km/h)", value=5.0,  step=0.5, key="d_vent")
        pluie   = st.number_input("Pluie actuelle (mm)", value=0.0,  step=0.1, key="d_plui")
        maladie = st.selectbox(
            "Maladie detectee (optionnel)",
            ["Aucune (automatique)", "BLACKPOD", "FROSTYPOD", "HEALTHY", "MIRID"]
        )
        btn_d = st.button("Obtenir la decision")
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        if btn_d:
            st.markdown("""
            <div class='action-box action-pulveriser'>
                <p class='action-title' style='color:#784212'>PULVERISER</p>
                <p class='action-sub' style='color:#935116'>Activer le pulverisateur</p>
            </div>
            """, unsafe_allow_html=True)

            c1, c2 = st.columns(2)
            with c1:
                st.markdown("""
                <div class='card'>
                    <div class='card-title'>Irrigation</div>
                    <span class='badge-warn'>Bloquee</span>
                    <div class='card-row'><span>Raison</span><b>Priorite pesticide</b></div>
                    <div class='card-row'><span>Attendre</span><b>48 heures</b></div>
                </div>
                """, unsafe_allow_html=True)
            with c2:
                st.markdown("""
                <div class='card card-green'>
                    <div class='card-title'>Pulverisation</div>
                    <span class='badge-ok'>Recommandee</span>
                    <div class='card-row'><span>Confiance</span><b>94.1%</b></div>
                    <div class='card-row'><span>SMS</span><span class='badge-ok'>Envoye</span></div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class='card' style='text-align:center; padding:60px 24px'>
                <p style='color:#9E9E9E; font-size:15px'>
                    Remplissez les donnees capteurs<br>et cliquez sur Decider
                </p>
            </div>
            """, unsafe_allow_html=True)
CI-96F0ED4C