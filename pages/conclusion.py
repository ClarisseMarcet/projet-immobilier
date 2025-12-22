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
    return f"<span style='color:{color}; font-weight:750;'>{txt}</span>"


def classify_vs_reference(value: float, ref: float, tol: float = 0.02):
    """
    Retourne (label, color) selon comparaison à une référence :
    - 'moins' si value < ref*(1-tol)
    - 'moyenne' si dans +/- tol
    - 'plus' si value > ref*(1+tol)
    """
    if pd.isna(value) or pd.isna(ref) or ref == 0:
        return ("non disponible", "#7f8c8d")

    if value < ref * (1 - tol):
        return ("moins", "#27ae60")
    if value > ref * (1 + tol):
        return ("plus", "#c0392b")
    return ("moyenne", "#f39c12")


# =========================
# CHARGEMENT DES DONNÉES
# =========================

@st.cache_data
def load_data():
    base_dir = Path(__file__).resolve().parents[1]
    path = base_dir / "data" / "base_finale_dashboard.csv"

    df = pd.read_csv(path, dtype={"code_departement": str}, low_memory=False)

    # Normalisation
    if "code_departement" in df.columns:
        df["code_departement"] = df["code_departement"].astype(str).str.strip().str.upper()
        mask_corse = df["code_departement"].isin(["2A", "2B"])
        df.loc[~mask_corse, "code_departement"] = df.loc[~mask_corse, "code_departement"].str.zfill(2)

    if "nom_departement" not in df.columns:
        df["nom_departement"] = df["code_departement"]

    if "zone" not in df.columns:
        df["zone"] = "Centre"
    df["zone"] = df["zone"].replace("Autres", "Centre")

    # Colonnes attendues
    if "region" not in df.columns:
        df["region"] = pd.NA
    df["region"] = df["region"].replace("", pd.NA)

    if "annee" in df.columns:
        df["annee"] = pd.to_numeric(df["annee"], errors="coerce")

    if "prix_m2" not in df.columns:
        df["prix_m2"] = pd.NA

    if "risque_climatique" not in df.columns:
        df["risque_climatique"] = pd.NA

    # =========================
    # REMPLISSAGE DES RÉGIONS (par code département)
    # =========================
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

        # Corse
        "2A": "Corse", "2B": "Corse",
    }

    df["region"] = df["region"].fillna(df["code_departement"].map(regions_par_departement))
    df["region"] = df["region"].fillna("Non renseignée")

    return df


# =========================
# PAGE PRINCIPALE
# =========================

def main():
    st.title("Conclusion – Lecture globale et interprétation")
    df = load_data()

    st.sidebar.header("Filtres géographiques")

    # Zone
    zone_sel = st.sidebar.selectbox("Zone", ["Toutes"] + sorted(df["zone"].dropna().unique()))
    df_zone = df if zone_sel == "Toutes" else df[df["zone"] == zone_sel]

    # Région (dépend de la zone)
    region_dispo = sorted(df_zone["region"].dropna().unique())
    region_sel = st.sidebar.selectbox("Région", ["Toutes"] + region_dispo)
    if region_sel != "Toutes" and region_sel not in region_dispo:
        region_sel = "Toutes"
    df_region = df_zone if region_sel == "Toutes" else df_zone[df_zone["region"] == region_sel]

    # Département (dépend de zone + région)
    dep_dispo = sorted(df_region["nom_departement"].dropna().unique())
    dep_sel = st.sidebar.selectbox("Département", ["Tous les départements"] + dep_dispo)
    if dep_sel != "Tous les départements" and dep_sel not in dep_dispo:
        dep_sel = "Tous les départements"

    # Autres filtres
    type_sel = st.sidebar.selectbox("Type de bien", ["Tous"] + sorted(df["type_local"].dropna().unique()))
    year_sel = st.sidebar.selectbox("Année", ["Toutes"] + sorted(df["annee"].dropna().unique()))

    # Application des filtres
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

    # Indicateurs globaux
    prix_moy = dff["prix_m2"].mean()
    prix_nat = df["prix_m2"].mean()

    risque_moy = dff["risque_climatique"].mean()
    risque_nat = df["risque_climatique"].mean()

    # Statut vs national (moins / moyenne / plus)
    prix_status, prix_color = classify_vs_reference(prix_moy, prix_nat, tol=0.02)
    risque_status, risque_color = classify_vs_reference(risque_moy, risque_nat, tol=0.02)

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Prix moyen local", f"{prix_moy:,.0f} €".replace(",", " ") if pd.notna(prix_moy) else "N/A")
    k2.metric("Prix moyen national", f"{prix_nat:,.0f} €".replace(",", " ") if pd.notna(prix_nat) else "N/A")
    k3.metric("Risque climatique local", f"{risque_moy:.2f}" if pd.notna(risque_moy) else "N/A")
    k4.metric("Risque climatique national", f"{risque_nat:.2f}" if pd.notna(risque_nat) else "N/A")

    # Tabs (sans les bandes blanches)
    geo_url = "https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/departements.geojson"
    tab_immo, tab_clim = st.tabs(["Synthèse immobilière", "Synthèse climatique"])

    # =========================
    # ONGLET IMMOBILIER
    # =========================
    with tab_immo:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Analyse immobilière</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-subtitle'>Carte des prix au m² et lecture par rapport à la France</div>", unsafe_allow_html=True)

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
                hover_name="nom_departement",
                labels={"prix_m2": "Prix moyen au m²"}
            )
            fig.update_geos(fitbounds="locations", visible=False)
            fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
            st.plotly_chart(fig, use_container_width=True)

        # Conclusion spécifique immobilier
        if prix_status == "moins":
            prix_phrase = "moins cher"
        elif prix_status == "plus":
            prix_phrase = "plus cher"
        elif prix_status == "moyenne":
            prix_phrase = "dans la moyenne"
        else:
            prix_phrase = "non disponible"

        st.markdown(
            f"""
            <div style="text-align:center; margin-top:8px; margin-bottom:10px;">
                <span class="badge">{zone_sel}</span>
                <span class="badge">{region_sel}</span>
                <span class="badge" style="background:#dff9fb; color:#130f40;">{dep_sel}</span>
            </div>

            Dans ce périmètre, le **prix moyen** est de **{highlight(f"{prix_moy:,.0f} € / m²".replace(",", " "), prix_color)}**,
            contre **{highlight(f"{prix_nat:,.0f} € / m²".replace(",", " "), "#7f8c8d")}** au niveau national.

            Lecture : le marché local est **{highlight(prix_phrase, prix_color)}** par rapport à la France.
            """,
            unsafe_allow_html=True
        )

        st.markdown("</div>", unsafe_allow_html=True)

    # =========================
    # ONGLET CLIMAT
    # =========================
    with tab_clim:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Analyse climatique</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-subtitle'>Carte du risque climatique et lecture par rapport à la France</div>", unsafe_allow_html=True)

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
                hover_name="nom_departement",
                labels={"risque": "Indice de risque climatique"}
            )
            fig.update_geos(fitbounds="locations", visible=False)
            fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
            st.plotly_chart(fig, use_container_width=True)

        # Conclusion spécifique climat
        if risque_status == "moins":
            risque_phrase = "moins exposé"
        elif risque_status == "plus":
            risque_phrase = "plus exposé"
        elif risque_status == "moyenne":
            risque_phrase = "dans la moyenne"
        else:
            risque_phrase = "non disponible"

        st.markdown(
            f"""
            <div style="text-align:center; margin-top:8px; margin-bottom:10px;">
                <span class="badge">{zone_sel}</span>
                <span class="badge">{region_sel}</span>
                <span class="badge" style="background:#dff9fb; color:#130f40;">{dep_sel}</span>
            </div>

            Dans ce périmètre, l’**indice de risque climatique moyen** est de **{highlight(f"{risque_moy:.2f}", risque_color)}**,
            contre **{highlight(f"{risque_nat:.2f}", "#7f8c8d")}** au niveau national.

            Lecture : le territoire est **{highlight(risque_phrase, risque_color)}** aux aléas climatiques par rapport à la France.
            """,
            unsafe_allow_html=True
        )

        st.markdown("</div>", unsafe_allow_html=True)

    # =========================
    # CONCLUSION GÉNÉRALE (transversale)
    # =========================
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Conclusion générale</div>", unsafe_allow_html=True)

    st.markdown(
        f"""
        <div style="text-align:center; margin-bottom:14px;">
            <span class="badge">{zone_sel}</span>
            <span class="badge">{region_sel}</span>
            <span class="badge" style="background:#dff9fb; color:#130f40;">{dep_sel}</span>
        </div>

        Cette synthèse met en évidence deux lectures complémentaires :
        <ul>
            <li>Une lecture **immobilière** : le territoire est <b>{highlight("moins cher" if prix_status=="moins" else ("plus cher" if prix_status=="plus" else "dans la moyenne"), prix_color)}</b> par rapport à la moyenne nationale.</li>
            <li>Une lecture **climatique** : le territoire est <b>{highlight("moins exposé" if risque_status=="moins" else ("plus exposé" if risque_status=="plus" else "dans la moyenne"), risque_color)}</b> par rapport à la France.</li>
        </ul>

        L’objectif de cette page est de fournir une conclusion lisible :  
        **le prix décrit l’accessibilité du marché**, et **le risque décrit le contexte d’exposition**.
        """,
        unsafe_allow_html=True
    )

    st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
