import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="Conclusion", layout="wide")

# ======================================================
# STYLE GLOBAL – NETTOYAGE DES BARRES BLANCHES + CARTES
# ======================================================

st.markdown("""
<style>

/* Supprime les bandes blanches Streamlit autour des tabs */
div[data-testid="stTabs"] {
    background: transparent !important;
    padding-top: 0 !important;
    padding-bottom: 0 !important;
}

/* Supprime les blocs blancs internes */
div[data-testid="stHorizontalBlock"] {
    background: transparent !important;
}

/* Fond global */
.main {
    background-color: #f6f7f9;
}

/* Cartes visuelles */
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
    font-weight: 750;
    margin-bottom: 10px;
    text-align: center;
}

.section-subtitle {
    text-align: center;
    color: #555;
    margin-bottom: 18px;
}

.badge {
    background:#ecf0f1;
    color:#2c3e50;
    padding:6px 14px;
    border-radius:18px;
    font-weight:600;
    font-size:0.9rem;
    margin-right:6px;
    display:inline-block;
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
    df["zone"] = df["zone"].replace("Autres", "Centre")

    if "region" not in df.columns:
        df["region"] = pd.NA

    regions = {
        "75": "Île-de-France", "92": "Île-de-France", "93": "Île-de-France",
        "94": "Île-de-France", "91": "Île-de-France", "77": "Île-de-France", "78": "Île-de-France",
        "13": "Provence-Alpes-Côte d’Azur", "69": "Auvergne-Rhône-Alpes",
        "59": "Hauts-de-France", "62": "Hauts-de-France",
        "33": "Nouvelle-Aquitaine", "31": "Occitanie"
    }

    df["region"] = df["region"].fillna(df["code_departement"].map(regions))
    df["region"] = df["region"].fillna("Non renseignée")

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
    st.title("Conclusion – Lecture globale et interprétation")

    df = load_data()

    # ----------------------
    # FILTRES
    # ----------------------

    st.sidebar.header("Filtres")

    zone_sel = st.sidebar.selectbox("Zone", ["Toutes"] + sorted(df["zone"].unique()))
    df_zone = df if zone_sel == "Toutes" else df[df["zone"] == zone_sel]

    region_opts = sorted(df_zone["region"].unique())
    region_sel = st.sidebar.selectbox("Région", ["Toutes"] + region_opts)
    df_region = df_zone if region_sel == "Toutes" else df_zone[df_zone["region"] == region_sel]

    dep_opts = sorted(df_region["nom_departement"].unique())
    dep_sel = st.sidebar.selectbox("Département", ["Tous les départements"] + dep_opts)

    dff = df.copy()
    if zone_sel != "Toutes":
        dff = dff[dff["zone"] == zone_sel]
    if region_sel != "Toutes":
        dff = dff[dff["region"] == region_sel]
    if dep_sel != "Tous les départements":
        dff = dff[dff["nom_departement"] == dep_sel]

    if dff.empty:
        st.warning("Aucune donnée avec ces filtres.")
        return

    # ----------------------
    # INDICATEURS
    # ----------------------

    prix_moy = dff["prix_m2"].mean()
    prix_nat = df["prix_m2"].mean()
    risque_moy = dff["risque_climatique"].mean()
    risque_nat = df["risque_climatique"].mean()

    prix_stat, prix_col = classify_vs_reference(prix_moy, prix_nat)
    risque_stat, risque_col = classify_vs_reference(risque_moy, risque_nat)

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Prix local", f"{prix_moy:,.0f} €".replace(",", " "))
    k2.metric("Prix France", f"{prix_nat:,.0f} €".replace(",", " "))
    k3.metric("Risque local", f"{risque_moy:.2f}")
    k4.metric("Risque France", f"{risque_nat:.2f}")

    # ----------------------
    # TABS
    # ----------------------

    geo_url = "https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/departements.geojson"
    tab_immo, tab_clim = st.tabs(["Analyse immobilière", "Analyse climatique"])

    # ======================
    # IMMOBILIER
    # ======================

    with tab_immo:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Analyse immobilière</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-subtitle'>Prix au m² par département</div>", unsafe_allow_html=True)

        _, col, _ = st.columns([0.1, 5, 0.1])
        with col:
            map_df = dff.groupby(["code_departement", "nom_departement"], as_index=False)["prix_m2"].mean()
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
            Le marché immobilier est **{highlight(
                "moins cher" if prix_stat=="moins" else "plus cher" if prix_stat=="plus" else "dans la moyenne",
                prix_col
            )}** par rapport à la France.
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
        st.markdown("<div class='section-subtitle'>Exposition aux risques climatiques</div>", unsafe_allow_html=True)

        _, col, _ = st.columns([0.1, 5, 0.1])
        with col:
            map_df = dff.groupby(["code_departement", "nom_departement"], as_index=False)["risque_climatique"].mean()
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
            )}** aux risques climatiques que la France.
            """,
            unsafe_allow_html=True
        )
        st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
