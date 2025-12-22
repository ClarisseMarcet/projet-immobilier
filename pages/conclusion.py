import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="Conclusion", layout="wide")

# =========================
# STYLE GLOBAL
# =========================

st.markdown("""
<style>
.section-card {
    background-color: #ffffff;
    border-radius: 16px;
    padding: 26px 30px;
    margin-top: 30px;
    margin-bottom: 40px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.06);
}

.section-title {
    font-size: 1.4rem;
    font-weight: 700;
    margin-bottom: 12px;
    text-align: center;
}

.section-subtitle {
    text-align: center;
    color: #555;
    margin-bottom: 22px;
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
        df["region"] = "Non renseignée"

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
    st.title("Conclusion – Lecture globale et interprétation")

    st.markdown(
        "Cette page propose une **lecture finale guidée** permettant de comprendre "
        "le positionnement immobilier et climatique d’un territoire donné."
    )

    df = load_data()

    # =========================
    # FILTRES INTELLIGENTS
    # =========================

    st.sidebar.header("Filtres géographiques")

    zone_sel = st.sidebar.selectbox("Zone", ["Toutes"] + sorted(df["zone"].dropna().unique()))
    df_zone = df if zone_sel == "Toutes" else df[df["zone"] == zone_sel]

    region_options = sorted(df_zone["region"].dropna().unique())
    region_sel = st.sidebar.selectbox("Région", ["Toutes"] + region_options)
    if region_sel != "Toutes" and region_sel not in region_options:
        region_sel = "Toutes"

    df_region = df_zone if region_sel == "Toutes" else df_zone[df_zone["region"] == region_sel]

    dep_options = sorted(df_region["nom_departement"].dropna().unique())
    dep_sel = st.sidebar.selectbox("Département", ["Tous les départements"] + dep_options)
    if dep_sel != "Tous les départements" and dep_sel not in dep_options:
        dep_sel = "Tous les départements"

    type_sel = st.sidebar.selectbox(
        "Type de bien", ["Tous"] + sorted(df["type_local"].dropna().unique())
    )

    year_sel = st.sidebar.selectbox(
        "Année", ["Toutes"] + sorted(df["annee"].dropna().unique())
    )

    # =========================
    # APPLICATION DES FILTRES
    # =========================

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

    col_prix = "#27ae60" if prix_moy < prix_nat else "#c0392b"
    col_risque = "#c0392b" if risque_moy > risque_nat else "#27ae60"

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Prix moyen local", f"{prix_moy:,.0f} €".replace(",", " "))
    k2.metric("Prix moyen national", f"{prix_nat:,.0f} €".replace(",", " "))
    k3.metric("Risque climatique local", f"{risque_moy:.2f}")
    k4.metric("Risque climatique national", f"{risque_nat:.2f}")

    # =========================
    # SOUS-PAGES BIEN ENCADRÉES
    # =========================

    geo_url = "https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/departements.geojson"

    st.markdown("<div style='height:30px'></div>", unsafe_allow_html=True)
    tab_immo, tab_clim = st.tabs(["Synthèse immobilière", "Synthèse climatique"])
    st.markdown("<div style='height:30px'></div>", unsafe_allow_html=True)

    with tab_immo:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Analyse immobilière du territoire</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-subtitle'>Positionnement des prix au m²</div>", unsafe_allow_html=True)

        col_l, col_c, col_r = st.columns([1, 3, 1])
        with col_c:
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
                hover_name="nom_departement"
            )
            fig.update_geos(fitbounds="locations", visible=False)
            fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
            st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with tab_clim:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Analyse de l’exposition climatique</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-subtitle'>Indice moyen de risque climatique</div>", unsafe_allow_html=True)

        col_l, col_c, col_r = st.columns([1, 3, 1])
        with col_c:
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
                hover_name="nom_departement"
            )
            fig.update_geos(fitbounds="locations", visible=False)
            fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
            st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # =========================
    # CONCLUSION FINALE
    # =========================

    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Conclusion interprétative</div>", unsafe_allow_html=True)

    st.markdown(
        f"""
        <div style="text-align:center; margin-bottom:18px;">
            <span class="badge">{zone_sel}</span>
            <span class="badge">{region_sel}</span>
            <span class="badge" style="background:#dff9fb; color:#130f40;">{dep_sel}</span>
        </div>

        Le **prix moyen immobilier** observé sur ce territoire est de
        {highlight(f"{prix_moy:,.0f} € / m²", col_prix)}, contre
        {highlight(f"{prix_nat:,.0f} € / m²", "#7f8c8d")} au niveau national.

        Le territoire apparaît donc comme
        **{highlight("plus accessible", "#27ae60") if prix_moy < prix_nat else highlight("plus cher", "#c0392b")}**
        que la moyenne française.

        En parallèle, le **niveau de risque climatique moyen** est de
        {highlight(f"{risque_moy:.2f}", col_risque)}, contre
        {highlight(f"{risque_nat:.2f}", "#7f8c8d")} à l’échelle nationale.

        Cela indique un territoire
        **{highlight("plus exposé", "#c0392b") if risque_moy > risque_nat else highlight("moins exposé", "#27ae60")}**
        aux aléas climatiques.

        **Lecture globale :**  
        Les prix immobiliers restent principalement structurés par la **localisation**
        et le **type de bien**, tandis que le climat agit comme un **facteur de contexte**
        à intégrer dans les décisions à long terme.
        """.replace(",", " "),
        unsafe_allow_html=True
    )

    st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
