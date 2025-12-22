import pandas as pd
from pathlib import Path

# -------------------------------------------------------------------
# 1. Dossiers et lecture de la base finale
# -------------------------------------------------------------------
BASE_DIR = Path(r"C:\Users\elicl\OneDrive\Bureau\Projet_Python\Projet_Immobilier\data")

INPUT_FILE = BASE_DIR / "base_finale" / "base_finale.csv"

OUT_DIR = BASE_DIR / "resultats"
OUT_DIR.mkdir(exist_ok=True)

print("Lecture de la base :", INPUT_FILE)
df = pd.read_csv(INPUT_FILE, dtype=str)

# -------------------------------------------------------------------
# 2. Mise en forme des colonnes / types
# -------------------------------------------------------------------
# Colonnes en minuscules, underscore
df.columns = (
    df.columns.str.lower()
              .str.replace(" ", "_")
              .str.replace("-", "_")
)

# Conversion numériques
for col in ["valeur_fonciere", "surface_reelle_bati", "prix_m2", "annee"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

# On garde seulement les lignes avec prix_m2 positif
df = df[(df["prix_m2"].notna()) & (df["prix_m2"] > 0)]

# -------------------------------------------------------------------
# 3. Ajout des régions à partir des codes départements
# -------------------------------------------------------------------
regions = {
    "01":"AURA","02":"HDF","03":"AURA","04":"PACA","05":"PACA","06":"PACA","07":"AURA","08":"GE",
    "09":"OCC","10":"GE","11":"OCC","12":"OCC","13":"PACA","14":"NOR","15":"AURA","16":"NAQ",
    "17":"NAQ","18":"CVL","19":"NAQ","21":"BFC","22":"BRE","23":"NAQ","24":"NAQ","25":"BFC",
    "26":"AURA","27":"NOR","28":"CVL","29":"BRE","2A":"COR","2B":"COR","30":"OCC","31":"OCC",
    "32":"OCC","33":"NAQ","34":"OCC","35":"BRE","36":"CVL","37":"CVL","38":"AURA","39":"BFC",
    "40":"NAQ","41":"CVL","42":"AURA","43":"AURA","44":"PDL","45":"CVL","46":"OCC","47":"NAQ",
    "48":"OCC","49":"PDL","50":"NOR","51":"GE","52":"GE","53":"PDL","54":"GE","55":"GE",
    "56":"BRE","57":"GE","58":"BFC","59":"HDF","60":"HDF","61":"NOR","62":"HDF","63":"AURA",
    "64":"NAQ","65":"OCC","66":"OCC","67":"GE","68":"GE","69":"AURA","70":"BFC","71":"BFC",
    "72":"PDL","73":"AURA","74":"AURA","75":"IDF","76":"NOR","77":"IDF","78":"IDF","79":"NAQ",
    "80":"HDF","81":"OCC","82":"OCC","83":"PACA","84":"PACA","85":"PDL","86":"NAQ","87":"NAQ",
    "88":"GE","89":"BFC","90":"BFC","91":"IDF","92":"IDF","93":"IDF","94":"IDF","95":"IDF"
}

def map_region(dep):
    if pd.isna(dep):
        return "AUTRE"
    dep = str(dep).strip()
    if dep in ("2A", "2B"):
        return regions.get(dep, "AUTRE")
    # on pad avec un zéro si besoin
    if dep.isdigit() and len(dep) == 1:
        dep = "0" + dep
    return regions.get(dep, "AUTRE")

if "code_departement" in df.columns:
    df["region"] = df["code_departement"].apply(map_region)
else:
    df["region"] = "AUTRE"

# -------------------------------------------------------------------
# 4. Fonction utilitaire pour calculer les stats et enregistrer
# -------------------------------------------------------------------
def save_stats(group_cols, filename):
    """
    Calcule moyenne, médiane, min, max, count de prix_m2
    group_cols : liste de colonnes pour le groupby
    filename   : nom du fichier de sortie (csv)
    """
    stats = (
        df.groupby(group_cols)["prix_m2"]
          .agg(["mean", "median", "min", "max", "count"])
          .reset_index()
    )
    stats.to_csv(OUT_DIR / filename, index=False)
    print("Fichier créé :", OUT_DIR / filename)

# -------------------------------------------------------------------
# 5. Prix par ville / département / région / type de bien / surface
# -------------------------------------------------------------------
# Prix par ville (commune)
save_stats(["commune"], "prix_par_ville.csv")

# Prix par département
if "code_departement" in df.columns:
    save_stats(["code_departement"], "prix_par_departement.csv")

# Prix par région
save_stats(["region"], "prix_par_region.csv")

# Prix par type de bien
if "type_local" in df.columns:
    save_stats(["type_local"], "prix_par_type_bien.csv")

# Prix par surface (classes de surface)
if "surface_reelle_bati" in df.columns:
    bins = [0, 40, 60, 80, 100, 150, 10_000]
    labels = ["0_40", "40_60", "60_80", "80_100", "100_150", "150_plus"]
    df["classe_surface"] = pd.cut(df["surface_reelle_bati"], bins=bins, labels=labels, right=False)
    save_stats(["classe_surface"], "prix_par_surface.csv")

# -------------------------------------------------------------------
# 6. Top 20 villes les plus chères / moins chères
# -------------------------------------------------------------------
ville_stats = (
    df.groupby("commune")["prix_m2"]
      .agg(mean="mean", median="median", nb_ventes="count")
      .reset_index()
)

# on peut filtrer sur un minimum de ventes, par exemple 30, pour éviter du bruit
ville_stats_filtre = ville_stats[ville_stats["nb_ventes"] >= 30]

top20_cheres = ville_stats_filtre.sort_values("mean", ascending=False).head(20)
top20_moins_cheres = ville_stats_filtre.sort_values("mean", ascending=True).head(20)

top20_cheres.to_csv(OUT_DIR / "top20_villes_cheres.csv", index=False)
top20_moins_cheres.to_csv(OUT_DIR / "top20_villes_moins_cheres.csv", index=False)

print("Fichier créé :", OUT_DIR / "top20_villes_cheres.csv")
print("Fichier créé :", OUT_DIR / "top20_villes_moins_cheres.csv")

# -------------------------------------------------------------------
# 7. Evolution annuelle (France entière et par type)
# -------------------------------------------------------------------
if "annee" in df.columns:
    evol_annuelle = (
        df.groupby("annee")["prix_m2"]
          .agg(mean="mean", median="median", nb_ventes="count")
          .reset_index()
          .sort_values("annee")
    )
    evol_annuelle.to_csv(OUT_DIR / "evolution_annuelle_france.csv", index=False)
    print("Fichier créé :", OUT_DIR / "evolution_annuelle_france.csv")

    if "type_local" in df.columns:
        evol_ann_type = (
            df.groupby(["annee", "type_local"])["prix_m2"]
              .agg(mean="mean", median="median", nb_ventes="count")
              .reset_index()
              .sort_values(["annee", "type_local"])
        )
        evol_ann_type.to_csv(OUT_DIR / "evolution_annuelle_par_type.csv", index=False)
        print("Fichier créé :", OUT_DIR / "evolution_annuelle_par_type.csv")

# -------------------------------------------------------------------
# 8. Variation 2020–2025 (augmentation / baisse) par ville et par département
# -------------------------------------------------------------------
if "annee" in df.columns:
    annees_dispo = sorted(df["annee"].dropna().unique())
    if (2020 in annees_dispo) and (2025 in annees_dispo):

        # Variation par ville
        sub_ville = df[df["annee"].isin([2020, 2025])]
        var_ville = (
            sub_ville.groupby(["commune", "annee"])["prix_m2"]
            .mean()
            .reset_index()
        )
        var_ville_pivot = var_ville.pivot(index="commune", columns="annee", values="prix_m2")
        var_ville_pivot = var_ville_pivot.rename(columns={2020: "prix_m2_2020", 2025: "prix_m2_2025"})
        var_ville_pivot["variation_abs"] = var_ville_pivot["prix_m2_2025"] - var_ville_pivot["prix_m2_2020"]
        var_ville_pivot["variation_pct"] = (var_ville_pivot["variation_abs"] / var_ville_pivot["prix_m2_2020"]) * 100
        var_ville_pivot = var_ville_pivot.dropna(subset=["prix_m2_2020", "prix_m2_2025"])

        var_ville_pivot.reset_index().to_csv(OUT_DIR / "variation_2020_2025_par_ville.csv", index=False)
        print("Fichier créé :", OUT_DIR / "variation_2020_2025_par_ville.csv")

        # Variation par département
        if "code_departement" in df.columns:
            sub_dep = df[df["annee"].isin([2020, 2025])]
            var_dep = (
                sub_dep.groupby(["code_departement", "annee"])["prix_m2"]
                .mean()
                .reset_index()
            )
            var_dep_pivot = var_dep.pivot(index="code_departement", columns="annee", values="prix_m2")
            var_dep_pivot = var_dep_pivot.rename(columns={2020: "prix_m2_2020", 2025: "prix_m2_2025"})
            var_dep_pivot["variation_abs"] = var_dep_pivot["prix_m2_2025"] - var_dep_pivot["prix_m2_2020"]
            var_dep_pivot["variation_pct"] = (var_dep_pivot["variation_abs"] / var_dep_pivot["prix_m2_2020"]) * 100
            var_dep_pivot = var_dep_pivot.dropna(subset=["prix_m2_2020", "prix_m2_2025"])

            var_dep_pivot.reset_index().to_csv(OUT_DIR / "variation_2020_2025_par_departement.csv", index=False)
            print("Fichier créé :", OUT_DIR / "variation_2020_2025_par_departement.csv")

print("Analyse terminée.")
