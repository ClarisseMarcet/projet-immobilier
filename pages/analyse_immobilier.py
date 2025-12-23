import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from pathlib import Path
import plotly.io as pio

pio.templates.default = "plotly_white"
st.set_page_config(page_title="Analyse immobilière", layout="wide")



# FONCTIONS MAPPING ZONES

def map_region(dep: str) -> str:
    if dep is None:
        return "Région inconnue"
    d = str(dep).strip()

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
    if d in ("16", "17", "19", "23", "24", "33", "40", "47", "64", "79", "86", "87"):
        return "Nouvelle-Aquitaine"
    if d in ("03", "15", "43", "63", "07", "26", "38", "42", "69", "73", "74", "01"):
        return "Auvergne-Rhône-Alpes"
    if d in ("09", "11", "12", "30", "31", "32", "34", "46", "48", "65", "66", "81", "82"):
        return "Occitanie"
    if d in ("04", "05", "06", "13", "83", "84"):
        return "Provence-Alpes-Côte d’Azur"
    return "Région inconnue"


def map_zone_macro(region: str) -> str:
    if region in ("Hauts-de-France", "Normandie"):
        return "Nord"
    if region == "Grand Est":
        return "Est"
    if region in ("Bretagne", "Pays de la Loire"):
        return "Ouest"
    if region in ("Occitanie", "Provence-Alpes-Côte d’Azur", "Corse"):
        return "Sud"
    return "Centre"






# CHARGEMENT DES DONNÉES


@st.cache_data
def load_data():
    BASE_DIR = Path(__file__).resolve().parents[1]
    data_path = BASE_DIR / "data" / "base_finale_dashboard.csv"

    if not data_path.exists():
        st.error(f"Fichier introuvable : {data_path}")
        st.stop()

    df = pd.read_csv(
        data_path,
        dtype={"code_departement": str, "code_commune": str},
        low_memory=False
    )

    # --- Normalisation codes
    if "code_departement" in df.columns:
        df["code_departement"] = (
            df["code_departement"]
            .astype(str)
            .str.strip()
            .str.upper()
        )
        # zfill pour les codes numériques (01, 02, ...)
        df["code_departement"] = df["code_departement"].apply(
            lambda x: x.zfill(2) if x.isdigit() else x
        )

    if "code_commune" in df.columns:
        df["code_commune"] = df["code_commune"].astype(str).str.zfill(5)

    # --- Si prix_m2 absent, on essaie de le calculer
    if "prix_m2" not in df.columns:
        if {"valeur_fonciere", "surface_reelle_bati"}.issubset(df.columns):
            surf = pd.to_numeric(df["surface_reelle_bati"], errors="coerce")
            val = pd.to_numeric(df["valeur_fonciere"], errors="coerce")
            df["prix_m2"] = np.where((surf > 0) & (val > 0), val / surf, np.nan)

    # --- Nettoyage prix_m2 (si dispo)
    if "prix_m2" in df.columns:
        df["prix_m2"] = pd.to_numeric(df["prix_m2"], errors="coerce")
        df = df[df["prix_m2"].between(50, 30000, inclusive="both")]

    # --- Eviter KeyError nom_departement
    if "nom_departement" not in df.columns:
        if "code_departement" in df.columns:
            df["nom_departement"] = df["code_departement"]
        else:
            df["nom_departement"] = "N/A"

    # --- Zone (si absente)
    if "zone" not in df.columns:
        df["zone"] = "Autres"

    # --- Régions + zones A / C
    if "code_departement" in df.columns:
        df["region"] = df["code_departement"].apply(map_region)
        df["zone_macro"] = df["region"].apply(map_zone_macro)
        df["zone_fiscale"] = df["code_departement"].apply(map_zone_fiscale)
    else:
        df["region"] = "Région inconnue"
        df["zone_macro"] = "Centre"
        df["zone_fiscale"] = "Zone C"

    # --- Paris / Banlieue IDF
    df["zone_paris"] = "Autre"
    if "code_departement" in df.columns:
        df.loc[df["code_departement"] == "75", "zone_paris"] = "Paris"
        df.loc[df["code_departement"].isin(["77", "78", "91", "92", "93", "94", "95"]), "zone_paris"] = "Banlieue IDF"

    return df



# APP

def main():
    st.markdown("""
    <style>
        .stTabs [role="tablist"] {
            justify-content: space-between;
            display: flex;
            width: 100%;
            font-size: 1.05rem;
            font-weight: 600;
        }
        .stTabs [aria-selected="true"] {
            color: #B30000 !important;
            border-bottom: 3px solid #B30000 !important;
            font-weight: 900;
        }
        .stTabs [aria-selected="false"] {
            color: #888;
            opacity: 0.7;
        }
    </style>
    """, unsafe_allow_html=True)

    st.title("Analyse immobilière - Dashboard professionnel")

    df = load_data()
    count_col = pick_count_col(df)

    st.sidebar.header("Filtres principaux")

    if "annee" in df.columns:
        annees = sorted(df["annee"].dropna().unique())
        annees_options = ["Toutes"] + [str(int(a)) for a in annees]
        annee_sel = st.sidebar.selectbox(
            "Année",
            annees_options,
            index=len(annees_options) - 1 if len(annees_options) > 1 else 0
        )
    else:
        annee_sel = "Toutes"

    st.sidebar.markdown("---")

    # IMPORTANT: widgets bien en sidebar
    with st.sidebar.expander("Filtres zones (A / C)", expanded=False):
        zm_options = ["Toutes"] + sorted(df["zone_macro"].dropna().unique()) if "zone_macro" in df.columns else ["Toutes"]
        zone_macro_sel = st.sidebar.selectbox("Zone macro (Nord / Sud / Est / Ouest / Centre)", zm_options)

        zf_options = ["Toutes"] + sorted(df["zone_fiscale"].dropna().unique()) if "zone_fiscale" in df.columns else ["Toutes"]
        zone_fiscale_sel = st.sidebar.selectbox("Zone fiscale (A / B1 / B2 / C)", zf_options)

    st.sidebar.markdown("---")

    regions = ["Toutes"] + sorted(df["region"].dropna().unique()) if "region" in df.columns else ["Toutes"]
    region_sel = st.sidebar.selectbox("Région", regions)

    deps = df["nom_departement"].dropna().unique() if "nom_departement" in df.columns else []
    deps_options = ["Tous"] + sorted(deps.tolist()) if hasattr(deps, "tolist") else ["Tous"]
    dep_sel = st.sidebar.selectbox("Département", deps_options)

    st.sidebar.markdown("---")

    types_bien = ["Tous"] + sorted(df["type_local"].dropna().unique()) if "type_local" in df.columns else ["Tous"]
    type_sel = st.sidebar.selectbox("Type de bien", types_bien)

    st.sidebar.markdown("---")

    if "prix_m2" in df.columns and not df["prix_m2"].dropna().empty:
        min_p = float(df["prix_m2"].min())
        max_p = float(df["prix_m2"].max())
    else:
        min_p, max_p = 0.0, 10000.0

    if int(min_p) >= int(max_p):
        st.sidebar.warning("Plage de prix insuffisante pour ce filtre.")
        prix_min, prix_max = int(min_p), int(max_p)
    else:
        prix_min, prix_max = st.sidebar.slider(
            "Filtre sur le prix au m²",
            min_value=int(min_p),
            max_value=int(max_p),
            value=(int(min_p), int(min_p + (max_p - min_p) * 0.7))
        )


    
    # APPLICATION DES FILTRES
    
    dff = df.copy()

    if annee_sel != "Toutes" and "annee" in dff.columns:
        annee_int = int(annee_sel)
        dff = dff[dff["annee"] == annee_int]
    else:
        annee_int = None

    if zone_macro_sel != "Toutes" and "zone_macro" in dff.columns:
        dff = dff[dff["zone_macro"] == zone_macro_sel]

    if zone_fiscale_sel != "Toutes" and "zone_fiscale" in dff.columns:
        dff = dff[dff["zone_fiscale"] == zone_fiscale_sel]

    if region_sel != "Toutes" and "region" in dff.columns:
        dff = dff[dff["region"] == region_sel]

    if dep_sel != "Tous" and "nom_departement" in dff.columns:
        dff = dff[dff["nom_departement"] == dep_sel]

    if type_sel != "Tous" and "type_local" in dff.columns:
        dff = dff[dff["type_local"] == type_sel]

    if "prix_m2" in dff.columns:
        dff = dff[(dff["prix_m2"] >= prix_min) & (dff["prix_m2"] <= prix_max)]

    if dff.empty:
        st.warning("Aucune donnée immobilière pour ces filtres.")
        return

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Vue générale",
        "Comparaisons départements",
        "Typologie des biens",
        "Tableaux & données",
        "Prévisions & tendances"
    ])

    # ---------------------------
    # TAB 1 – VUE GÉNÉRALE
    # ---------------------------
    with tab1:
        st.subheader("Indicateurs clés")

        k1, k2, k3, k4 = st.columns(4)

        prix_moy = dff["prix_m2"].mean() if "prix_m2" in dff.columns else None
        prix_med = dff["prix_m2"].median() if "prix_m2" in dff.columns else None

        if "nb_transactions" in dff.columns:
            nb_trans = int(pd.to_numeric(dff["nb_transactions"], errors="coerce").fillna(0).sum())
        else:
            nb_trans = len(dff)

        val_moy = dff["valeur_fonciere"].mean() if "valeur_fonciere" in dff.columns else None

        delta_txt = None
        if (
            prix_moy is not None
            and annee_sel != "Toutes"
            and "annee" in df.columns
            and "prix_m2" in df.columns
            and annee_int is not None
        ):
            prev_year = annee_int - 1
            df_prev = df.copy()

            if zone_macro_sel != "Toutes" and "zone_macro" in df_prev.columns:
                df_prev = df_prev[df_prev["zone_macro"] == zone_macro_sel]
            if zone_fiscale_sel != "Toutes" and "zone_fiscale" in df_prev.columns:
                df_prev = df_prev[df_prev["zone_fiscale"] == zone_fiscale_sel]
            if region_sel != "Toutes" and "region" in df_prev.columns:
                df_prev = df_prev[df_prev["region"] == region_sel]
            if dep_sel != "Tous" and "nom_departement" in df_prev.columns:
                df_prev = df_prev[df_prev["nom_departement"] == dep_sel]
            if type_sel != "Tous" and "type_local" in df_prev.columns:
                df_prev = df_prev[df_prev["type_local"] == type_sel]
            if "prix_m2" in df_prev.columns:
                df_prev = df_prev[(df_prev["prix_m2"] >= prix_min) & (df_prev["prix_m2"] <= prix_max)]

            df_prev = df_prev[df_prev["annee"] == prev_year] if "annee" in df_prev.columns else df_prev

            if not df_prev.empty and "prix_m2" in df_prev.columns:
                prix_prev = df_prev["prix_m2"].mean()
                if prix_prev and prix_prev > 0:
                    delta = (prix_moy / prix_prev - 1) * 100
                    delta_txt = f"{delta:,.1f} % vs {prev_year}"

        k1.metric("Prix moyen au m²", f"{prix_moy:,.0f} €" if prix_moy is not None else "N/A", delta=delta_txt)
        k2.metric("Prix médian au m²", f"{prix_med:,.0f} €" if prix_med is not None else "N/A")
        k3.metric("Nombre de transactions", f"{nb_trans:,}".replace(",", " "))
        k4.metric("Valeur foncière moyenne", f"{val_moy:,.0f} €" if val_moy is not None else "N/A")

        st.markdown("---")

        c1, c2 = st.columns([1.7, 1])

        with c1:
            st.subheader("Prix au m² par département")

            geo_url = "https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/departements.geojson"

            needed = {"code_departement", "nom_departement", "prix_m2"}
            if needed.issubset(dff.columns) and not dff["prix_m2"].dropna().empty:
                df_dep = (
                    dff.groupby(["code_departement", "nom_departement"], as_index=False)
                    .agg(
                        prix_m2=("prix_m2", "mean"),
                        nb=(count_col, "count")
                    )
                )

                # petite sécurité: il faut des codes non vides
                df_dep = df_dep[df_dep["code_departement"].notna() & (df_dep["code_departement"].astype(str).str.len() > 0)]

                if df_dep.empty:
                    st.info("Pas assez de données agrégées pour construire la carte.")
                else:
                    fig_map = px.choropleth(
                        df_dep,
                        geojson=geo_url,
                        locations="code_departement",
                        featureidkey="properties.code",
                        color="prix_m2",
                        color_continuous_scale="Blues",
                        hover_name="nom_departement",
                        hover_data={"prix_m2": True, "nb": True, "code_departement": False},
                        labels={"prix_m2": "Prix moyen au m²", "nb": "Nb transactions"}
                    )
                    fig_map.update_geos(fitbounds="locations", visible=False)
                    fig_map.update_layout(margin=dict(l=0, r=0, t=0, b=0))
                    st.plotly_chart(fig_map, use_container_width=True)
            else:
                st.info("Colonnes insuffisantes pour afficher la carte (code_departement / nom_departement / prix_m2).")

        with c2:
            st.subheader("Distribution des prix au m²")

            if "prix_m2" in dff.columns and not dff["prix_m2"].dropna().empty:
                hist_fig = px.histogram(
                    dff,
                    x="prix_m2",
                    nbins=50,
                    labels={"prix_m2": "Prix au m²"},
                )
                hist_fig.update_layout(
                    bargap=0.05,
                    xaxis_title="Prix au m²",
                    yaxis_title="Nombre de biens"
                )
                st.plotly_chart(hist_fig, use_container_width=True)
            else:
                st.info("Pas assez de données pour afficher la distribution des prix.")

        st.markdown("---")

        c3, c4 = st.columns([1.3, 1.2])

        with c3:
            st.subheader("Evolution du prix au m² par année")

            df_e = df.copy()
            if zone_macro_sel != "Toutes" and "zone_macro" in df_e.columns:
                df_e = df_e[df_e["zone_macro"] == zone_macro_sel]
            if zone_fiscale_sel != "Toutes" and "zone_fiscale" in df_e.columns:
                df_e = df_e[df_e["zone_fiscale"] == zone_fiscale_sel]
            if region_sel != "Toutes" and "region" in df_e.columns:
                df_e = df_e[df_e["region"] == region_sel]
            if dep_sel != "Tous" and "nom_departement" in df_e.columns:
                df_e = df_e[df_e["nom_departement"] == dep_sel]
            if type_sel != "Tous" and "type_local" in df_e.columns:
                df_e = df_e[df_e["type_local"] == type_sel]
            if "prix_m2" in df_e.columns:
                df_e = df_e[(df_e["prix_m2"] >= prix_min) & (df_e["prix_m2"] <= prix_max)]

                if "annee" in df_e.columns:
                    df_e = (
                        df_e.groupby("annee", as_index=False)
                        .agg(prix_m2=("prix_m2", "mean"), nb=(count_col, "count"))
                        .sort_values("annee")
                    )
                    df_e = df_e[df_e["nb"] >= 30].copy()

                    if not df_e.empty:
                        df_e["moving"] = df_e["prix_m2"].rolling(window=3, center=True).mean()
                        evol_fig = px.line(
                            df_e,
                            x="annee",
                            y=["prix_m2", "moving"],
                            markers=True,
                            labels={"annee": "Année", "value": "Prix moyen au m²", "variable": ""},
                        )
                        evol_fig.update_layout(legend_title_text="")
                        st.plotly_chart(evol_fig, use_container_width=True)

                        st.caption(
                            f"Évolution calculée uniquement pour les années ayant au moins 30 transactions. "
                            f"Total utilisé : {int(df_e['nb'].sum()):,}".replace(",", " ")
                        )
                    else:
                        st.info("Pas assez de données (≥ 30 transactions/an) pour afficher une évolution robuste.")
                else:
                    st.info("Colonne 'annee' manquante pour l'évolution.")
            else:
                st.info("Variable prix_m2 indisponible pour l'évolution.")

        with c4:
            st.subheader("Prix au m² vs surface")

            if "surface_reelle_bati" in dff.columns and "prix_m2" in dff.columns:
                scat_df = dff.dropna(subset=["surface_reelle_bati", "prix_m2"]).copy()
                scat_df["surface_reelle_bati"] = pd.to_numeric(scat_df["surface_reelle_bati"], errors="coerce")
                scat_df = scat_df.dropna(subset=["surface_reelle_bati", "prix_m2"])
                if not scat_df.empty:
                    if len(scat_df) > 5000:
                        scat_df = scat_df.sample(5000, random_state=42)
                    scat_fig = px.scatter(
                        scat_df,
                        x="surface_reelle_bati",
                        y="prix_m2",
                        color="type_local" if "type_local" in scat_df.columns else None,
                        hover_data=[c for c in ["valeur_fonciere", "commune", "nom_departement"] if c in scat_df.columns],
                        labels={
                            "surface_reelle_bati": "Surface réelle (m²)",
                            "prix_m2": "Prix au m²",
                            "type_local": "Type de bien"
                        }
                    )
                    st.plotly_chart(scat_fig, use_container_width=True)
                else:
                    st.info("Pas assez de données pour le nuage de points.")
            else:
                st.info("Variables surface ou prix manquantes pour le scatter.")


    
    ################### TAB 2 – COMPARAISONS DÉPARTEMENTS
    
    with tab2:
        st.subheader("Comparaison inter-départements")

        df_comp = df.copy()
        if annee_sel != "Toutes" and "annee" in df_comp.columns:
            df_comp = df_comp[df_comp["annee"] == int(annee_sel)]
        if zone_macro_sel != "Toutes" and "zone_macro" in df_comp.columns:
            df_comp = df_comp[df_comp["zone_macro"] == zone_macro_sel]
        if zone_fiscale_sel != "Toutes" and "zone_fiscale" in df_comp.columns:
            df_comp = df_comp[df_comp["zone_fiscale"] == zone_fiscale_sel]
        if region_sel != "Toutes" and "region" in df_comp.columns:
            df_comp = df_comp[df_comp["region"] == region_sel]
        if type_sel != "Tous" and "type_local" in df_comp.columns:
            df_comp = df_comp[df_comp["type_local"] == type_sel]
        if "prix_m2" in df_comp.columns:
            df_comp = df_comp[(df_comp["prix_m2"] >= prix_min) & (df_comp["prix_m2"] <= prix_max)]

        if {"code_departement", "nom_departement", "prix_m2"}.issubset(df_comp.columns):
            comp_agg = (
                df_comp.groupby(["code_departement", "nom_departement"], as_index=False)
                .agg(prix_m2=("prix_m2", "mean"), nb=(count_col, "count"))
                .dropna(subset=["prix_m2"])
            )
        else:
            comp_agg = pd.DataFrame()

        if comp_agg.empty:
            st.info("Pas assez de données pour la comparaison inter-départements.")
        else:
            moyenne_fr = comp_agg["prix_m2"].mean()
            comp_agg["indice_100"] = comp_agg["prix_m2"] / moyenne_fr * 100 if moyenne_fr and moyenne_fr > 0 else np.nan

            col_top, col_sel = st.columns([1.6, 1.4])

            with col_top:
                st.markdown("Classement des départements (indice 100 = moyenne France)")
                metric_sel = st.radio(
                    "Indicateur",
                    ["Prix moyen au m²", "Indice (France=100)", "Nombre de transactions"],
                    horizontal=True
                )

                if metric_sel == "Prix moyen au m²":
                    bar_fig = px.bar(
                        comp_agg.sort_values("prix_m2", ascending=False),
                        x="nom_departement",
                        y="prix_m2",
                        labels={"nom_departement": "Département", "prix_m2": "Prix moyen au m²"},
                    )
                elif metric_sel == "Indice (France=100)":
                    bar_fig = px.bar(
                        comp_agg.sort_values("indice_100", ascending=False),
                        x="nom_departement",
                        y="indice_100",
                        labels={"nom_departement": "Département", "indice_100": "Indice prix (France=100)"},
                    )
                else:
                    bar_fig = px.bar(
                        comp_agg.sort_values("nb", ascending=False),
                        x="nom_departement",
                        y="nb",
                        labels={"nom_departement": "Département", "nb": "Nombre de transactions"},
                    )

                bar_fig.update_layout(xaxis_tickangle=-60)
                st.plotly_chart(bar_fig, use_container_width=True)

            with col_sel:
                st.markdown("Comparaison A vs B")

                options_dep = sorted(comp_agg["nom_departement"].unique())
                if len(options_dep) >= 2:
                    depA = st.selectbox("Département A", options_dep, index=0)
                    depB = st.selectbox("Département B", options_dep, index=1)

                    dfA = comp_agg[comp_agg["nom_departement"] == depA].iloc[0]
                    dfB = comp_agg[comp_agg["nom_departement"] == depB].iloc[0]

                    cA, cB = st.columns(2)
                    with cA:
                        st.markdown(f"**{depA}**")
                        st.metric("Prix moyen au m²", f"{dfA['prix_m2']:,.0f} €")
                        st.metric("Indice prix (France=100)", f"{dfA['indice_100']:,.1f}")
                        st.metric("Nombre de transactions", f"{int(dfA['nb']):,}".replace(",", " "))
                    with cB:
                        st.markdown(f"**{depB}**")
                        st.metric("Prix moyen au m²", f"{dfB['prix_m2']:,.0f} €")
                        st.metric("Indice prix (France=100)", f"{dfB['indice_100']:,.1f}")
                        st.metric("Nombre de transactions", f"{int(dfB['nb']):,}".replace(",", " "))
                else:
                    st.info("Nombre de départements insuffisant pour comparaison A/B.")

        st.markdown("---")
        st.subheader("Paris vs Banlieue IDF (bouton dédié)")

        df_pb = df_comp.copy()
        df_paris = df_pb[df_pb["zone_paris"] == "Paris"] if "zone_paris" in df_pb.columns else df_pb.iloc[0:0]
        df_banl = df_pb[df_pb["zone_paris"] == "Banlieue IDF"] if "zone_paris" in df_pb.columns else df_pb.iloc[0:0]

        if st.button("Comparer Paris / Banlieue"):
            colP, colB = st.columns(2)
            with colP:
                st.markdown("**Paris (75)**")
                if not df_paris.empty and "prix_m2" in df_paris.columns:
                    st.metric("Prix moyen au m²", f"{df_paris['prix_m2'].mean():,.0f} €")
                else:
                    st.write("Pas de données pour Paris avec ces filtres.")

            with colB:
                st.markdown("**Banlieue IDF (77,78,91–95)**")
                if not df_banl.empty and "prix_m2" in df_banl.columns:
                    st.metric("Prix moyen au m²", f"{df_banl['prix_m2'].mean():,.0f} €")
                else:
                    st.write("Pas de données pour la banlieue avec ces filtres.")

            if (
                not df_paris.empty and not df_banl.empty
                and "prix_m2" in df_paris.columns and "prix_m2" in df_banl.columns
            ):
                comp = pd.DataFrame({
                    "Zone": ["Paris", "Banlieue IDF"],
                    "Prix moyen": [df_paris["prix_m2"].mean(), df_banl["prix_m2"].mean()]
                })
                figpb = px.bar(comp, x="Zone", y="Prix moyen", text="Prix moyen")
                figpb.update_traces(texttemplate="%{text:,.0f} €", textposition="outside")
                st.plotly_chart(figpb, use_container_width=True)

    
    
    ################ TAB 3 – TYPOLOGIE DES BIENS
    
    with tab3:
        st.subheader("Répartition par type de bien")

        if "type_local" in dff.columns and "prix_m2" in dff.columns:
            agg_type = (
                dff.groupby("type_local", as_index=False)
                .agg(prix_m2=("prix_m2", "mean"), nb=(count_col, "count"))
            )

            c1, c2 = st.columns([1.2, 1])

            with c1:
                bar_type = px.bar(
                    agg_type.sort_values("prix_m2", ascending=False),
                    x="type_local",
                    y="prix_m2",
                    labels={"type_local": "Type de bien", "prix_m2": "Prix moyen au m²"},
                )
                st.plotly_chart(bar_type, use_container_width=True)

            with c2:
                pie_type = px.pie(agg_type, names="type_local", values="nb")
                st.plotly_chart(pie_type, use_container_width=True)

            st.markdown("---")

            if "nom_departement" in dff.columns:
                st.subheader("Prix au m² par type et par département (top 10 départements)")

                dep_top = (
                    dff.groupby("nom_departement", as_index=False)[count_col]
                    .count()
                    .rename(columns={count_col: "nb"})
                    .sort_values("nb", ascending=False)
                    .head(10)["nom_departement"]
                    .tolist()
                )

                dft = dff[dff["nom_departement"].isin(dep_top)].copy()
                heat = dft.groupby(["nom_departement", "type_local"], as_index=False)["prix_m2"].mean()

                heat_fig = px.density_heatmap(
                    heat,
                    x="type_local",
                    y="nom_departement",
                    z="prix_m2",
                    color_continuous_scale="Viridis",
                    labels={"prix_m2": "Prix moyen au m²", "type_local": "Type", "nom_departement": "Département"},
                )
                st.plotly_chart(heat_fig, use_container_width=True)
        else:
            st.info("Variables 'type_local' ou 'prix_m2' manquantes pour cette analyse.")

    
    # TAB 4 – TABLEAUX & DONNÉES
    
    with tab4:
        st.subheader("Classement des communes selon le prix au m²")

        if "commune" not in dff.columns or "prix_m2" not in dff.columns:
            st.info("La colonne 'commune' ou 'prix_m2' n'est pas disponible dans la base.")
        else:
            group_cols = ["commune"]
            if "nom_departement" in dff.columns:
                group_cols.append("nom_departement")

            agg_commune = (
                dff.groupby(group_cols, as_index=False)["prix_m2"]
                .mean()
                .dropna(subset=["prix_m2"])
            )

            col_left, col_right = st.columns(2)

            with col_left:
                st.markdown("#### 🔝 Top 20 communes les plus chères")
                top20 = agg_commune.sort_values("prix_m2", ascending=False).head(20)
                st.dataframe(top20.reset_index(drop=True))

            with col_right:
                st.markdown("#### 🔻 Top 20 communes les moins chères")
                bottom20 = agg_commune.sort_values("prix_m2", ascending=True).head(20)
                st.dataframe(bottom20.reset_index(drop=True))

        st.markdown("---")
        st.subheader("Aperçu des données filtrées")
        st.dataframe(dff.head(300))

        csv = dff.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Télécharger les données filtrées (CSV)",
            data=csv,
            file_name="donnees_filtrees_immobilier.csv",
            mime="text/csv"
        )

    # ---------------------------
    # TAB 5 – PRÉVISIONS & TENDANCES
    # ---------------------------
    with tab5:
        st.subheader("Prévisions simples & tendances (prix moyen au m²)")

        df_fore = df.copy()
        if zone_macro_sel != "Toutes" and "zone_macro" in df_fore.columns:
            df_fore = df_fore[df_fore["zone_macro"] == zone_macro_sel]
        if zone_fiscale_sel != "Toutes" and "zone_fiscale" in df_fore.columns:
            df_fore = df_fore[df_fore["zone_fiscale"] == zone_fiscale_sel]
        if region_sel != "Toutes" and "region" in df_fore.columns:
            df_fore = df_fore[df_fore["region"] == region_sel]
        if dep_sel != "Tous" and "nom_departement" in df_fore.columns:
            df_fore = df_fore[df_fore["nom_departement"] == dep_sel]
        if type_sel != "Tous" and "type_local" in df_fore.columns:
            df_fore = df_fore[df_fore["type_local"] == type_sel]
        if "prix_m2" in df_fore.columns:
            df_fore = df_fore[(df_fore["prix_m2"] >= prix_min) & (df_fore["prix_m2"] <= prix_max)]

        if "annee" not in df_fore.columns or "prix_m2" not in df_fore.columns:
            st.info("Colonnes insuffisantes pour faire une prévision (annee / prix_m2).")
            return

        ts = (
            df_fore.groupby("annee", as_index=False)
            .agg(prix_m2=("prix_m2", "mean"), nb=(count_col, "count"))
            .sort_values("annee")
        )

        ts = ts[ts["nb"] >= 30].copy()

        if not ts.empty and ts["nb"].min() < 50:
            st.info(
                "Attention : certaines années reposent sur un nombre limité de transactions. "
                "La tendance doit être interprétée avec prudence."
            )

        if len(ts) < 3:
            st.info("Pas assez d'années (≥ 30 transactions/an) pour une prévision globale (minimum 3 années).")
        else:
            X = ts["annee"].values.astype(float)
            y = ts["prix_m2"].values.astype(float)

            coef = np.polyfit(X, y, 1)
            trend = np.poly1d(coef)

            last_year = int(ts["annee"].max())
            future_years = np.arange(last_year + 1, last_year + 4)
            future_prices = np.maximum(trend(future_years), 0)

            hist = ts.copy()
            hist["type"] = "Historique"
            df_fut = pd.DataFrame({"annee": future_years, "prix_m2": future_prices, "type": "Prévision"})

            full = pd.concat([hist[["annee", "prix_m2", "type"]], df_fut], ignore_index=True)

            fig_fore = px.line(
                full,
                x="annee",
                y="prix_m2",
                color="type",
                markers=True,
                labels={"annee": "Année", "prix_m2": "Prix moyen au m²", "type": ""},
            )
            st.plotly_chart(fig_fore, use_container_width=True)

            st.markdown("#### Prévisions (3 prochaines années)")
            prev_table = df_fut.copy()
            prev_table["prix_m2"] = prev_table["prix_m2"].round(0)
            prev_table = prev_table.rename(columns={"annee": "Année", "prix_m2": "Prix prévisionnel au m²"})
            st.dataframe(prev_table)

        st.markdown("---")
        st.subheader("Tendance par zone macro / fiscale")

        colz1, colz2 = st.columns(2)

        with colz1:
            st.markdown("**Tendance par zone macro (Nord/Sud/Est/Ouest/Centre)**")
            if {"annee", "zone_macro", "prix_m2"}.issubset(df.columns):
                zone_ts = (
                    df.groupby(["annee", "zone_macro"], as_index=False)["prix_m2"]
                    .mean()
                    .sort_values(["zone_macro", "annee"])
                )
                if not zone_ts.empty:
                    fig_zone = px.line(
                        zone_ts,
                        x="annee",
                        y="prix_m2",
                        color="zone_macro",
                        markers=True,
                        labels={"annee": "Année", "prix_m2": "Prix moyen au m²", "zone_macro": "Zone macro"},
                    )
                    st.plotly_chart(fig_zone, use_container_width=True)

        with colz2:
            st.markdown("**Tendance par zone fiscale (A / B1 / B2 / C)**")
            if {"annee", "zone_fiscale", "prix_m2"}.issubset(df.columns):
                zf_ts = (
                    df.groupby(["annee", "zone_fiscale"], as_index=False)["prix_m2"]
                    .mean()
                    .sort_values(["zone_fiscale", "annee"])
                )
                if not zf_ts.empty:
                    fig_zf = px.line(
                        zf_ts,
                        x="annee",
                        y="prix_m2",
                        color="zone_fiscale",
                        markers=True,
                        labels={"annee": "Année", "prix_m2": "Prix moyen au m²", "zone_fiscale": "Zone fiscale"},
                    )
                    st.plotly_chart(fig_zf, use_container_width=True)

        st.markdown("---")
        st.subheader("Tendance par type de bien (global France)")

        if {"annee", "type_local", "prix_m2"}.issubset(df.columns):
            type_ts = (
                df.groupby(["annee", "type_local"], as_index=False)["prix_m2"]
                .mean()
                .sort_values(["type_local", "annee"])
            )
            if not type_ts.empty:
                fig_type_ts = px.line(
                    type_ts,
                    x="annee",
                    y="prix_m2",
                    color="type_local",
                    markers=True,
                    labels={"annee": "Année", "prix_m2": "Prix moyen au m²", "type_local": "Type de bien"},
                )
                st.plotly_chart(fig_type_ts, use_container_width=True)

        st.markdown("---")
        st.subheader("Synthèse automatique (lecture Data Scientist)")

        try:
            prix_global = df["prix_m2"].mean() if "prix_m2" in df.columns else np.nan
            prix_filtre = dff["prix_m2"].mean() if "prix_m2" in dff.columns else np.nan
            txt = f"""
- Prix moyen national (toutes données) : **{prix_global:,.0f} € / m²**
- Prix moyen avec vos filtres : **{prix_filtre:,.0f} € / m²**
- Zone macro sélectionnée : **{zone_macro_sel if zone_macro_sel != 'Toutes' else 'Toutes'}**
- Zone fiscale sélectionnée : **{zone_fiscale_sel if zone_fiscale_sel != 'Toutes' else 'Toutes'}**
"""
            st.markdown(txt.replace(",", " "))
        except Exception:
            st.info("Impossible de générer une synthèse automatique.")


if __name__ == "__main__":
    main()
