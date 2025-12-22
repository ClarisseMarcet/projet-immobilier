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

    df = pd.read_csv(
        path,
        dtype={"code_departement": str},
        low_memory=False
    )

    # Normalisation
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

    # =========================
    # REMPLISSAGE DES RÉGIONS
    # =========================

    regions_par_departement = {
        "01": "Auvergne-Rhône-Alpes", "03": "Auvergne-Rhône-Alpes", "07": "Auvergne-Rhône-Alpes",
        "15": "Auvergne-Rhône-Alpes", "26": "Auvergne-Rhône-Alpes", "38": "Auvergne-Rhône-Alpes",
        "42": "Auvergne-Rhône-Alpes", "43": "Auvergne-Rhône-Alpes", "63": "Auvergne-Rhône-Alpes",
        "69": "Auvergne-Rhône-Alpes", "73": "Auvergne-Rhône-Alpes", "74": "Auvergne-Rhône-Alpes",

        "21": "Bourgogne-Franche-Comté", "25": "Bourgogne-Franche-Comté",
        "39": "Bourgogne-Franche-Comté", "58": "Bourgogne-Franche-Comté",
        "70": "Bourgogne-Franche-Comté", "71": "Bourgogne-Franche-Comté",
        "89": "Bourgogne-Franche-Comté", "90": "Bourgogne-Franche-Comté",

        "22": "Bretagne", "29": "Bretagne", "35": "Bretagne", "56": "Bretagne",

        "18": "Centre-Val de Loire", "28": "Centre-Val de Loire",
        "36": "Centre-Val de Loire", "37": "Centre-Val de Loire",
        "41": "Centre-Val de Loire", "45": "Centre-Val de Loire",

        "08": "Grand Est", "10": "Grand Est", "51": "Grand Est",
        "52": "Grand Est", "54": "Grand Est", "55": "Grand Est",
        "57": "Grand Est", "67": "Grand Est", "68": "Grand Est",
        "88": "Grand Est",

        "02": "Hauts-de-France", "59": "Hauts-de-France", "60": "Hauts-de-France",
        "62": "Hauts-de-France", "80": "Hauts-de-France",

        "75": "Île-de-France", "77": "Île-de-France", "78": "Île-de-France",
        "91": "Île-de-France", "92": "Île-de-France", "93": "Île-de-France",
        "94": "Île-de-France", "95": "Île-de-France",

        "14": "Normandie", "27": "Normandie", "50": "Normandie",
        "61": "Normandie", "76": "Normandie",

        "16": "Nouvelle-Aquitaine", "17": "Nouvelle-Aquitaine", "19": "Nouvelle-Aquitaine",
        "23": "Nouvelle-Aquitaine", "24": "Nouvelle-Aquitaine", "33": "Nouvelle-Aquitaine",
        "40": "Nouvelle-Aquitaine", "47": "Nouvelle-Aquitaine", "64": "Nouvelle-Aquitaine",
        "79": "Nouvelle-Aquitaine", "86": "Nouvelle-Aquitaine", "87": "Nouvelle-Aquitaine",

        "09": "Occitanie", "11": "Occitanie", "12": "Occitanie", "30": "Occitanie",
        "31": "Occitanie", "32": "Occitanie", "34": "Occitanie", "46": "Occitanie",
        "48": "Occitanie", "65": "Occitanie", "66": "Occitanie", "81": "Occitanie",
        "82": "Occitanie",

        "44": "Pays de la Loire", "49": "Pays de la Loire",
        "53": "Pays de la Loire", "72": "Pays de la Loire", "85": "Pays de la Loire",

        "04": "Provence-Alpes-Côte d’Azur", "05": "Provence-Alpes-Côte d’Azur",
        "06": "Provence-Alpes-Côte d’Azur", "13": "Provence-Alpes-Côte d’Azur",
        "83": "Provence-Alpes-Côte d’Azur", "84": "Provence-Alpes-Côte d’Azur",
    }

    df["region"] = df["region"].replace("", pd.NA)
    df["region"] = df["region"].fillna(df["code_departement"].map(regions_par_departement))
    df["region"] = df["region"].fillna("Non renseignée")

    df = df[df["code_departement"].str.match(r"^\d{2}$")]
    df = df[df["code_departement"].astype(int).between(1, 95)]

    return df



# PAGE PRINCIPALE


def main():
    st.title("Conclusion – Synthèse des résultats")

    st.markdown(
        "Cette page propose une **lecture transversale** des résultats, "
        "en croisant **marché immobilier** et **exposition climatique**, "
        "à partir des filtres sélectionnés.",
        unsafe_allow_html=True
    )

    st.markdown("---")

    df = load_data()


    # FILTRES


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


    # APPLICATION DES FILTRES


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


    # KPI SYNTHÈSE
  

    st.subheader("Indicateurs clés de synthèse")

    prix_moy = dff["prix_m2"].mean()
    prix_nat = df["prix_m2"].mean()
    risque_moy = dff["risque_climatique"].mean()
    risque_nat = df["risque_climatique"].mean()

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Prix moyen au m²", f"{prix_moy:,.0f} €".replace(",", " "))
    k2.metric("Prix moyen national", f"{prix_nat:,.0f} €".replace(",", " "))
    k3.metric("Risque climatique moyen", f"{risque_moy:.2f}")
    k4.metric("Risque climatique national", f"{risque_nat:.2f}")

    st.markdown("---")

    tab_immo, tab_clim = st.tabs(["Synthèse immobilière", "Synthèse climatique"])

    geo_url = "https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/departements.geojson"


    # IMMOBILIER
  

    with tab_immo:
        st.subheader("Lecture consolidée du marché immobilier")

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

        st.markdown(f"""
Dans le périmètre sélectionné :
- **Prix moyen observé** : {highlight(f"{prix_moy:,.0f} € / m²")}
- **Moyenne nationale** : {highlight(f"{prix_nat:,.0f} € / m²", "#7f8c8d")}

Le marché local est **{"plus accessible" if prix_moy < prix_nat else "plus cher"}** que la moyenne française.
""".replace(",", " "), unsafe_allow_html=True)


    # CLIMAT


    with tab_clim:
        st.subheader("Lecture consolidée du risque climatique")

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

        st.markdown(f"""
- **Risque moyen observé** : {highlight(f"{risque_moy:.2f}")}
- **Moyenne nationale** : {highlight(f"{risque_nat:.2f}", "#7f8c8d")}

Le territoire est **{"plus exposé" if risque_moy > risque_nat else "moins exposé"}** que la moyenne nationale.
""", unsafe_allow_html=True)

    st.markdown("---")

    st.subheader("Conclusion générale")

    st.markdown("""
Cette analyse montre que **les dynamiques immobilières et climatiques doivent être interprétées conjointement**.  
Le climat agit comme un **facteur de risque structurel**, tandis que les prix immobiliers restent fortement dépendants
de la **localisation**, du **type de bien** et du **contexte territorial**.

Cette approche croisée apporte une **lecture plus réaliste, plus nuancée et plus opérationnelle** des territoires.
""")


if __name__ == "__main__":
    main()
