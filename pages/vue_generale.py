import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path


def load_data():
    data_path = Path("data/base_finale_dashboard.csv")

    if not data_path.exists():
        raise FileNotFoundError(f"Fichier introuvable : {data_path}")

    df = pd.read_csv(
        data_path,
        dtype={"code_departement": str, "code_commune": str},
        low_memory=False
    )

    df["code_departement"] = df["code_departement"].astype(str).str.zfill(2)
    df["code_commune"] = df["code_commune"].astype(str).str.zfill(5)

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

    RISK_MAP = {
        "Global (pondéré)": "risque_climatique",
        "Chaleur": "R_ATM_2016",
        "Sécheresse": "R_MVT_2016",
        "Inondation": "R_INO_2016",
        "Feux": "R_FEU_2016",
    }
    risque_label = st.sidebar.selectbox("Type de risque", list(RISK_MAP.keys()))
    col_risque = RISK_MAP[risque_label]

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

    prix_moy = dff["prix_m2"].mean()
    k1.metric("Prix moyen au m²", f"{prix_moy:,.0f} €")

    if "PMUN_2014" in dff.columns:
        pop_exposee = int(dff["PMUN_2014"].sum())
        k2.metric("Population exposée", f"{pop_exposee:,}".replace(",", " "))
    else:
        k2.metric("Population exposée", "Non disponible")

    if "risque_climatique" in dff.columns:
        dep_risk = dff.groupby("nom_departement")["risque_climatique"].mean()
        k3.metric("Département le plus risqué", dep_risk.idxmax())
    else:
        k3.metric("Département le plus risqué", "Non disponible")

    if col_risque in dff.columns:
        k4.metric("Indice moyen", round(dff[col_risque].mean(), 3))
    else:
        k4.metric("Indice moyen", "Non disponible")

    st.markdown("---")

    st.subheader("Aperçu des données")
    st.dataframe(dff.head(200))


if __name__ == "__main__":
    main()
