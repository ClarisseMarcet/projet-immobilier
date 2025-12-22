import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="Conclusion", layout="wide")

# =========================
# UTILITAIRE VISUEL
# =========================

def highlight(txt, color="#e74c3c"):
    return f"<span style='color:{color}; font-weight:700;'>{txt}</span>"


# =========================
# CHARGEMENT DES DONNÉES
# =========================

@st.cache_data
def load_data():
    base_dir = Path(__file__).resolve().parents[1]
    path = base_dir / "data" / "base_finale_dashboard.csv"

    df = pd.read_csv(path, dtype={"code_departement": str}, low_memory=False)

    df["code_departement"] = df["code_departement"].astype(str).str.zfill(2)

    if "nom_departement" not in df.columns:
        df["nom_departement"] = df["code_departement"]

    if "zone" not in df.columns:
        df["zone"] = "Centre"
    df["zone"] = df["zone"].replace("Autres", "Centre")

    if "region" not in df.columns:
        df["region"] = pd.NA

    if "annee" in df.columns:
        df["annee"] = pd.to_numeric(df["annee"], errors="coerce")

    if "prix_m2" not in df.columns:
        df["prix_m2"] = pd.NA

    if "risque_climatique" not in df.columns:
        df["risque_climatique"] = pd.NA

    return df


# =========================
# PAGE PRINCIPALE
# =========================

def main():
    st.title("Conclusion – Synthèse des résultats")

    df = load_data()

    st.sidebar.header("Filtres")

    # -------------------------
    # 1) FILTRE ZONE
    # -------------------------
    zones = ["Toutes"] + sorted(df["zone"].dropna().unique())
    zone_sel = st.sidebar.selectbox("Zone", zones)

    df_zone = df.copy()
    if zone_sel != "Toutes":
        df_zone = df_zone[df_zone["zone"] == zone_sel]

    # -------------------------
    # 2) FILTRE RÉGION (auto-reset)
    # -------------------------
    regions_disponibles = sorted(df_zone["region"].dropna().unique())
    region_options = ["Toutes"] + regions_disponibles

    region_sel = st.sidebar.selectbox("Région", region_options)

    if region_sel != "Toutes" and region_sel not in regions_disponibles:
        region_sel = "Toutes"

    df_region = df_zone.copy()
    if region_sel != "Toutes":
        df_region = df_region[df_region["region"] == region_sel]

    # -------------------------
    # 3) FILTRE DÉPARTEMENT (auto-reset)
    # -------------------------
    deps_disponibles = sorted(df_region["nom_departement"].dropna().unique())
    dep_options = ["Tous les départements"] + deps_disponibles

    dep_sel = st.sidebar.selectbox("Département", dep_options)

    if dep_sel != "Tous les départements" and dep_sel not in deps_disponibles:
        dep_sel = "Tous les départements"

    # -------------------------
    # 4) AUTRES FILTRES
    # -------------------------
    type_sel = st.sidebar.selectbox(
        "Type de bien",
        ["Tous"] + sorted(df["type_local"].dropna().unique())
    )

    year_sel = st.sidebar.selectbox(
        "Année",
        ["Toutes"] + sorted(df["annee"].dropna().unique())
    )

    # -------------------------
    # APPLICATION DES FILTRES
    # -------------------------
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
        st.warning("Aucune donnée disponible avec ces filtres.")
        return

    # =========================
    # INDICATEURS
    # =========================

    prix_moy = dff["prix_m2"].mean()
    prix_nat = df["prix_m2"].mean()
    risque_moy = dff["risque_climatique"].mean()
    risque_nat = df["risque_climatique"].mean()

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Prix moyen au m²", f"{prix_moy:,.0f} €".replace(",", " "))
    k2.metric("Prix national", f"{prix_nat:,.0f} €".replace(",", " "))
    k3.metric("Risque climatique moyen", f"{risque_moy:.2f}")
    k4.metric("Risque climatique national", f"{risque_nat:.2f}")

    st.markdown("---")

    tab_immo, tab_clim = st.tabs(["Synthèse immobilière", "Synthèse climatique"])

    geo_url = "https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/departements.geojson"

    with tab_immo:
        map_df = (
            dff.groupby(["code_departement", "nom_departement"], as_index=False)
            .agg(prix_m2=("prix_m2", "mean"))
            .dropna()
        )

        fig = px.choropleth(
            map_df,
            geojson=geo_url,
            locations="code_departement",
            featureidkey="properties.code",
            color="prix_m2",
            color_continuous_scale="Blues",
            hover_name="nom_departement",
        )
        fig.update_geos(fitbounds="locations", visible=False)
        st.plotly_chart(fig, use_container_width=True)

    with tab_clim:
        map_df = (
            dff.groupby(["code_departement", "nom_departement"], as_index=False)
            .agg(risque=("risque_climatique", "mean"))
            .dropna()
        )

        fig = px.choropleth(
            map_df,
            geojson=geo_url,
            locations="code_departement",
            featureidkey="properties.code",
            color="risque",
            color_continuous_scale="Reds",
            hover_name="nom_departement",
        )
        fig.update_geos(fitbounds="locations", visible=False)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("Conclusion générale")

    st.markdown("""
Cette page de synthèse garantit une lecture cohérente des résultats en empêchant
les combinaisons géographiques impossibles. Les analyses immobilières et climatiques
sont ainsi toujours présentées sur un périmètre valide et interprétable.
""")


if __name__ == "__main__":
    main()
