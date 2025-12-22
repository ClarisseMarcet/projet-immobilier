import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="Introduction", layout="wide")

# =========================
# STYLE (harmonisé avec Conclusion)
# =========================
st.markdown("""
<style>
.section-card {
    background-color: #ffffff;
    border-radius: 16px;
    padding: 26px 30px;
    margin-top: 22px;
    margin-bottom: 28px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.06);
}

.section-title {
    font-size: 1.4rem;
    font-weight: 750;
    margin-bottom: 14px;
    text-align: center;
}

.section-text {
    font-size: 1rem;
    line-height: 1.6;
    color: #333;
}
</style>
""", unsafe_allow_html=True)

# =========================
# CHARGEMENT DES DONNÉES
# =========================
@st.cache_data
def load_data():
    path = Path("data/base_finale_dashboard.csv")
    df = pd.read_csv(path, dtype={"code_departement": str}, low_memory=False)

    df["code_departement"] = df["code_departement"].astype(str).str.zfill(2)

    if "prix_m2" not in df.columns:
        df["prix_m2"] = pd.NA
    if "risque_climatique" not in df.columns:
        df["risque_climatique"] = pd.NA

    return df


# =========================
# PAGE INTRODUCTION
# =========================
def main():

    st.title("Analyse croisée de l’immobilier et des risques climatiques en France")

    df = load_data()

    # =========================
    # TEXTE INTRODUCTIF
    # =========================
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Objectif du tableau de bord</div>", unsafe_allow_html=True)

    st.markdown("""
    <div class="section-text">
    Ce tableau de bord propose une lecture synthétique et interactive des dynamiques du
    <b>marché immobilier</b> et de l’<b>exposition aux risques climatiques</b> en France.

    L’objectif est d’analyser les disparités territoriales en croisant des indicateurs
    économiques et environnementaux, afin de mieux comprendre les enjeux actuels
    auxquels font face les territoires.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # =========================
    # INDICATEURS GLOBAUX
    # =========================
    prix_nat = df["prix_m2"].mean()
    risque_nat = df["risque_climatique"].mean()

    c1, c2 = st.columns(2)
    c1.metric("Prix moyen national au m²", f"{prix_nat:,.0f} €".replace(",", " "))
    c2.metric("Indice moyen national de risque climatique", f"{risque_nat:.2f}")

    # =========================
    # CARTE DE FRANCE (REPÈRE VISUEL)
    # =========================
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Répartition territoriale – aperçu national</div>", unsafe_allow_html=True)

    geo_url = "https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/departements.geojson"

    map_df = (
        df.groupby("code_departement", as_index=False)
        .agg(
            prix_m2=("prix_m2", "mean"),
            risque=("risque_climatique", "mean")
        )
        .dropna()
    )

    col_l, col_c, col_r = st.columns([0.05, 4.9, 0.05])
    with col_c:
        fig = px.choropleth(
            map_df,
            geojson=geo_url,
            locations="code_departement",
            featureidkey="properties.code",
            color="prix_m2",
            color_continuous_scale="Blues",
            labels={"prix_m2": "Prix moyen au m²"}
        )
        fig.update_geos(fitbounds="locations", visible=False)
        fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
    <div class="section-text" style="text-align:center; margin-top:12px;">
    Cette carte offre une première lecture des disparités territoriales en matière de prix immobiliers.
    Les pages suivantes permettent d’approfondir l’analyse en intégrant les risques climatiques
    et des filtres géographiques détaillés.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
