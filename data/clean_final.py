import pandas as pd
from pathlib import Path

# Dossiers
BASE_DIR = Path("C:/Users/elicl/OneDrive/Bureau/Projet_Python/Projet_Immobilier/data")
INPUT_FILE = BASE_DIR / "DVF_BASE_FINALE" / "DVF_BASE_FINALE.csv"

OUTPUT_DIR = BASE_DIR / "base_finale"
OUTPUT_DIR.mkdir(exist_ok=True)
OUTPUT_FILE = OUTPUT_DIR / "base_finale.csv"

print("Lecture :", INPUT_FILE)

# 1. Charger la base
df = pd.read_csv(INPUT_FILE, dtype=str)

# Harmonisation des colonnes (on met tout en minuscules + remplace espaces)
df.columns = (
    df.columns.str.lower()
              .str.replace(" ", "_")
              .str.replace("-", "_")
)

# Vérification des colonnes
print("Colonnes disponibles :", list(df.columns))

# 2. Convertir valeur fonciere et surface en numérique
if "valeur_fonciere" in df.columns:
    df["valeur_fonciere"] = (
        df["valeur_fonciere"]
        .str.replace(",", "", regex=False)
        .str.replace(" ", "", regex=False)
        .astype(float)
    )
else:
    raise Exception("La colonne 'Valeur fonciere' est absente du fichier CSV.")

if "surface_reelle_bati" in df.columns:
    df["surface_reelle_bati"] = (
        df["surface_reelle_bati"]
        .str.replace(",", "", regex=False)
        .astype(float)
    )
else:
    raise Exception("La colonne 'Surface reelle bati' est absente du fichier CSV.")

# 3. Extraire l’année de date_mutation
if "date_mutation" in df.columns:
    df["annee"] = pd.to_datetime(df["date_mutation"], format="%d/%m/%Y", errors="coerce").dt.year
else:
    raise Exception("La colonne 'Date mutation' est absente du fichier CSV.")

# 4. Créer prix/m2
df["prix_m2"] = df["valeur_fonciere"] / df["surface_reelle_bati"]

# 5. Supprimer les lignes invalides
df = df[df["prix_m2"].notna() & (df["prix_m2"] > 0)]

# 6. Export final
df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

print("Base finale créée :", OUTPUT_FILE)
