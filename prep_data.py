import pandas as pd
from pathlib import Path
import unicodedata
import os
import numpy as np

# ---------------------------------------------------------
# CHEMINS
# ---------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
RESULT_DIR = DATA_DIR / "resultats"

os.makedirs(RESULT_DIR, exist_ok=True)
print(f"📁 Dossier résultats : {RESULT_DIR}")

# ---------------------------------------------------------
# Fonction normalisation colonnes
# ---------------------------------------------------------
def normalize(colname: str) -> str:
    colname = "".join(
        c for c in unicodedata.normalize("NFD", colname)
        if unicodedata.category(c) != "Mn"
    )
    colname = colname.strip().lower().replace(" ", "_")
    return colname

# ---------------------------------------------------------
# Lecture base fusionnée
# ---------------------------------------------------------
base_csv = DATA_DIR / "BASE_FUSIONNEE.csv"
print(f"📥 Lecture : {base_csv}")

df = pd.read_csv(base_csv, low_memory=False)
df.columns = [normalize(c) for c in df.columns]

print("🔎 Colonnes détectées :")
print(df.columns.tolist())

# ---------------------------------------------------------
# Vérifications colonnes essentielles
# ---------------------------------------------------------
required = ["valeur_fonciere", "surface_reelle_bati", "code_departement", "commune"]
for col in required:
    if col not in df.columns:
        raise ValueError(f"❌ Colonne manquante : {col}")

# colonne année
if "annee" not in df.columns and "date_mutation" in df.columns:
    df["date_mutation"] = pd.to_datetime(df["date_mutation"], errors="coerce")
    df["annee"] = df["date_mutation"].dt.year

df["annee"] = pd.to_numeric(df["annee"], errors="coerce")
df = df[(df["annee"] >= 2000) & (df["annee"] <= 2025)]
print(f"➜ Lignes après filtre années 2000–2025 : {len(df):,}")

# ---------------------------------------------------------
# Calcul prix/m2
# ---------------------------------------------------------
df["valeur_fonciere"] = pd.to_numeric(df["valeur_fonciere"], errors="coerce")
df["surface_reelle_bati"] = pd.to_numeric(df["surface_reelle_bati"], errors="coerce")

df = df[(df["valeur_fonciere"] > 0) & (df["surface_reelle_bati"] > 0)]
print(f"➜ Lignes après filtre VF/surface > 0 : {len(df):,}")

df["prix_m2"] = df["valeur_fonciere"] / df["surface_reelle_bati"]

# ---------------------------------------------------------
# Normalisation code departement
# ---------------------------------------------------------
df["code_departement"] = df["code_departement"].astype(str).str.replace(" ", "")

def pad_dep(dep):
    if dep in ["2A", "2B"]:
        return dep
    return dep.zfill(2)

df["code_departement"] = df["code_departement"].apply(pad_dep)

# ---------------------------------------------------------
# Zones
# ---------------------------------------------------------
zones = {
    "Zone_NordIDF": ["59","62","60","80","02","75","77","78","91","92","93","94","95"],
    "Zone_Ouest": [
        "22","29","35","56","14","27","50","61","76","44","49","53","72","85",
        "18","28","36","37","41","45","16","17","33","40","47","64"
    ],
    "Zone_Sud": [
        "09","11","12","30","31","32","34","46","48","65","66","81","82",
        "04","05","06","13","83","84","2A","2B"
    ],
    "Zone_Est": [
        "08","10","51","52","54","55","57","67","68","88",
        "21","25","39","58","70","71","89","90",
        "01","03","07","15","26","38","42","43","63","69","73","74"
    ]
}

def get_zone(dep):
    for z, liste in zones.items():
        if dep in liste:
            return z
    return "Zone_Autre"

df["zone"] = df["code_departement"].apply(get_zone)

# ---------------------------------------------------------
# Régions
# ---------------------------------------------------------
regions = {
    "01":"AURA","02":"HDF","03":"AURA","04":"PACA","05":"PACA","06":"PACA","07":"AURA",
    "08":"GE","09":"OCC","10":"GE","11":"OCC","12":"OCC","13":"PACA","14":"NOR","15":"AURA",
    "16":"NAQ","17":"NAQ","18":"CVL","19":"NAQ","21":"BFC","22":"BRE","23":"NAQ",
    "24":"NAQ","25":"BFC","26":"AURA","27":"NOR","28":"CVL","29":"BRE","2A":"COR",
    "2B":"COR","30":"OCC","31":"OCC","32":"OCC","33":"NAQ","34":"OCC","35":"BRE",
    "36":"CVL","37":"CVL","38":"AURA","39":"BFC","40":"NAQ","41":"CVL","42":"AURA",
    "43":"AURA","44":"PDL","45":"CVL","46":"OCC","47":"NAQ","48":"OCC","49":"PDL",
    "50":"NOR","51":"GE","52":"GE","53":"PDL","54":"GE","55":"GE","56":"BRE","57":"GE",
    "58":"BFC","59":"HDF","60":"HDF","61":"NOR","62":"HDF","63":"AURA","64":"NAQ",
    "65":"OCC","66":"OCC","67":"GE","68":"GE","69":"AURA","70":"BFC","71":"BFC",
    "72":"PDL","73":"AURA","74":"AURA","75":"IDF","76":"NOR","77":"IDF","78":"IDF",
    "79":"NAQ","80":"HDF","81":"OCC","82":"OCC","83":"PACA","84":"PACA","85":"PDL",
    "86":"NAQ","87":"NAQ","88":"GE","89":"BFC","90":"BFC","91":"IDF","92":"IDF",
    "93":"IDF","94":"IDF","95":"IDF"
}

df["region"] = df["code_departement"].apply(lambda d: regions.get(d, "Autre"))

# ---------------------------------------------------------
# Garder seulement Maison / Appartement
# ---------------------------------------------------------
df["type_local"] = df["type_local"].astype(str)
mask = df["type_local"].str.contains("maison|appartement", case=False, na=False)
df = df[mask]
print(f"➜ Lignes (Maison/Appartement) : {len(df):,}")

# ---------------------------------------------------------
# DVF LIGHT
# ---------------------------------------------------------
dvf_light = df[[
    "annee","code_departement","commune","type_local",
    "valeur_fonciere","surface_reelle_bati",
    "prix_m2","zone","region"
]]
dvf_light.to_csv(RESULT_DIR / "DVF_LIGHT.csv", index=False)
print("💾 DVF_LIGHT.csv")

# ---------------------------------------------------------
# Prix par ville (global + annuel)
# ---------------------------------------------------------
prix_ville = df.groupby(["commune","code_departement"])["prix_m2"].agg(
    count="count", mean="mean", median="median", min="min", max="max"
).reset_index()
prix_ville.to_csv(RESULT_DIR / "prix_par_ville_global.csv", index=False)
print("💾 prix_par_ville_global.csv")

prix_ville_annee = df.groupby(["annee","commune","code_departement"])["prix_m2"].agg(
    count="count", mean="mean", median="median", min="min", max="max"
).reset_index()
prix_ville_annee.to_csv(RESULT_DIR / "prix_par_ville_annee.csv", index=False)
print("💾 prix_par_ville_annee.csv")

# ---------------------------------------------------------
# Evolution 2020–2025 par ville
# ---------------------------------------------------------
if 2020 in prix_ville_annee["annee"].unique() and 2025 in prix_ville_annee["annee"].unique():
    pivot_ville = prix_ville_annee.pivot_table(
        index=["commune","code_departement"],
        columns="annee",
        values="mean"
    )
    sub = pivot_ville[[2020, 2025]].dropna()
    sub["variation_abs"] = sub[2025] - sub[2020]
    sub["variation_pct"] = 100 * sub["variation_abs"] / sub[2020]
    evo_ville = sub.reset_index()
    evo_ville.to_csv(RESULT_DIR / "evolution_villes_2020_2025.csv", index=False)
    print("💾 evolution_villes_2020_2025.csv")

# ---------------------------------------------------------
# Prix par departement (global + annuel)
# ---------------------------------------------------------
prix_dep = df.groupby("code_departement")["prix_m2"].agg(
    count="count", mean="mean", median="median", min="min", max="max"
).reset_index()
prix_dep.to_csv(RESULT_DIR / "prix_departement_global.csv", index=False)
print("💾 prix_departement_global.csv")

prix_dep_annee = df.groupby(["annee","code_departement"])["prix_m2"].agg(
    count="count", mean="mean", median="median", min="min", max="max"
).reset_index()
prix_dep_annee.to_csv(RESULT_DIR / "prix_departement_annee.csv", index=False)
print("💾 prix_departement_annee.csv")

# Evolution dept 2020–2025
if 2020 in prix_dep_annee["annee"].unique() and 2025 in prix_dep_annee["annee"].unique():
    pivot_dep = prix_dep_annee.pivot_table(
        index="code_departement",
        columns="annee",
        values="mean"
    )
    sub = pivot_dep[[2020, 2025]].dropna()
    sub["variation_abs"] = sub[2025] - sub[2020]
    sub["variation_pct"] = 100 * sub["variation_abs"] / sub[2020]
    evo_dep = sub.reset_index()
    evo_dep.to_csv(RESULT_DIR / "evolution_departement_2020_2025.csv", index=False)
    print("💾 evolution_departement_2020_2025.csv")

# ---------------------------------------------------------
# Prix par region (global + annuel)
# ---------------------------------------------------------
prix_reg = df.groupby("region")["prix_m2"].agg(
    count="count", mean="mean", median="median", min="min", max="max"
).reset_index()
prix_reg.to_csv(RESULT_DIR / "prix_region_global.csv", index=False)
print("💾 prix_region_global.csv")

prix_reg_annee = df.groupby(["annee","region"])["prix_m2"].agg(
    count="count", mean="mean", median="median", min="min", max="max"
).reset_index()
prix_reg_annee.to_csv(RESULT_DIR / "prix_region_annee.csv", index=False)
print("💾 prix_region_annee.csv")

# Evolution region 2020–2025
if 2020 in prix_reg_annee["annee"].unique() and 2025 in prix_reg_annee["annee"].unique():
    pivot_reg = prix_reg_annee.pivot_table(
        index="region",
        columns="annee",
        values="mean"
    )
    sub = pivot_reg[[2020, 2025]].dropna()
    sub["variation_abs"] = sub[2025] - sub[2020]
    sub["variation_pct"] = 100 * sub["variation_abs"] / sub[2020]
    evo_reg = sub.reset_index()
    evo_reg.to_csv(RESULT_DIR / "evolution_region_2020_2025.csv", index=False)
    print("💾 evolution_region_2020_2025.csv")

# ---------------------------------------------------------
# Prix par zone (global + annuel)
# ---------------------------------------------------------
prix_zone = df.groupby("zone")["prix_m2"].agg(
    count="count", mean="mean", median="median", min="min", max="max"
).reset_index()
prix_zone.to_csv(RESULT_DIR / "prix_zone_global.csv", index=False)
print("💾 prix_zone_global.csv")

prix_zone_annee = df.groupby(["annee","zone"])["prix_m2"].agg(
    count="count", mean="mean", median="median", min="min", max="max"
).reset_index()
prix_zone_annee.to_csv(RESULT_DIR / "prix_zone_annee.csv", index=False)
print("💾 prix_zone_annee.csv")

# Evolution zone 2020–2025
if 2020 in prix_zone_annee["annee"].unique() and 2025 in prix_zone_annee["annee"].unique():
    pivot_zone = prix_zone_annee.pivot_table(
        index="zone",
        columns="annee",
        values="mean"
    )
    sub = pivot_zone[[2020, 2025]].dropna()
    sub["variation_abs"] = sub[2025] - sub[2020]
    sub["variation_pct"] = 100 * sub["variation_abs"] / sub[2020]
    evo_zone = sub.reset_index()
    evo_zone.to_csv(RESULT_DIR / "evolution_zone_2020_2025.csv", index=False)
    print("💾 evolution_zone_2020_2025.csv")

# ---------------------------------------------------------
# Prix par type (Maison/Appartement) par année
# ---------------------------------------------------------
prix_type_annee = df.groupby(["annee","type_local"])["prix_m2"].agg(
    count="count", mean="mean", median="median", min="min", max="max"
).reset_index()
prix_type_annee.to_csv(RESULT_DIR / "prix_type_annee.csv", index=False)
print("💾 prix_type_annee.csv")

# ---------------------------------------------------------
# Classes de surface
# ---------------------------------------------------------
bins = [0, 30, 60, 90, np.inf]
labels = ["<=30","30-60","60-90",">90"]
df["classe_surface"] = pd.cut(df["surface_reelle_bati"], bins=bins, labels=labels)

prix_surface = df.groupby(["annee","classe_surface","type_local"])["prix_m2"].agg(
    count="count", mean="mean", median="median", min="min", max="max"
).reset_index()
prix_surface.to_csv(RESULT_DIR / "prix_par_surface_type_annee.csv", index=False)
print("💾 prix_par_surface_type_annee.csv")

# ---------------------------------------------------------
# Top 20 villes les plus chères & les moins chères (dernière année)
# ---------------------------------------------------------
annee_max = int(df["annee"].max())
df_last = df[df["annee"] == annee_max]

moy_villes_last = df_last.groupby(["commune","code_departement"])["prix_m2"].mean().reset_index()

top20 = moy_villes_last.sort_values("prix_m2", ascending=False).head(20)
top20.to_csv(RESULT_DIR / "top20_villes_plus_cheres.csv", index=False)
print(f"💾 top20_villes_plus_cheres.csv (année {annee_max})")

bottom20 = moy_villes_last.sort_values("prix_m2", ascending=True).head(20)
bottom20.to_csv(RESULT_DIR / "bottom20_villes_moins_cheres.csv", index=False)
print(f"💾 bottom20_villes_moins_cheres.csv (année {annee_max})")

print("\n✅ FIN — Tous les fichiers CSV sont prêts dans data/resultats/")
