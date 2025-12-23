import streamlit as st

st.set_page_config(
    page_title="Immobilier & Climat – Vue d’ensemble",
    layout="wide"
)

# =========================
# STYLE (corrigé, lisible, sans barres)
# =========================

st.markdown("""
<style>

/* Centrage général */
.center {
    text-align: center;
}

/* Cartes */
.card {
    padding: 24px 26px;
    border-radius: 16px;
    border: 3px solid;
    height: 100%;
}

/* IMPORTANT : forcer la couleur du texte (thème sombre Streamlit) */
.card, .card * {
    color: #000000;
}

/* Carte climat */
.card-climat {
    background-color: #e3f0ff;
    border-color: #2f6fd6;
}

/* Carte immobilier */
.card-immo {
    background-color: #eef6e6;
    border-color: #558b2f;
}

.card-title {
    font-size: 1.25rem;
    font-weight: 800;
    margin-bottom: 12px;
}

/* Espacement vertical */
.section {
    margin-top: 32px;
    margin-bottom: 32px;
}

</style>
""", unsafe_allow_html=True)

# =========================
# TITRE + INTRO
# =========================

st.markdown(
    "<h1 class='center'>Immobilier & Climat : Vue d’ensemble</h1>",
    unsafe_allow_html=True
)

st.markdown(
    "<p class='center'>"
    "Ce tableau de bord analyse les interactions entre le marché immobilier "
    "et les facteurs climatiques pour mieux comprendre les enjeux et les impacts à long terme."
    "</p>",
    unsafe_allow_html=True
)

# =========================
# À QUOI SERT LE DASHBOARD (CENTRÉ)
# =========================

st.markdown("<div class='section'></div>", unsafe_allow_html=True)

st.markdown(
    "<h3 class='center'>À quoi sert ce tableau de bord ?</h3>",
    unsafe_allow_html=True
)

st.markdown("""
<p class='center'>Comprendre les tendances du marché immobilier</p>
<p class='center'>Evaluer les risques climatiques</p>
<p class='center'>Identifier les zones à enjeux ou à opportunités</p>
<p class='center'>Aider à la prise de décision (investissement, aménagement, prévention)</p>
""", unsafe_allow_html=True)

# =========================
# DEUX CARTES ANALYTIQUES
# =========================

st.markdown("<div class='section'></div>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="card card-climat">
        <div class="card-title">Analyse climatique</div>
        Etudiez les indicateurs climatiques :
        <ul>
            <li>Températures</li>
            <li>Précipitations</li>
            <li>Evénements extrêmes</li>
            <li>Niveaux de risque</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="card card-immo">
        <div class="card-title">Analyse immobilière</div>
        Explorez les données immobilières :
        <ul>
            <li>Prix au m²</li>
            <li>Transactions</li>
            <li>Types de biens</li>
            <li>Évolution du marché</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# =========================
# POURQUOI CROISER
# =========================

st.markdown("<div class='section'></div>", unsafe_allow_html=True)

st.markdown(
    "<h3 class='center'>Pourquoi croiser climat et immobilier ?</h3>",
    unsafe_allow_html=True
)

st.markdown(
    "<p class='center'>"
    "Les conditions climatiques influencent la valeur des biens et l’attractivité des territoires. "
    "Une analyse croisée permet d’anticiper les évolutions futures et de mieux comprendre "
    "les dynamiques territoriales."
    "</p>",
    unsafe_allow_html=True
)

# =========================
# COMMENT UTILISER
# =========================

st.markdown("<div class='section'></div>", unsafe_allow_html=True)

st.markdown(
    "<h3 class='center'>Comment utiliser le tableau de bord ?</h3>",
    unsafe_allow_html=True
)

st.markdown("""
<p class='center'>1. Commencez par la vue d’ensemble</p>
<p class='center'>2. Consultez la page climatique</p>
<p class='center'>3. Explorez la page immobilière</p>
<p class='center'>4. Croisez les informations pour interpréter les résultats</p>
""", unsafe_allow_html=True)
