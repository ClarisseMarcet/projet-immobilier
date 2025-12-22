import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

try:
    from sklearn.linear_model import LinearRegression
    HAS_SKLEARN = True
except Exception:
    HAS_SKLEARN = False


st.set_page_config(
    page_title="Exposition de la population aux risques climatiques",
    layout="wide"
)

st.markdown("""
<style>
h1 { margin-bottom: 2.2rem !important; }
div[data-testid="stTabs"] { margin-top: 0.2rem; margin-bottom: 1.8rem; }
.stTabs [data-baseweb="tab-list"] { gap: 18px; justify-content: center; margin-bottom: 1.2rem; }
.stTabs [data-baseweb="tab"] { font-size: 1.02rem; padding: 12px 22px; background: #f3f4f6; border-radius: 10px; color: #222; border: 1px solid #e6e7ea; }
.stTabs [aria-selected="true"] { background: #1f4fd8 !important; color: #fff !important; border: 1px solid #1f4fd8 !important; font-weight: 650; }
.stTabs [data-baseweb="tab-highlight"] { display: none; }
</style>
""", unsafe_allow_html=True)


DEPARTEMENT_NOMS = {
    "01": "Ain", "02": "Aisne", "03": "Allier", "04": "Alpes-de-Haute-Provence",
    "05": "Hautes-Alpes", "06": "Alpes-Maritimes", "07": "Ardèche", "08": "Ardennes",
    "09": "Ariège", "10": "Aube", "11": "Aude", "12": "Aveyron", "13": "Bouches-du-Rhône",
    "14": "Calvados", "15": "Cantal", "16": "Charente", "17": "Charente-Maritime",
    "18": "Cher", "19": "Corrèze", "2A": "Corse-du-Sud", "2B": "Haute-Corse",
    "21": "Côte-d'Or", "22": "Côtes-d'Armor", "23": "Creuse", "24": "Dordogne",
    "25": "Doubs", "26": "Drôme", "27": "Eure", "28": "Eure-et-Loir", "29": "Finistère",
    "30": "Gard", "31": "Haute-Garonne", "32": "Gers", "33": "Gironde", "34": "Hérault",
    "35": "Ille-et-Vilaine", "36": "Indre", "37": "Indre-et-Loire", "38": "Isère",
    "39": "Jura", "40": "Landes", "41": "Loir-et-Cher", "42": "Loire",
    "43": "Haute-Loire", "44": "Loire-Atlantique", "45": "Loiret", "46": "Lot",
    "47": "Lot-et-Garonne", "48": "Lozère", "49": "Maine-et-Loire", "50": "Manche",
    "51": "Marne", "52": "Haute-Marne", "53": "Mayenne", "54": "Meurthe-et-Moselle",
    "55": "Meuse", "56": "Morbihan", "57": "Moselle", "58": "Nièvre",
    "59": "Nord", "60": "Oise", "61": "Orne", "62": "Pas-de-Calais", "63": "Puy-de-Dôme",
    "64": "Pyrénées-Atlantiques", "65": "Hautes-Pyrénées", "66": "Pyrénées-Orientales",
    "67": "Bas-Rhin", "68": "Haut-Rhin", "69": "Rhône", "70": "Haute-Saône",
    "71": "Saône-et-Loire", "72": "Sarthe", "73": "Savoie", "74": "Haute-Savoie",
    "75": "Paris", "76": "Seine-Maritime", "77": "Seine-et-Marne", "78": "Yvelines",
    "79": "Deux-Sèvres", "80": "Somme", "81": "Tarn", "82": "Tarn-et-Garonne",
    "83": "Var", "84": "Vaucluse", "85": "Vendée", "86": "Vienne", "87": "Haute-Vienne",
    "88": "Vosges", "89": "Yonne", "90": "Territoire de Belfort", "91": "Essonne",
    "92": "Hauts-de-Seine", "93": "Seine-Saint-Denis", "94": "Val-de-Marne",
    "95": "Val-d'Oise",
}

RISQUE_LABELS = {
    "risque_global": "Risque global (pondéré)",
    "risque_chaleur": "Chaleur / canicule",
    "risque_inondation": "Inondation",
    "risque_secheresse": "Mouvements de terrain / sécheresse",
    "risque_feux": "Feux de forêt",
}


def map_region(dep: str) -> str:
    if dep is None:
        return "Région inconnue"
    d = str(dep).strip().upper()
    if d in ("2A", "2B"):
        return "Corse"
    if d in ("75", "77", "78", "91", "92", "93", "94", "95"):
        return "Île-de-France"
    if d in ("18", "28", "36", "37", "41", "45"):
        return "Centre-Val de Loire"
    if d in ("21", "58", "71", "89", "25", "39", "70", "90"):
        return "Bourgogne-Franche-Comté"
    if d in ("67", "68", "88", "52", "54", "55", "57", "08", "10", "51"):
        return "Grand Est"
    if d in ("59", "62", "80", "02", "60"):
        return "Hauts-de-France"
    if d in ("14", "27", "50", "61", "76"):
        return "Normandie"
    if d in ("22", "29", "35", "56"):
        return "Bretagne"
    if d in ("44", "49", "53", "72", "85"):
        return "Pays de la Loire"
    if d in ("16", "17", "19", "23", "24", "33", "40",
             "47", "64", "79", "86", "87"):
        return "Nouvelle-Aquitaine"
    if d in ("03", "15", "43", "63", "07", "26", "38", "42",
             "69", "73", "74", "01"):
        return "Auvergne-Rhône-Alpes"
    if d in ("09", "11", "12", "30", "31", "32", "34",
             "46", "48", "65", "66", "81", "82"):
        return "Occitanie"
    if d in ("04", "05", "06", "13", "83", "84"):
        return "Provence-Alpes-Côte d’Azur"
    return "Région inconnue"


def map_zone5(region: str) -> str:
    if region in ("Hauts-de-France", "Normandie"):
        return "Nord"
    if region == "Grand Est":
        return "Est"
    if region in ("Bretagne", "Pays de la Loire"):
        return "Ouest"
    if region in ("Occitanie", "Provence-Alpes-Côte d’Azur", "Corse"):
        return "Sud"
    return "Centre"


def ensure_column(df: pd.DataFrame, target: str, candidates: list[str]) -> pd.DataFrame:
    if target in df.columns:
        return df
    for c in candidates:
        if c in df.columns:
            df[target] = df[c]
            return df
    return df


@st.cache_data
def load_data():
    base_dir = Path(__file__).resolve().parents[1]
    data_path = base_dir / "data" / "base_finale_dashboard.csv"

    if not data_path.exists():
        st.error(f"Fichier introuvable : {data_path}")
        st.stop()

    df = pd.read_csv(
        data_path,
        dtype={"code_departement": str, "code_commune": str},
        low_memory=False
    )

    df.columns = [str(c).strip() for c in df.columns]

    # codes
    df["code_departement"] = df["code_departement"].astype(str).str.strip().str.upper()
    mask_corse = df["code_departement"].isin(["2A", "2B"])
    df.loc[~mask_corse, "code_departement"] = df.loc[~mask_corse, "code_departement"].str.zfill(2)

    if "code_commune" in df.columns:
        df["code_commune"] = (
            df["code_commune"].astype(str)
            .str.replace(r"\D", "", regex=True)
            .str.zfill(5)
        )

    # renommage standard (ton CSV)
    rename_dict = {
        "PMUN_2014": "population_exposee",
        "risque_climatique": "risque_global",
        "R_ATM_2016": "risque_chaleur",
        "R_INO_2016": "risque_inondation",
        "R_MVT_2016": "risque_secheresse",
        "R_FEU_2016": "risque_feux",
    }
    df = df.rename(columns=rename_dict)

    # colonnes garanties
    df = ensure_column(df, "population_exposee", ["population_exposee", "PMUN_2014"])
    df = ensure_column(df, "risque_global", ["risque_global", "risque_climatique"])
    df = ensure_column(df, "risque_chaleur", ["risque_chaleur", "R_ATM_2016"])
    df = ensure_column(df, "risque_inondation", ["risque_inondation", "R_INO_2016"])
    df = ensure_column(df, "risque_secheresse", ["risque_secheresse", "R_MVT_2016"])
    df = ensure_column(df, "risque_feux", ["risque_feux", "R_FEU_2016"])

    # nom département + zones
    if "nom_departement" not in df.columns:
        df["nom_departement"] = df["code_departement"].map(DEPARTEMENT_NOMS)

    df["region"] = df["code_departement"].apply(map_region)
    df["zone5"] = df["region"].apply(map_zone5)

    if "annee" in df.columns:
        df["annee"] = pd.to_numeric(df["annee"], errors="coerce")

    # population_exposee en numérique
    if "population_exposee" in df.columns:
        df["population_exposee"] = pd.to_numeric(df["population_exposee"], errors="coerce")

    return df


def main():
    st.title("Exposition de la population aux risques climatiques")

    df = load_data()

    if "population_exposee" not in df.columns or df["population_exposee"].dropna().empty:
        st.error(
            "Colonne 'population_exposee' introuvable ou vide.\n\n"
            "Colonnes détectées :\n- " + "\n- ".join(list(df.columns)[:200])
        )
        st.stop()

    df_pop = df.dropna(subset=["population_exposee", "code_departement", "nom_departement", "zone5", "region"]).copy()

    # agrégation département
    agg_dict = {
        "population_exposee": ("population_exposee", "sum"),
        "risque_global": ("risque_global", "mean") if "risque_global" in df_pop.columns else ("population_exposee", "mean"),
    }
    for col in ["risque_chaleur", "risque_inondation", "risque_secheresse", "risque_feux"]:
        if col in df_pop.columns:
            agg_dict[col] = (col, "mean")

    dep_agg = (
        df_pop.groupby(["code_departement", "nom_departement", "zone5", "region"], as_index=False)
        .agg(**agg_dict)
    )

    total_pop = dep_agg["population_exposee"].sum()

    # filtres
    st.sidebar.header("Filtres")

    zones = ["Toutes", "Nord", "Sud", "Est", "Ouest", "Centre"]
    zone_sel = st.sidebar.selectbox("Zone (5 zones France)", zones)

    regions = ["Toutes"] + sorted(dep_agg["region"].dropna().unique())
    region_sel = st.sidebar.selectbox("Région", regions)

    dff = dep_agg.copy()
    if zone_sel != "Toutes":
        dff = dff[dff["zone5"] == zone_sel]
    if region_sel != "Toutes":
        dff = dff[dff["region"] == region_sel]

    deps = ["Tous"] + sorted(dff["nom_departement"].dropna().unique())
    dep_sel = st.sidebar.selectbox("Département", deps)

    if dep_sel != "Tous":
        dff = dff[dff["nom_departement"] == dep_sel]

    risk_label_map = {
        "Risque global (pondéré)": "risque_global",
        "Chaleur / canicule": "risque_chaleur",
        "Inondation": "risque_inondation",
        "Mouvements de terrain / sécheresse": "risque_secheresse",
        "Feux de forêt": "risque_feux",
    }
    risk_choice = st.sidebar.selectbox("Type de risque à analyser", list(risk_label_map.keys()))
    risk_col = risk_label_map[risk_choice]
    if risk_col not in df.columns:
        risk_col = "risque_global" if "risque_global" in df.columns else None

    top_n = st.sidebar.slider("Top communes les plus exposées", 5, 30, 10)

    if dff.empty:
        st.warning("Aucune donnée après filtre.")
        return

    tab1, tab2, tab3, tab4 = st.tabs([
        "Exposition globale",
        "Comparaisons territoriales",
        "Analyse multi-risques",
        "Évolutions & prévisions"
    ])

    with tab1:
        st.subheader("Indicateurs clés")

        pop_filtre = dff["population_exposee"].sum()
        part = pop_filtre / total_pop * 100 if total_pop else 0

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Population exposée (filtres)", f"{int(pop_filtre):,}".replace(",", " "))
        k2.metric("Part de l'exposition nationale", f"{part:.1f} %")
        k3.metric("Départements concernés", dff["code_departement"].nunique())
        k4.metric("Risque global moyen", f"{dff['risque_global'].mean():.2f}" if "risque_global" in dff.columns else "N/A")

        st.markdown("---")

        geo_url = "https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/departements.geojson"
        c1, c2 = st.columns([1.7, 1])

        with c1:
            st.subheader("Population exposée par département")
            fig_map = px.choropleth(
                dff,
                geojson=geo_url,
                locations="code_departement",
                featureidkey="properties.code",
                color="population_exposee",
                hover_name="nom_departement",
                hover_data=[c for c in ["region", "zone5", "population_exposee", "risque_global"] if c in dff.columns],
            )
            fig_map.update_geos(fitbounds="locations", visible=False)
            fig_map.update_layout(height=530, margin=dict(l=15, r=60, t=10, b=10))
            st.plotly_chart(fig_map, use_container_width=True)

        with c2:
            st.subheader("Répartition de la population exposée")
            zone_agg = (
                dep_agg.groupby("zone5")["population_exposee"]
                .sum().reset_index()
                .sort_values("population_exposee", ascending=False)
            )
            fig_zone = px.pie(zone_agg, names="zone5", values="population_exposee", hole=0.50)
            fig_zone.update_layout(height=530, margin=dict(l=10, r=10, t=45, b=0))
            st.plotly_chart(fig_zone, use_container_width=True)

    with tab2:
        st.subheader("Top 10 régions les plus exposées")
        region_agg = (
            dep_agg.groupby("region")["population_exposee"]
            .sum().reset_index()
            .sort_values("population_exposee", ascending=False)
            .head(10)
        )
        fig_region = px.bar(region_agg, x="population_exposee", y="region", orientation="h",
                            labels={"population_exposee": "Population exposée", "region": "Région"})
        fig_region.update_yaxes(autorange="reversed")
        st.plotly_chart(fig_region, use_container_width=True)

        st.markdown("---")
        st.subheader("Population exposée vs risque global (par département)")
        if "risque_global" in dff.columns:
            scatter = px.scatter(
                dff,
                x="risque_global",
                y="population_exposee",
                size="population_exposee",
                color="zone5",
                hover_name="nom_departement",
                labels={"risque_global": "Risque global (moyen)", "population_exposee": "Population exposée"}
            )
            st.plotly_chart(scatter, use_container_width=True)
        else:
            st.info("Colonne risque_global absente : scatter indisponible.")

        st.markdown("---")
        st.subheader(f"Top {top_n} communes les plus exposées")

        df_top_src = df_pop.copy()
        if zone_sel != "Toutes":
            df_top_src = df_top_src[df_top_src["zone5"] == zone_sel]
        if region_sel != "Toutes":
            df_top_src = df_top_src[df_top_src["region"] == region_sel]
        if dep_sel != "Tous":
            df_top_src = df_top_src[df_top_src["nom_departement"] == dep_sel]

        required = {"zone5", "region", "code_departement", "nom_departement", "code_commune", "commune", "population_exposee"}
        if required.issubset(df_top_src.columns):
            df_comm = (
                df_top_src.dropna(subset=["commune"])
                .groupby(["zone5", "region", "code_departement", "nom_departement", "code_commune", "commune"], as_index=False)
                .agg(population_exposee=("population_exposee", "sum"))
                .sort_values("population_exposee", ascending=False)
                .head(top_n)
            )
            st.dataframe(df_comm, use_container_width=True)
        else:
            st.info("Colonnes insuffisantes pour afficher le top communes.")

    with tab3:
        st.subheader("Analyse multi-risques par département")

        risque_cols = [c for c in ["risque_chaleur", "risque_inondation", "risque_secheresse", "risque_feux"] if c in dff.columns]
        if not risque_cols:
            st.info("Colonnes multi-risques absentes.")
        else:
            df_radar = dff[risque_cols].mean().reset_index()
            df_radar.columns = ["type_risque", "valeur"]
            df_radar["type_risque"] = df_radar["type_risque"].replace(RISQUE_LABELS)

            values = df_radar["valeur"].tolist()
            values += [values[0]]
            labels = df_radar["type_risque"].tolist()
            labels += [labels[0]]

            fig_radar = go.Figure()
            fig_radar.add_trace(go.Scatterpolar(r=values, theta=labels, fill='toself', line=dict(width=3), opacity=0.9))
            fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True)), showlegend=False, height=420)
            st.plotly_chart(fig_radar, use_container_width=True)

    with tab4:
        if risk_col is None:
            st.info("Aucun indicateur de risque disponible.")
            return

        st.subheader(f"Évolution de {risk_choice.lower()} par zone")

        df_risk = df.dropna(subset=["annee", risk_col]).copy()
        df_risk = df_risk[df_risk["annee"].notna()]

        if region_sel != "Toutes":
            df_risk = df_risk[df_risk["region"] == region_sel]
        if dep_sel != "Tous":
            df_risk = df_risk[df_risk["nom_departement"] == dep_sel]

        if not df_risk.empty:
            risk_zone_year = df_risk.groupby(["annee", "zone5"])[risk_col].mean().reset_index()
            fig_risk_zone = px.line(risk_zone_year, x="annee", y=risk_col, color="zone5", markers=True)
            st.plotly_chart(fig_risk_zone, use_container_width=True)
        else:
            st.info("Pas de données suffisantes pour tracer l'évolution.")

        st.markdown("---")
        st.subheader("Prévision de la population exposée (2026–2030)")

        df_pop_evol = df_pop.dropna(subset=["annee"]).copy()
        if zone_sel != "Toutes":
            df_pop_evol = df_pop_evol[df_pop_evol["zone5"] == zone_sel]
        if region_sel != "Toutes":
            df_pop_evol = df_pop_evol[df_pop_evol["region"] == region_sel]
        if dep_sel != "Tous":
            df_pop_evol = df_pop_evol[df_pop_evol["nom_departement"] == dep_sel]

        if HAS_SKLEARN and not df_pop_evol.empty:
            pop_year = df_pop_evol.groupby("annee")["population_exposee"].sum().reset_index()
            if pop_year["annee"].nunique() >= 2:
                import numpy as np
                X = pop_year["annee"].values.reshape(-1, 1)
                y = pop_year["population_exposee"].values
                model = LinearRegression().fit(X, y)

                years_future = np.array([2026, 2027, 2028, 2029, 2030]).reshape(-1, 1)
                preds = model.predict(years_future)

                df_future = pd.DataFrame({"annee": [2026, 2027, 2028, 2029, 2030], "population_predite": preds})
                df_plot = pop_year.merge(df_future, on="annee", how="outer")

                fig_prev = px.line(df_plot, x="annee", y=["population_exposee", "population_predite"])
                st.plotly_chart(fig_prev, use_container_width=True)
            else:
                st.info("Pas assez d'années pour entraîner une prévision.")
        else:
            st.info("Prévisions non disponibles (sklearn absent ou données insuffisantes).")

    st.markdown("---")
    st.subheader("Synthèse automatique")

    try:
        zone_agg_full = dep_agg.groupby("zone5")["population_exposee"].sum().reset_index().sort_values("population_exposee", ascending=False)
        zone_top = zone_agg_full.iloc[0]["zone5"]
        pop_zone = int(zone_agg_full.iloc[0]["population_exposee"])

        dep_top = dff.sort_values("population_exposee", ascending=False).iloc[0]
        top_dep_name = dep_top["nom_departement"]
        top_dep_pop = int(dep_top["population_exposee"])

        txt = f"""
- Population exposée (filtres) : **{int(dff["population_exposee"].sum()):,} habitants**
- Part de l'exposition nationale : **{(dff["population_exposee"].sum() / total_pop * 100 if total_pop else 0):.1f} %**
- Zone la plus exposée : **{zone_top}** avec **{pop_zone:,} habitants**
- Département le plus exposé : **{top_dep_name}** avec **{top_dep_pop:,} habitants**
"""
        st.markdown(txt.replace(",", " "))
    except Exception:
        st.info("Impossible de générer une synthèse.")

    with st.expander("Tableau détaillé (départements agrégés)"):
        st.dataframe(dff, use_container_width=True)


if __name__ == "__main__":
    main()
