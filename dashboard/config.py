"""
CACAO INTELLIGENT — Configuration
Toutes les constantes du projet en un seul endroit.
Modifier ce fichier suffit pour adapter l'ensemble du dashboard.
"""

# ============================================================
# API
# ============================================================
API_BASE_URL = "http://localhost:5000"
API_TIMEOUT  = 10  # secondes

ROUTES = {
    "statut"           : f"{API_BASE_URL}/",
    "meteo"            : f"{API_BASE_URL}/meteo",
    "predire"          : f"{API_BASE_URL}/predire",
    "pulveriser"       : f"{API_BASE_URL}/pulveriser",
    "decider"          : f"{API_BASE_URL}/decider",
    "analyser"         : f"{API_BASE_URL}/analyser",
    "derniere_lecture" : f"{API_BASE_URL}/derniere_lecture",
}

# ============================================================
# LOCALISATION
# ============================================================
LAT_DEFAUT = 5.3096
LON_DEFAUT = -4.0126
VILLE      = "Abidjan, Cote d'Ivoire"

# ============================================================
# MODELE
# ============================================================
CLASSES_MALADIE = ["BLACKPOD", "FROSTYPOD", "HEALTHY", "MIRID"]
SEUIL_CONFIANCE = 60.0  # %

# ============================================================
# NAVIGATION
# ============================================================
PAGES = ["Dashboard", "Decision", "Profil", "Traçabilité"]

# ============================================================
# SAISONS
# ============================================================
NOMS_SAISONS = {
    0: "Grande saison seche",
    1: "Grande saison des pluies",
    2: "Petite saison seche",
    3: "Petite saison des pluies",
}

# ============================================================
# CSS GLOBAL
# ============================================================
CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=DM+Sans:wght@300;400;500&display=swap');

    :root {
        --dark    : #2C1810;
        --brown   : #6B3A2A;
        --caramel : #C17F3E;
        --gold    : #E8A84C;
        --green   : #2D5016;
        --leaf    : #4A7C2F;
        --light   : #F5ECD7;
        --cream   : #FBF5E6;
    }

    /* Fond general */
    .stApp {
        background-color : var(--cream);
        font-family      : 'DM Sans', sans-serif;
    }

    /* Masquer elements Streamlit par defaut */
    #MainMenu { visibility: hidden; }
    footer    { visibility: hidden; }

    /* Garder le header UNIQUEMENT pour le bouton sidebar (masquer le reste) */
    header[data-testid="stHeader"] {
        background: transparent !important;
        border: none !important;
    }
    /* Masquer le bouton Deploy et toolbar */
    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    .stDeployButton { display: none !important; }

    /* Style de la sidebar (couleurs, bordures) - s'applique partout */
    section[data-testid="stSidebar"] {
        background   : linear-gradient(180deg, var(--dark) 0%, var(--brown) 100%) !important;
        border-right : 3px solid var(--caramel) !important;
    }

    /* Forcer la sidebar a rester visible et fixe UNIQUEMENT sur grand ecran */
    @media (min-width: 768px) {
        section[data-testid="stSidebar"] {
            display: flex !important;
            width: 280px !important;
            min-width: 280px !important;
            transform: none !important;
            opacity: 1 !important;
            visibility: visible !important;
            z-index: 999 !important;
        }
    }

    /* Toujours permettre l'usage du bouton toggle sur mobile */
    button[data-testid="stSidebarCollapseButton"],
    button[data-testid="collapsedControl"] {
        color: var(--caramel) !important;
    }

    /* Masquer UNIQUEMENT la nav automatique Streamlit sans toucher aux radio */
    [data-testid="stSidebarNavItems"]    { display: none !important; }
    [data-testid="stSidebarNavSeparator"]{ display: none !important; }
    [data-testid="stSidebarNavLink"]     { display: none !important; }

    /* Titres */
    h1, h2, h3 {
        font-family : 'Playfair Display', serif !important;
        color       : var(--dark) !important;
    }

    /* ---- SIDEBAR ----------------------------------------- */
    section[data-testid="stSidebar"] * {
        color : var(--light) !important;
    }
    section[data-testid="stSidebar"] .stRadio label p {
        color       : var(--light) !important;
        font-size   : 14px !important;
        font-family : 'DM Sans', sans-serif !important;
    }
    section[data-testid="stSidebar"] .stRadio input[type="radio"]:checked + div {
        background-color : var(--caramel) !important;
        border-color     : var(--caramel) !important;
    }
    section[data-testid="stSidebar"] .stRadio label:hover p {
        color : var(--gold) !important;
    }
    .sidebar-logo {
        text-align    : center;
        padding       : 24px 0 16px;
        border-bottom : 1px solid #6B3A2A;
        margin-bottom : 16px;
    }
    .sidebar-app-name {
        font-family : 'Playfair Display', serif;
        font-size   : 20px;
        font-weight : 700;
        color       : var(--gold) !important;
    }
    .sidebar-app-sub {
        font-size  : 11px;
        color      : var(--caramel) !important;
        margin-top : 4px;
    }
    .sidebar-status {
        font-size   : 12px;
        color       : var(--caramel) !important;
        text-align  : center;
        padding     : 16px 0;
        border-top  : 1px solid #6B3A2A;
        margin-top  : 16px;
        line-height : 2;
    }

    /* ---- HEADER BANNER ----------------------------------- */
    .header-banner {
        background    : linear-gradient(135deg, var(--dark) 0%, var(--brown) 70%, var(--caramel) 100%);
        border-radius : 16px;
        padding       : 28px 36px;
        margin-bottom : 28px;
    }
    .header-title {
        font-family : 'Playfair Display', serif;
        font-size   : 32px;
        font-weight : 700;
        color       : var(--light) !important;
        margin      : 0 0 6px 0;
    }
    .header-sub {
        font-size : 14px;
        color     : var(--gold) !important;
        margin    : 0;
    }

    /* ---- CARDS ------------------------------------------- */
    .card {
        background    : #FFFFFF;
        border-radius : 14px;
        padding       : 24px 28px;
        border-left   : 5px solid var(--caramel);
        box-shadow    : 0 2px 16px rgba(44,24,16,0.07);
        margin-bottom : 16px;
    }
    .card-green { border-left-color: var(--leaf); }
    .card-red   { border-left-color: #C0392B; }
    .card-blue  { border-left-color: #1A5276; }

    .card-title {
        font-family   : 'Playfair Display', serif;
        font-size     : 18px;
        font-weight   : 700;
        color         : var(--dark) !important;
        margin-bottom : 16px;
    }
    .card-row {
        display         : flex;
        justify-content : space-between;
        align-items     : center;
        padding         : 8px 0;
        border-bottom   : 1px solid #F0E8D8;
        font-size       : 14px;
        color           : var(--dark) !important;
    }
    .card-row:last-child { border-bottom: none; }

    /* ---- BADGES ------------------------------------------ */
    .badge-ok {
        background    : #E8F5E9;
        color         : #1B5E20 !important;
        padding       : 3px 12px;
        border-radius : 20px;
        font-size     : 13px;
        font-weight   : 500;
    }
    .badge-err {
        background    : #FFEBEE;
        color         : #B71C1C !important;
        padding       : 3px 12px;
        border-radius : 20px;
        font-size     : 13px;
        font-weight   : 500;
    }
    .badge-warn {
        background    : #FFF8E1;
        color         : #E65100 !important;
        padding       : 3px 12px;
        border-radius : 20px;
        font-size     : 13px;
        font-weight   : 500;
    }

    /* ---- ACTION BOXES ------------------------------------ */
    .action-box {
        border-radius : 14px;
        padding       : 28px;
        text-align    : center;
        margin-bottom : 16px;
    }
    .action-irriguer   { background:#EBF5FB; border:2px solid #1A5276; }
    .action-pulveriser { background:#FEF9E7; border:2px solid #784212; }
    .action-manuelle   { background:#FDEDEC; border:2px solid #78281F; }
    .action-rien       { background:#EAFAF1; border:2px solid #1E8449; }

    .action-title {
        font-family : 'Playfair Display', serif;
        font-size   : 26px;
        font-weight : 700;
        margin      : 0 0 6px 0;
    }
    .action-sub { font-size: 14px; margin: 0; }

    /* ---- BARRES DE CONFIANCE ----------------------------- */
    .confiance-label {
        font-size     : 14px;
        font-weight   : 500;
        color         : var(--dark) !important;
        margin-bottom : 4px;
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
        background    : linear-gradient(90deg, var(--leaf), var(--gold));
    }
    .confiance-fill-red {
        height        : 10px;
        border-radius : 8px;
        background    : linear-gradient(90deg, #C0392B, #E74C3C);
    }
    .confiance-fill-blue {
        height        : 10px;
        border-radius : 8px;
        background    : linear-gradient(90deg, #1A5276, #2E86C1);
    }

    /* ---- BOUTONS ----------------------------------------- */
    .stButton > button {
        background    : linear-gradient(135deg, var(--green), var(--leaf));
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

    /* ---- ONGLETS LOGIN ----------------------------------- */
    div[data-testid="stTabs"] button[role="tab"] {
        color       : #6B3A2A !important;
        font-size   : 15px !important;
        font-weight : 500 !important;
        font-family : 'DM Sans', sans-serif !important;
    }
    div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
        color        : #C17F3E !important;
        font-weight  : 700 !important;
        border-bottom: 2px solid #C17F3E !important;
    }
    div[data-testid="stTabs"] button[role="tab"]:hover {
        color : #E8A84C !important;
    }
    div[data-testid="stTextInput"] label p,
    div[data-testid="stNumberInput"] label p,
    div[data-testid="stSelectbox"] label p,
    div[data-testid="stFileUploader"] label p {
        color       : var(--dark) !important;
        font-family : 'DM Sans', sans-serif !important;
        font-size   : 14px !important;
        font-weight : 500 !important;
    }
    /* Forcer fond blanc sur tous les inputs texte */
    div[data-testid="stTextInput"] input,
    div[data-testid="stTextInput"] input[type="text"],
    div[data-testid="stTextInput"] input[type="password"] {
        border-radius    : 8px !important;
        border           : 1.5px solid #D5C9B8 !important;
        background-color : #FFFFFF !important;
        color            : #2C1810 !important;
        font-family      : 'DM Sans', sans-serif !important;
    }
    div[data-testid="stTextInput"] input:focus,
    div[data-testid="stTextInput"] input[type="password"]:focus {
        border-color : #C17F3E !important;
        box-shadow   : 0 0 0 2px rgba(193,127,62,0.15) !important;
        outline      : none !important;
    }
    .stNumberInput input {
        border-radius : 8px !important;
        border        : 1.5px solid #D5C9B8 !important;
        font-family   : 'DM Sans', sans-serif !important;
        color         : var(--dark) !important;
        background    : #FFFFFF !important;
    }
    .stNumberInput input:disabled {
        background : var(--light) !important;
        color      : var(--brown) !important;
        cursor     : not-allowed;
    }

    /* ---- ALERTES ----------------------------------------- */
    .alerte-conflit {
        background    : #FFF3CD;
        border        : 1.5px solid #FFC107;
        border-radius : 10px;
        padding       : 14px 18px;
        font-size     : 14px;
        color         : #856404 !important;
        margin-bottom : 16px;
    }
    .api-error {
        background    : #FFEBEE;
        border        : 1.5px solid #EF9A9A;
        border-radius : 10px;
        padding       : 16px 20px;
        color         : #B71C1C !important;
        font-size     : 14px;
        margin-bottom : 16px;
    }
</style>
"""
