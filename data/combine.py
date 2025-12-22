import pandas as pd
from pathlib import Path

# ---- 1. Dossiers ----
BASE_DIR = Path(r"C:\Users\elicl\OneDrive\Bureau\Projet_Python\Projet_Immobilier\data")
SRC_DIR = Path(r"C:\Users\elicl\OneDrive\Bureau\Projet_Python\bases_clean")
DEST_DIR = BASE_DIR / "DVF_BASE_FINALE"

DEST_DIR.mkdir(parents=True, exist_ok=True)

print("📁 Dossier de destination :", DEST_DIR)

# ---- 2. Fichiers DVF à convertir ----
fichiers_xlsx = [
    "ValeursFoncieres-2020-S2_NETTOYE_CLEAN.xlsx",
    "ValeursFoncieres-2021_NETTOYE_CLEAN.xlsx",
    "ValeursFoncieres-2022_NETTOYE_CLEAN.xlsx",
    "ValeursFoncieres-2023_NETTOYE_CLEAN.xlsx",
    "ValeursFoncieres-2024_NETTOYE_CLEAN.xlsx",
    "ValeursFoncieres-2025-S1_NETTOYE_CLEAN.xlsx",
]

csv_list = []

# ---- 3. Conversion XLSX → CSV ----
print("\n🔄 Conversion XLSX → CSV...\n")

for fx in fichiers_xlsx:
    xlsx_path = SRC_DIR / fx

    if not xlsx_path.exists():
        print(f"❌ FICHIER MANQUANT : {xlsx_path}")
        continue

    df = pd.read_excel(xlsx_path)

    # Nom CSV
    csv_name = fx.replace(".xlsx", ".csv")
    csv_path = DEST_DIR / csv_name

    df.to_csv(csv_path, index=False, encoding="utf-8")
    csv_list.append(csv_path)

    print(f"✔ Converti : {csv_path}")

# ---- 4. Fusion des CSV ----
print("\n📚 Fusion des fichiers CSV...")

df_final = pd.concat((pd.read_csv(f) for f in csv_list), ignore_index=True)

FINAL_PATH = DEST_DIR / "DVF_BASE_FINALE.csv"

df_final.to_csv(FINAL_PATH, index=False, encoding="utf-8")

print("\n✅ Fusion terminée !")
print("📦 Base finale enregistrée sous :")
print(FINAL_PATH)
