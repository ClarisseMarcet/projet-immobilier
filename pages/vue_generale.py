import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

@st.cache_data
def load_data():
    base_dir = Path(__file__).resolve().parents[1]
    data_path = base_dir / "data" / "base_finale_dashboard.csv"

    df = pd.read_csv(
        data_path,
        dtype={"code_departement": str, "code_commune": str},
        low_memory=False
    )

    df["code_departement"] = df["code_departement"].astype(str).str.zfill(2)
    df["code_commune"] = df["code_commune"].astype(str).str.zfill(5)

    # Zones France (Nord / Sud / Est / Ouest / Autres)
    def map_zone(dep):
        try:
            cd = int(dep)
        except:
            return "Autres"

        if cd in {59, 62, 80, 2, 60, 76}:
            return "Nord"

        if cd in {57, 54, 55, 88, 67, 68, 52, 21, 25, 39, 70}:
            return "Est"

        if cd in {29, 22, 56, 35, 44, 85, 79, 17, 50, 14, 53}:
            return "Ouest"

        if cd in {
            13, 83, 6, 34, 30, 66, 31, 64, 40, 47, 11, 81, 82,
            46, 48, 12, 84, 4, 5
        }:
            return "Sud"

        return "Autres"

    df["zone"] = df["code_departement"].apply(map_zone)

    if "nom_departement" not in df.columns:
        df["nom_departement"] = df["code_departement"]

    return df


def main():
    st.title("Vue générale – Immobilier et risques climatiques")

    df = load_data()

    # Filtres
    st.sidebar.header("Filtres")

    annees = sorted(df["annee"].dropna().unique())
    annee = st.sidebar.selectbox("Année", annees, index=len(annees) - 1)

    zones = ["Toutes"] + sorted(df["zone"].dropna().unique())
    zone = st.sidebar.selectbox("Zone", zones)

    if zone != "Toutes":
        deps = df[df["zone"] == zone]["nom_departement"].dropna().unique()
    else:
        deps = df["nom_departement"].dropna().unique()

    departements = ["Tous"] + sorted(deps)
    departement = st.sidebar.selectbox("Département", departements)

    types_bien = ["Tous"] + sorted(df["type_local"].dropna().unique())
    type_bien = st.sidebar.selectbox("Type de bien", types_bien)

    # Type de risque
    RISK_MAP = {
        "Global (pondéré)": "risque_climatique",
        "Chaleur (R_ATM_2016)": "R_ATM_2016",
        "Sécheresse (R_MVT_2016)": "R_MVT_2016",
        "Inondation (R_INO_2016)": "R_INO_2016",
        "Feux (R_FEU_2016)": "R_FEU_2016",
    }
    risque_label = st.sidebar.selectbox("Type de risque", list(RISK_MAP.keys()))
    col_risque = RISK_MAP[risque_label]

    if st.sidebar.button("Réinitialiser"):
        st.experimental_rerun()

    # Application des filtres
    dff = df[df["annee"] == annee].copy()

    if zone != "Toutes":
        dff = dff[dff["zone"] == zone]

    if departement != "Tous":
        dff = dff[dff["nom_departement"] == departement]

    if type_bien != "Tous":
        dff = dff[dff["type_local"] == type_bien]

    if dff.empty:
        st.warning("Aucune donnée pour ces filtres.")
        return

    st.subheader("Indicateurs clés")

    k1, k2, k3, k4 = st.columns(4)

    # KPI 1 : prix moyen au m²
    prix_moy = dff["prix_m2"].mean()

    # KPI 2 : population exposée
    if "PMUN_2014" in dff.columns:
        vals = dff["PMUN_2014"].dropna()
        pop_exposee = f"{int(vals.sum()):,}".replace(",", " ") if len(vals) > 0 else "Non disponible"
    else:
        pop_exposee = "Non disponible"

    # KPI 3 : département le plus risqué (sur risque_climatique global)
    if "risque_climatique" in dff.columns and not dff["risque_climatique"].dropna().empty:
        dep_risk = (
            dff.groupby("nom_departement")["risque_climatique"]
            .mean()
            .sort_values(ascending=False)
        )
        dep_plus_risque = dep_risk.index[0]
    else:
        dep_plus_risque = "Non disponible"

    # KPI 4 : indice moyen du risque sélectionné
    if col_risque in dff.columns and not dff[col_risque].dropna().empty:
        score_risque = round(dff[col_risque].mean(), 3)
    else:
        score_risque = "Non disponible"

    k1.metric("Prix moyen au m²", f"{prix_moy:,.0f} €")
    k2.metric("Population exposée", pop_exposee)
    k3.metric("Département le plus risqué", dep_plus_risque)
    k4.metric(f"Indice moyen ({risque_label})", score_risque)

    st.markdown("---")

    c1, c2 = st.columns([1.4, 1])

    # Carte des prix
    with c1:
        st.subheader("Prix au m² par département")

        geo_url = "https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/departements.geojson"

        df_dep = (
            dff.groupby(["code_departement", "nom_departement"], as_index=False)
            .agg(
                prix_m2=("prix_m2", "mean"),
                risque_climatique=("risque_climatique", "mean")
            )
        )

        fig_map = px.choropleth(
            df_dep,
            geojson=geo_url,
            locations="code_departement",
            featureidkey="properties.code",
            color="prix_m2",
            color_continuous_scale="Blues",
            hover_name="nom_departement",
            hover_data=["prix_m2", "risque_climatique"]
        )
        fig_map.update_geos(fitbounds="locations", visible=False)
        fig_map.update_layout(margin=dict(l=0, r=0, t=0, b=0))

        st.plotly_chart(fig_map, use_container_width=True)

    # Risque moyen par zone
    with c2:
        st.subheader(f"Risque moyen ({risque_label}) par zone")

        if col_risque not in dff.columns or dff[col_risque].dropna().empty:
            st.info("Aucune donnée de risque disponible pour ces filtres.")
        else:
            df_zone = (
                dff.groupby("zone")[col_risque]
                .mean()
                .reset_index()
                .sort_values(col_risque, ascending=False)
            )

            fig_risk_zone = px.bar(
                df_zone,
                x=col_risque,
                y="zone",
                orientation="h",
                labels={col_risque: "Indice moyen", "zone": "Zone"},
            )
            fig_risk_zone.update_yaxes(autorange="reversed")
            st.plotly_chart(fig_risk_zone, use_container_width=True)

    st.markdown("---")

    d1, d2 = st.columns(2)

    # Donut prix moyen par zone
    with d1:
        st.subheader("Prix moyen par zone")

        df_pmz = dff.groupby("zone")["prix_m2"].mean().reset_index()

        fig_donut = px.pie(
            df_pmz,
            names="zone",
            values="prix_m2",
            hole=0.55
        )
        fig_donut.update_traces(textinfo="percent+label")
        st.plotly_chart(fig_donut, use_container_width=True)

    # Top 10 départements les plus chers
    with d2:
        st.subheader("Top 10 départements les plus chers")

        df_top_price = (
            dff.groupby("nom_departement")["prix_m2"]
            .mean()
            .sort_values(ascending=False)
            .head(10)
            .reset_index()
        )

        fig_top_price = px.bar(
            df_top_price,
            x="prix_m2",
            y="nom_departement",
            orientation="h",
            labels={"prix_m2": "Prix moyen au m²", "nom_departement": "Département"},
        )
        fig_top_price.update_yaxes(autorange="reversed")
        st.plotly_chart(fig_top_price, use_container_width=True)

    st.markdown("---")

    r1, r2 = st.columns(2)

    # Top 10 départements les plus risqués
    with r1:
        st.subheader(f"Top 10 départements les plus risqués ({risque_label})")

        if col_risque in dff.columns and not dff[col_risque].dropna().empty:
            df_top_risk = (
                dff.groupby("nom_departement")[col_risque]
                .mean()
                .sort_values(ascending=False)
                .head(10)
                .reset_index()
            )

            fig_top_risk = px.bar(
                df_top_risk,
                x=col_risque,
                y="nom_departement",
                orientation="h",
                labels={col_risque: "Indice moyen", "nom_departement": "Département"},
                color=col_risque,
                color_continuous_scale="Reds"
            )
            fig_top_risk.update_yaxes(autorange="reversed")
            st.plotly_chart(fig_top_risk, use_container_width=True)
        else:
            st.info("Pas assez de données de risque pour ce graphique.")

    # Histogramme des prix
    with r2:
        st.subheader("Distribution des prix au m²")

        fig_hist = px.histogram(
            dff,
            x="prix_m2",
            nbins=40,
            labels={"prix_m2": "Prix au m²"},
        )
        st.plotly_chart(fig_hist, use_container_width=True)

    st.markdown("---")

    # Evolution du prix dans le temps
    st.subheader("Évolution du prix au m² dans le temps")

    df_e = df.copy()

    if zone != "Toutes":
        df_e = df_e[df_e["zone"] == zone]

    if departement != "Tous":
        df_e = df_e[df_e["nom_departement"] == departement]

    if type_bien != "Tous":
        df_e = df_e[df_e["type_local"] == type_bien]

    df_e = df_e.groupby("annee")["prix_m2"].mean().reset_index()

    fig_evo = px.line(
        df_e,
        x="annee",
        y="prix_m2",
        markers=True,
        labels={"annee": "Année", "prix_m2": "Prix moyen au m²"}
    )
    st.plotly_chart(fig_evo, use_container_width=True)

    st.markdown("---")

    # Synthèse automatique
    st.subheader("Synthèse automatique")

    zone_prix = dff.groupby("zone")["prix_m2"].mean().sort_values(ascending=False)

    zone_risk = None
    if col_risque in dff.columns and not dff[col_risque].dropna().empty:
        zone_risk = (
            dff.groupby("zone")[col_risque]
            .mean()
            .sort_values(ascending=False)
        )

    dep_prix = (
        dff.groupby("nom_departement")["prix_m2"]
        .mean()
        .sort_values(ascending=False)
    )

    text_lines = []

    if not df_e.empty and len(df_e) >= 2:
        prix_start = df_e.iloc[0]["prix_m2"]
        prix_end = df_e.iloc[-1]["prix_m2"]
        var_abs = prix_end - prix_start
        var_pct = (var_abs / prix_start * 100) if prix_start not in (0, None) else 0
        sens = "augmenté" if var_abs >= 0 else "diminué"

        text_lines.append(
            f"- Sur la période disponible, le prix moyen au m² a {sens} de "
            f"{abs(var_abs):,.0f} € (environ {abs(var_pct):,.1f} %)."
        )

    if not zone_prix.empty:
        z_max = zone_prix.index[0]
        p_max = zone_prix.iloc[0]
        text_lines.append(
            f"- La zone {z_max} est la plus chère, avec un prix moyen proche de {p_max:,.0f} € / m²."
        )

    if zone_risk is not None and not zone_risk.empty:
        zr_max = zone_risk.index[0]
        r_max = zone_risk.iloc[0]
        text_lines.append(
            f"- Pour le risque {risque_label}, la zone {zr_max} est la plus exposée "
            f"(indice moyen ≈ {r_max:,.2f})."
        )

    if not dep_prix.empty:
        d_max = dep_prix.index[0]
        dp = dep_prix.iloc[0]
        text_lines.append(
            f"- Le département le plus cher dans cette vue est {d_max}, avec {dp:,.0f} € / m²."
        )

    if text_lines:
        st.markdown("\n".join(text_lines))
    else:
        st.info("Aucune synthèse disponible pour ces filtres.")

    # Aperçu des données filtrées
    with st.expander("Aperçu des données filtrées"):
        st.dataframe(dff.head(200))


if __name__ == "__main__":
    main()
