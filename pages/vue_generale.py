import streamlit as st

st.set_page_config(
    page_title="Immobilier & Climat – Vue d’ensemble",
    layout="wide"
)

# =========================
# STYLE VISUEL (léger, attractif)
# =========================

st.markdown("""
<style>
.center {
    text-align: center;
}

.section {
    margin-top: 30px;
    margin-bottom: 30px;
}

.card {
    padding: 20px 24px;
    border-radius: 14px;
    border: 2px solid #dcdcdc;
    height: 100%;
}

.card-climat {
    background-color: #f0f6ff;
    border-color: #4a90e2;
}

.card-immo {
    background-color: #f6f9f0;
    border-color: #7cb342;
}


.card-title {
    font-size: 1.2rem;
    font-weight: 700;
    margin-bottom: 10px;
}

.hr {
    border-top: 2px solid #000000;
    margin: 30px 0;
}
</style>
""", unsafe_allow_html=True)

# =========================
# TITRE + INTRO
# =========================

st.markdown("<h1 class='center'>Immobilier & Climat : Vue d’ensemble</h1>", unsafe_allow_html=True)

st.markdown(
    "<p class='center'>"
    "Ce tableau de bord analyse les interactions entre le marché immobilier "
    "et les facteurs climatiques pour mieux comprendre les enjeux et les impacts à long terme."
    "</p>",
    unsafe_allow_html=True
)

st.markdown("<div class='hr'></div>", unsafe_allow_html=True)

# =========================
# À QUOI SERT LE DASHBOARD (CENTRÉ)
# =========================

st.markdown("<h3 class='center'>À quoi sert ce tableau de bord ?</h3>", unsafe_allow_html=True)

st.markdown("""
<p class='center'>Comprendre les tendances du marché immobilier</p>
<p class='center'>Évaluer les risques climatiques</p>
<p class='center'>Identifier les zones à enjeux ou à opportunités</p>
<p class='center'>Aider à la prise de décision (investissement, aménagement, prévention)</p>
""", unsafe_allow_html=True)

st.markdown("<div class='hr'></div>", unsafe_allow_html=True)

# =========================
# DEUX ANALYSES ENCADRÉES
# =========================

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="card card-climat">
        <div class="card-title">Analyse climatique</div>
        Étudiez les indicateurs climatiques :
        <ul>
            <li>Températures</li>
            <li>Précipitations</li>
            <li>Événements extrêmes</li>
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

st.markdown("<div class='hr'></div>", unsafe_allow_html=True)

# =========================
# POURQUOI CROISER
# =========================

st.markdown("<h3 class='center'>Pourquoi croiser climat et immobilier ?</h3>", unsafe_allow_html=True)

st.markdown(
    "<p class='center'>"
    "Les conditions climatiques influencent la valeur des biens et l’attractivité des territoires. "
    "Une analyse croisée permet d’anticiper les évolutions futures et de mieux comprendre les dynamiques locales."
    "</p>",
    unsafe_allow_html=True
)

st.markdown("<div class='hr'></div>", unsafe_allow_html=True)

# =========================
# COMMENT UTILISER
# =========================

st.markdown("<h3 class='center'>Comment utiliser le tableau de bord ?</h3>", unsafe_allow_html=True)

st.markdown("""
<p class='center'>1. Commencez par la vue d’ensemble</p>
<p class='center'>2. Consultez la page climatique</p>
<p class='center'>3. Explorez la page immobilière</p>
<p class='center'>4. Croisez les informations pour interpréter les résultats</p>
""", unsafe_allow_html=True)
