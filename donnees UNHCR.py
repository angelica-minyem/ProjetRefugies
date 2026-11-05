import requests
import pandas as pd

# Récupération des informations de chaque pays :
# code ISO, nom et région
URL = "https://api.unhcr.org/population/v1/countries"
params = {"limit": 300, "page": 1}

req = requests.get(URL, params=params)
pays_brut = req.json()

countries = pd.DataFrame([{
                        "iso": country["iso"],
                        "name": country["name"],
                        "region": country["region"]}
                        for country in pays_brut["items"]])
                        
# Récupération des nouvelles demandes d'asile enregistrées par l'UNHCR
# entre 2017 et 2020.
# PT = ASY correspond aux nouvelles demandes d'asile.
URL2 = "https://minio.lab.sspcloud.fr/angelik/ProjetRefugies/UNHCR_Data.xlsx"

use_cols = ["OriginISO", "OriginName", "AsylumISO", "AsylumName", "PT", "Year", "Count"]

refugees = pd.read_excel(URL2, usecols=use_cols,
                    sheet_name="DATA").rename(columns=
                    {"Year": "year",
                    "OriginISO": "coo_iso",
                    "OriginName": "coo_name",
                    "AsylumISO": "coa_iso",
                    "AsylumName": "coa_name",
                    "Count": "refugees"})

# Conservation des nouvelles demandes d'asile entre 2017 et 2020
refugees = refugees[(refugees["year"] >= 2017) &
                    (refugees["year"] <= 2020) &
                    (refugees["PT"] == "ASY")].drop(columns="PT")

# Conversion en numérique et en entier pour permettre les opérations statistiques
refugees["refugees"] = pd.to_numeric(refugees["refugees"])
refugees["year"] = refugees["year"].astype(int)


# Ajout de la région du pays d'origine
unhcr_df = refugees.merge(countries[["iso", "region"]].rename(columns={"region": "region_origin"}),
                        left_on="coo_iso", right_on="iso", how="left").drop(columns="iso")

# Conversion du dataframe en fichier parquet
unhcr_df.to_parquet("unhcr_df.parquet", index=False)