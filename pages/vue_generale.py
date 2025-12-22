import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="Introduction", layout="wide")

# =========================
# STYLE SIMPLE & AÉRÉ
# =========================
st.markdown("""
<style>
.intro-container {
    max-width: 1100px;
    margin: auto;
}

.section-title {
    font-size: 1.6rem;
    font-weight: 700;
    margin-top: 30px;
    margin-bottom: 14px;
}

.section-text {
    font-size: 1rem;
    line-height: 1.7;
    color: #333;
}

.grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 26px;
    margin-top: 20px;
}

.box {
    padding: 18px 22px;
    border-left: 4px solid #2c3e50;
    background-color: #f9f9f9;
}

.box-title {
    font-weight: 700;
    margin-bottom: 8px;
}

.steps {
    margin-top: 10px;
}

.step {
    margin-bottom: 8px;
}
</style>
""", unsafe_allow_html=True)

# =========================
# CHARGEMENT DES DONNÉES (pour chiffres clés)
# =========================
@st.cache_data
def load_data():
    path = Path("data/base_finale_dashboard.csv")
    df = pd.read_csv(path, low_memory=False)

    if "prix_m2" not in df.columns:
        df["prix_m2"] = pd.NA
    if "risque_climatique" not in df.columns:
        df["risque_climatique"] = pd.NA

    return df


def main():
    df = load_data()

    prix_moy_nat = df["prix_m2"].mean()
    risque_moy_nat = df["risque_climatique"].mean()
    nb_departements = df["code_departement"].nunique() if "code_departement" in df.columns else None

    st.title("Immobilier & Climat : vue d’ensemble")

    st.markdown("<div class='intro-container'>", unsafe_allow_html=True)

    # =========================
    # TEXTE INTRODUCTIF
    # =========================
    st.markdown("""
    <div class="section-text">
    Ce tableau de bord analyse les interactions entre le <b>marché immobilier</b> et les
    <b>facteurs climatiques</b> afin de mieux comprendre les enjeux territoriaux actuels.

    L’objectif est d’apporter une lecture claire et structurée des disparités géographiques,
    en mettant en regard l’accessibilité du marché immobilier et l’exposition aux risques
    climatiques.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # =========================
    # À QUOI SERT CE TABLEAU DE BORD ?
    # =========================
    st.markdown("<div class='section-title'>À quoi sert ce tableau de bord ?</div>", unsafe_allow_html=True)

    st.markdown("""
    <div class="section-text">
    ▸ Comprendre les tendances du marché immobilier<br>
    ▸ Analyser les indicateurs climatiques<br>
    ▸ Identifier les zones à risques ou à opportunités<br>
    ▸ Aider à la prise de décision en matière d’investissement, d’aménagement et de prévention
    </div>
    """, unsafe_allow_html=True)

    # =========================
    # IMMOBILIER / CLIMAT (2 BLOCS)
    # =========================
    st.markdown("<div class='grid'>", unsafe_allow_html=True)

    st.markdown("""
    <div class="box">
        <div class="box-title">Analyse climatique</div>
        ▸ Températures et aléas climatiques<br>
        ▸ Sécheresse, inondations, feux<br>
        ▸ Population exposée<br>
        ▸ Pressions environnementales sur les territoires
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="box">
        <div class="box-title">Analyse immobilière</div>
        ▸ Prix au mètre carré<br>
        ▸ Types de biens et transactions<br>
        ▸ Évolution temporelle du marché<br>
        ▸ Accessibilité territoriale
    </div>
    """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # =========================
    # LIEN IMMOBILIER / CLIMAT
    # =========================
    st.markdown("<div class='section-title'>Pourquoi croiser climat et immobilier ?</div>", unsafe_allow_html=True)

    st.markdown("""
    <div class="section-text">
    Les conditions climatiques impactent durablement l’attractivité des territoires.
    Le croisement des données immobilières et climatiques permet d’anticiper certaines
    évolutions, de mieux comprendre les dynamiques locales et d’éclairer les choix
    d’aménagement et d’investissement.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # =========================
    # CHIFFRES CLÉS (PEU NOMBREUX)
    # =========================
    st.markdown("<div class='section-title'>Repères nationaux</div>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)

    c1.metric("Prix moyen national", f"{prix_moy_nat:,.0f} € / m²".replace(",", " "))
    c2.metric("Indice climatique moyen", f"{risque_moy_nat:.2f}")
    if nb_departements:
        c3.metric("Départements analysés", nb_departements)

    # =========================
    # COMMENT UTILISER LE DASHBOARD
    # =========================
    st.markdown("<div class='section-title'>Comment utiliser le tableau de bord ?</div>", unsafe_allow_html=True)

    st.markdown("""
    <div class="section-text steps">
        <div class="step">1. Commencer par la page <b>Vue générale</b></div>
        <div class="step">2. Explorer les indicateurs climatiques</div>
        <div class="step">3. Analyser les données immobilières</div>
        <div class="step">4. Croiser les informations pour affiner l’interprétation</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
