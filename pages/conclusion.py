import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="Conclusion", layout="wide")

# UTILITAIRE VISUEL

def highlight(txt, color="#e74c3c"):
    return f"<span style='color:{color}; font-weight:700;'>{txt}</span>"


# CHARGEMENT DES DONNÉES

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

    # On garde ta logique, mais on s'assure que region existe même si vide
    if "region" not in df.columns:
        df["region"] = pd.NA

    if "annee" in df.columns:
        df["annee"] = pd.to_numeric(df["annee"], errors="coerce")

    if "prix_m2" not in df.columns:
        df["prix_m2"] = pd.NA

    if "risque_climatique" not in df.columns:
        df["risque_climatique"] = pd.NA

    # -------------------------
    # REMPLISSAGE DES RÉGIONS (seule correction demandée)
    # -------------------------
    regions_par_departement = {
        # Auvergne-Rhône-Alpes
        "01": "Auvergne-Rhône-Alpes", "03": "Auvergne-Rhône-Alpes", "07": "Auvergne-Rhône-Alpes",
        "15": "Auvergne-Rhône-Alpes", "26": "Auvergne-Rhône-Alpes", "38": "Auvergne-Rhône-Alpes",
        "42": "Auvergne-Rhône-Alpes", "43": "Auvergne-Rhône-Alpes", "63": "Auvergne-Rhône-Alpes",
        "69": "Auvergne-Rhône-Alpes", "73": "Auvergne-Rhône-Alpes", "74": "Auvergne-Rhône-Alpes",

        # Bourgogne-Franche-Comté
        "21": "Bourgogne-Franche-Comté", "25": "Bourgogne-Franche-Comté",
        "39": "Bourgogne-Franche-Comté", "58": "Bourgogne-Franche-Comté",
        "70": "Bourgogne-Franche-Comté", "71": "Bourgogne-Franche-Comté",
        "89": "Bourgogne-Franche-Comté", "90": "Bourgogne-Franche-Comté",

        # Bretagne
        "22": "Bretagne", "29": "Bretagne", "35": "Bretagne", "56": "Bretagne",

        # Centre-Val de Loire
        "18": "Centre-Val de Loire", "28": "Centre-Val de Loire",
        "36": "Centre-Val de Loire", "37": "Centre-Val de Loire",
        "41": "Centre-Val de Loire", "45": "Centre-Val de Loire",

        # Grand Est
        "08": "Grand Est", "10": "Grand Est", "51": "Grand Est",
        "52": "Grand Est", "54": "Grand Est", "55": "Grand Est",
        "57": "Grand Est", "67": "Grand Est", "68": "Grand Est",
        "88": "Grand Est",

        # Hauts-de-France
        "02": "Hauts-de-France", "59": "Hauts-de-France", "60": "Hauts-de-France",
        "62": "Hauts-de-France", "80": "Hauts-de-France",

        # Île-de-France
        "75": "Île-de-France", "77": "Île-de-France", "78": "Île-de-France",
        "91": "Île-de-France", "92": "Île-de-France", "93": "Île-de-France",
        "94": "Île-de-France", "95": "Île-de-France",

        # Normandie
        "14": "Normandie", "27": "Normandie", "50": "Normandie",
        "61": "Normandie", "76": "Normandie",

        # Nouvelle-Aquitaine
        "16": "Nouvelle-Aquitaine", "17": "Nouvelle-Aquitaine", "19": "Nouvelle-Aquitaine",
        "23": "Nouvelle-Aquitaine", "24": "Nouvelle-Aquitaine", "33": "Nouvelle-Aquitaine",
        "40": "Nouvelle-Aquitaine", "47": "Nouvelle-Aquitaine", "64": "Nouvelle-Aquitaine",
        "79": "Nouvelle-Aquitaine", "86": "Nouvelle-Aquitaine", "87": "Nouvelle-Aquitaine",

        # Occitanie
        "09": "Occitanie", "11": "Occitanie", "12": "Occitanie", "30": "Occitanie",
        "31": "Occitanie", "32": "Occitanie", "34": "Occitanie", "46": "Occitanie",
        "48": "Occitanie", "65": "Occitanie", "66": "Occitanie", "81": "Occitanie",
        "82": "Occitanie",

        # Pays de la Loire
        "44": "Pays de la Loire", "49": "Pays de la Loire",
        "53": "Pays de la Loire", "72": "Pays de la Loire", "85": "Pays de la Loire",

        # Provence-Alpes-Côte d’Azur
        "04": "Provence-Alpes-Côte d’Azur", "05": "Provence-Alpes-Côte d’Azur",
        "06": "Provence-Alpes-Côte d’Azur", "13": "Provence-Alpes-Côte d’Azur",
        "83": "Provence-Alpes-Côte d’Azur", "84": "Provence-Alpes-Côte d’Azur",

        # (Optionnel) Corse si jamais tu l'as mais tu filtres 01-95 ensuite
        "2A": "Corse", "2B": "Corse",
    }

    # Remplir seulement les valeurs manquantes/vides
    # 1) uniformiser les "vides" en NA
    df["region"] = df["region"].replace("", pd.NA)

    # 2) compléter via le code département
    df["region"] = df["region"].fillna(df["code_departement"].map(regions_par_departement))

    # 3) fallback
    df["region"] = df["region"].fillna("Non renseignée")

    # France métropolitaine uniquement (01 à 95)
    df = df[df["code_departement"].str.match(r"^\d{2}$")]
    df = df[df["code_departement"].astype(int).between(1, 95)]

    return df


# PAGE PRINCIPALE

def main():
    st.title("Conclusion – Synthèse des résultats")

    df = load_data()

    
    # FILTRES DÉPENDANTS
    
    st.sidebar.header("Filtres")

    zone_sel = st.sidebar.selectbox(
        "Zone",
        ["Toutes"] + sorted(df["zone"].dropna().unique())
    )

    df_zone = df.copy()
    if zone_sel != "Toutes":
        df_zone = df_zone[df_zone["zone"] == zone_sel]

    region_sel = st.sidebar.selectbox(
        "Région",
        ["Toutes"] + sorted(df_zone["region"].dropna().unique())
    )

    df_region = df_zone.copy()
    if region_sel != "Toutes":
        df_region = df_region[df_region["region"] == region_sel]

    dep_sel = st.sidebar.selectbox(
        "Département",
        ["Tous les départements"] + sorted(df_region["nom_departement"].dropna().unique())
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

    
    # SOUS-PAGES (ESPACÉES)
    
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    tab_immo, tab_clim = st.tabs(["Synthèse immobilière", "Synthèse climatique"])
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    geo_url = "https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/departements.geojson"

    
    # IMMOBILIER
    
    with tab_immo:
        st.subheader("Carte des prix immobiliers")

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
            labels={"prix_m2": "Prix moyen au m²"}
        )
        fig.update_geos(fitbounds="locations", visible=False)
        st.plotly_chart(fig, use_container_width=True)

        prix_moy = dff["prix_m2"].mean()
        prix_nat = df["prix_m2"].mean()

        st.markdown(f"""
**Filtres appliqués :**  
Zone : {highlight(zone_sel, "#f39c12")}  
Région : {highlight(region_sel, "#3498db")}  
Département : {highlight(dep_sel, "#2ecc71")}  
Type de bien : {highlight(type_sel, "#9b59b6")}  
Année : {highlight(year_sel, "#e67e22")}

Dans ce périmètre, le **prix moyen observé** est de **{highlight(f"{prix_moy:,.0f} € / m²")}**.  
À titre de repère, la **moyenne nationale** est de **{highlight(f"{prix_nat:,.0f} € / m²", "#7f8c8d")}**.

Cela signifie que, sur ce territoire, le marché immobilier est **{"plus accessible" if prix_moy < prix_nat else "plus cher"}** que la moyenne observée en France.

**Lecture simple :**  
- Le **territoire** (zone, région, département) joue un rôle majeur sur les prix.  
- Le **type de bien** modifie sensiblement le niveau de prix.  
- L’**année** permet de replacer ces prix dans leur contexte d’évolution.
""".replace(",", " "), unsafe_allow_html=True)

    
    # CLIMAT
    
    with tab_clim:
        st.subheader("Carte des risques climatiques")

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
            labels={"risque": "Indice de risque climatique"}
        )
        fig.update_geos(fitbounds="locations", visible=False)
        st.plotly_chart(fig, use_container_width=True)

        risque_moy = dff["risque_climatique"].mean()
        risque_nat = df["risque_climatique"].mean()

        st.markdown(f"""
**Filtres appliqués :**  
Zone : {highlight(zone_sel, "#f39c12")}  
Région : {highlight(region_sel, "#3498db")}  
Département : {highlight(dep_sel, "#2ecc71")}  
Année : {highlight(year_sel, "#e67e22")}

Le **niveau de risque moyen** observé est de **{highlight(f"{risque_moy:.2f}")}**,  
contre **{highlight(f"{risque_nat:.2f}", "#7f8c8d")}** en moyenne nationale.

Cela indique que le territoire étudié est **{"plus exposé" if risque_moy > risque_nat else "moins exposé"}** aux aléas climatiques que la moyenne.

**Lecture simple :**  
- Tous les territoires ne sont pas exposés de la même manière.  
- Le risque constitue un **facteur de contexte**, mais **n’explique pas seul** les niveaux de prix immobiliers.
""", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
