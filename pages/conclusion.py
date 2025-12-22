import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="Conclusion", layout="wide")

# ======================================================
# CSS – SUPPRESSION DES 2 BARRES BLANCHES (SEULE CORRECTION UI)
# ======================================================

st.markdown("""
<style>
div[data-testid="stTabs"] {
    background: transparent !important;
    padding-top: 0 !important;
    padding-bottom: 0 !important;
}

div[data-testid="stHorizontalBlock"] {
    background: transparent !important;
}

section.main > div {
    padding-top: 0 !important;
}

.section-card {
    background-color: #ffffff;
    border-radius: 16px;
    padding: 26px 30px;
    margin-top: 22px;
    margin-bottom: 28px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.06);
}

.section-title {
    font-size: 1.35rem;
    font-weight: 700;
    margin-bottom: 10px;
    text-align: center;
}

.section-subtitle {
    text-align: center;
    color: #555;
    margin-bottom: 18px;
}
</style>
""", unsafe_allow_html=True)


def highlight(txt, color):
    return f"<span style='color:{color}; font-weight:700;'>{txt}</span>"


def classify_vs_reference(value, ref, tol=0.02):
    if pd.isna(value) or pd.isna(ref) or ref == 0:
        return "non disponible", "#7f8c8d"
    if value < ref * (1 - tol):
        return "moins", "#27ae60"
    if value > ref * (1 + tol):
        return "plus", "#c0392b"
    return "moyenne", "#f39c12"


# ======================================================
# CHARGEMENT DES DONNÉES
# ======================================================

@st.cache_data
def load_data():
    base_dir = Path(__file__).resolve().parents[1]
    path = base_dir / "data" / "base_finale_dashboard.csv"

    df = pd.read_csv(path, dtype={"code_departement": str}, low_memory=False)

    df["code_departement"] = df["code_departement"].astype(str).str.strip().str.upper()
    mask_corse = df["code_departement"].isin(["2A", "2B"])
    df.loc[~mask_corse, "code_departement"] = df.loc[~mask_corse, "code_departement"].str.zfill(2)

    if "nom_departement" not in df.columns:
        df["nom_departement"] = df["code_departement"]

    if "zone" not in df.columns:
        df["zone"] = "Centre"

    if "region" not in df.columns:
        df["region"] = "Non renseignée"

    if "annee" in df.columns:
        df["annee"] = pd.to_numeric(df["annee"], errors="coerce")

    if "prix_m2" not in df.columns:
        df["prix_m2"] = pd.NA

    if "risque_climatique" not in df.columns:
        df["risque_climatique"] = pd.NA

    return df


# ======================================================
# PAGE PRINCIPALE
# ======================================================

def main():
    st.title("Conclusion – Synthèse finale")

    df = load_data()

    # ======================
    # FILTRES (INCHANGÉS)
    # ======================

    st.sidebar.header("Filtres")

    zone_sel = st.sidebar.selectbox("Zone", ["Toutes"] + sorted(df["zone"].dropna().unique()))
    region_sel = st.sidebar.selectbox("Région", ["Toutes"] + sorted(df["region"].dropna().unique()))
    dep_sel = st.sidebar.selectbox(
        "Département",
        ["Tous les départements"] + sorted(df["nom_departement"].dropna().unique())
    )
    type_sel = st.sidebar.selectbox(
        "Type de bien",
        ["Tous"] + sorted(df["type_local"].dropna().unique())
    )
    year_sel = st.sidebar.selectbox(
        "Année",
        ["Toutes"] + sorted(df["annee"].dropna().unique())
    )

    dff = df.copy()
    if zone_sel != "Toutes":
        dff = dff[dff["zone"] == zone_sel]
    if region_sel != "Toutes":
        dff = dff[dff["region"] == region_sel]
    if dep_sel != "Tous les départements":
        dff = dff[dff["nom_departement"] == dep_sel]
    if type_sel != "Tous":
        dff = dff[dff["type_local"] == type_sel]
    if year_sel != "Toutes":
        dff = dff[dff["annee"] == year_sel]

    if dff.empty:
        st.warning("Aucune donnée avec ces filtres.")
        return

    prix_moy = dff["prix_m2"].mean()
    prix_nat = df["prix_m2"].mean()
    risque_moy = dff["risque_climatique"].mean()
    risque_nat = df["risque_climatique"].mean()

    prix_stat, prix_col = classify_vs_reference(prix_moy, prix_nat)
    risque_stat, risque_col = classify_vs_reference(risque_moy, risque_nat)

    geo_url = "https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/departements.geojson"

    tab_immo, tab_clim = st.tabs(["Synthèse immobilière", "Synthèse climatique"])

    # ======================
    # IMMOBILIER
    # ======================

    with tab_immo:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Analyse immobilière</div>", unsafe_allow_html=True)

        _, col, _ = st.columns([0.1, 5, 0.1])
        with col:
            map_df = dff.groupby(
                ["code_departement", "nom_departement"], as_index=False
            )["prix_m2"].mean()

            fig = px.choropleth(
                map_df,
                geojson=geo_url,
                locations="code_departement",
                featureidkey="properties.code",
                color="prix_m2",
                color_continuous_scale="Blues",
                hover_name="nom_departement"
            )
            fig.update_geos(fitbounds="locations", visible=False)
            fig.update_layout(height=620, margin=dict(l=0, r=0, t=0, b=0))
            st.plotly_chart(fig, use_container_width=True)

        st.markdown(
            f"""
            Le territoire étudié est **{highlight(
                "moins cher" if prix_stat=="moins" else "plus cher" if prix_stat=="plus" else "dans la moyenne",
                prix_col
            )}** que la moyenne nationale en termes de prix immobiliers.
            """,
            unsafe_allow_html=True
        )
        st.markdown("</div>", unsafe_allow_html=True)

    # ======================
    # CLIMAT
    # ======================

    with tab_clim:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Analyse climatique</div>", unsafe_allow_html=True)

        _, col, _ = st.columns([0.1, 5, 0.1])
        with col:
            map_df = dff.groupby(
                ["code_departement", "nom_departement"], as_index=False
            )["risque_climatique"].mean()

            fig = px.choropleth(
                map_df,
                geojson=geo_url,
                locations="code_departement",
                featureidkey="properties.code",
                color="risque_climatique",
                color_continuous_scale="Reds",
                hover_name="nom_departement"
            )
            fig.update_geos(fitbounds="locations", visible=False)
            fig.update_layout(height=620, margin=dict(l=0, r=0, t=0, b=0))
            st.plotly_chart(fig, use_container_width=True)

        st.markdown(
            f"""
            Le territoire est **{highlight(
                "moins exposé" if risque_stat=="moins" else "plus exposé" if risque_stat=="plus" else "dans la moyenne",
                risque_col
            )}** aux risques climatiques par rapport à la France.
            """,
            unsafe_allow_html=True
        )
        st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
