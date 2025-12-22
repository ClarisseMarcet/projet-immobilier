import streamlit as st

st.set_page_config(
    page_title="Immobilier & Climat – Vue d’ensemble",
    layout="wide"
)

# =========================
# STYLE (noir / jaune, lisible)
# =========================

st.markdown("""
<style>
body {
    color: #000000;
}

.main-container {
    max-width: 1100px;
    margin: auto;
}

.title {
    font-size: 2.1rem;
    font-weight: 800;
    margin-bottom: 10px;
}

.subtitle {
    font-size: 1.05rem;
    margin-bottom: 26px;
    line-height: 1.6;
}

.section-title {
    font-size: 1.4rem;
    font-weight: 800;
    margin-top: 34px;
    margin-bottom: 14px;
}

.hr {
    border-top: 2px solid #000000;
    margin: 30px 0;
}

.list-item {
    margin-bottom: 8px;
    font-size: 1.05rem;
}

.grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 28px;
    margin-top: 18px;
}

.box {
    border: 2px solid #f1c40f;
    padding: 18px 22px;
}

.box-title {
    font-weight: 800;
    margin-bottom: 10px;
}

.highlight-box {
    border: 2px solid #f1c40f;
    padding: 18px 22px;
    margin-top: 18px;
}

.steps {
    margin-top: 10px;
}

.step {
    margin-bottom: 8px;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# =========================
# CONTENU
# =========================

st.markdown("<div class='main-container'>", unsafe_allow_html=True)

st.markdown("<div class='title'>Immobilier & Climat : Vue d’ensemble</div>", unsafe_allow_html=True)

st.markdown(
    "<div class='subtitle'>"
    "Ce tableau de bord analyse les interactions entre le marché immobilier et les facteurs climatiques "
    "pour mieux comprendre les enjeux et les impacts à long terme."
    "</div>",
    unsafe_allow_html=True
)

st.markdown("<div class='hr'></div>", unsafe_allow_html=True)

# =========================
# À quoi sert le dashboard
# =========================

st.markdown("<div class='section-title'>À quoi sert ce tableau de bord ?</div>", unsafe_allow_html=True)

st.markdown("""
<div class='list-item'>• Comprendre les tendances du marché immobilier</div>
<div class='list-item'>• Évaluer les risques climatiques</div>
<div class='list-item'>• Identifier les zones à enjeux ou à opportunités</div>
<div class='list-item'>• Aider à la prise de décision (investissement, aménagement, prévention)</div>
""", unsafe_allow_html=True)

# =========================
# Deux blocs Analyse
# =========================

st.markdown("<div class='grid'>", unsafe_allow_html=True)

st.markdown("""
<div class='box'>
    <div class='box-title'>Analyse climatique</div>
    Étudiez les indicateurs climatiques :
    <ul>
        <li>Températures</li>
        <li>Précipitations</li>
        <li>Événements extrêmes</li>
        <li>Niveaux de risque</li>
    </ul>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class='box'>
    <div class='box-title'>Analyse immobilière</div>
    Explorez les données immobilières :
    <ul>
        <li>Prix au m²</li>
        <li>Transactions</li>
        <li>Types de biens</li>
        <li>Évolution du marché</li>
    </ul>
</div>
""", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# =========================
# Pourquoi croiser climat / immobilier
# =========================

st.markdown("<div class='section-title'>Pourquoi croiser climat et immobilier ?</div>", unsafe_allow_html=True)

st.markdown("""
<div class='highlight-box'>
Les conditions climatiques impactent la valeur des biens et l’attractivité des territoires.
<br><br>
Une analyse croisée permet d’anticiper les évolutions à venir et de mieux comprendre
les dynamiques territoriales.
</div>
""", unsafe_allow_html=True)

# =========================
# Comment utiliser le dashboard
# =========================

st.markdown("<div class='section-title'>Comment utiliser le tableau de bord ?</div>", unsafe_allow_html=True)

st.markdown("""
<div class='steps'>
    <div class='step'>1. Commencez par la vue d’ensemble</div>
    <div class='step'>2. Consultez la page climatique</div>
    <div class='step'>3. Explorez la page immobilière</div>
    <div class='step'>4. Croisez les informations pour interpréter les résultats</div>
</div>
""", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)
