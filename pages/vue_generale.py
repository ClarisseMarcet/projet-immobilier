import streamlit as st

st.set_page_config(
    page_title="Immobilier & Climat – Vue d’ensemble",
    layout="wide"
)

# =========================
# TITRE + INTRO
# =========================

st.title("Immobilier & Climat : Vue d’ensemble")

st.write(
    "Ce tableau de bord analyse les interactions entre le marché immobilier "
    "et les facteurs climatiques pour mieux comprendre les enjeux et les impacts à long terme."
)

st.markdown("---")

# =========================
# À QUOI SERT LE DASHBOARD
# =========================

st.subheader("À quoi sert ce tableau de bord ?")

st.write("• Comprendre les tendances du marché immobilier")
st.write("• Évaluer les risques climatiques")
st.write("• Identifier les zones à enjeux")
st.write("• Aider à la prise de décision")

st.markdown("---")

# =========================
# DEUX BLOCS CÔTE À CÔTE
# =========================

col1, col2 = st.columns(2)

with col1:
    st.subheader("Analyse climatique")
    st.write("Étudiez les indicateurs climatiques :")
    st.write("• Températures")
    st.write("• Précipitations")
    st.write("• Événements extrêmes")

with col2:
    st.subheader("Analyse immobilière")
    st.write("Explorez les données immobilières :")
    st.write("• Prix")
    st.write("• Transactions")
    st.write("• Évolution du marché")

st.markdown("---")

# =========================
# POURQUOI CROISER
# =========================

st.subheader("Pourquoi croiser climat et immobilier ?")

st.write(
    "Les conditions climatiques impactent la valeur des biens et l’attractivité des territoires. "
    "Une analyse croisée permet d’anticiper les évolutions à venir."
)

st.markdown("---")

# =========================
# COMMENT UTILISER
# =========================

st.subheader("Comment utiliser le tableau de bord ?")

st.write("1. Commencez par la vue d’ensemble")
st.write("2. Consultez la page climatique")
st.write("3. Explorez la page immobilière")
st.write("4. Croisez les informations")
