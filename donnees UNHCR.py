import requests
import pandas as pd

# Récupération des informations de chaque pays :
# identifiant, code, nom, et région 
URL2 = "https://api.unhcr.org/population/v1/countries"
params2= {"limit": 300, "page": 1}

req2 = requests.get(URL2, params = params2)
pays_brut = req2.json()

countries = pd.DataFrame([{"id": country["id"], 
                        "iso": country["iso"],
                        "name": country["name"],
                        "region": country["region"]} 
                        for country in pays_brut["items"]])


# Récupération des populations de réfugiés et demandeurs d'asile de 2017 à 2020
# coo = country of origin ; coa = country of asylum
# coo_all=True et coa_all=True permettent de récupérer toutes les paires origine-destination
# refugees = nombre de réfugiés présents en fin d'année
# asylum_seekers = nombre de demandeurs d'asile dont la demande est encore en cours à la fin de l'année

URL3 = "https://api.unhcr.org/population/v1/population"

params3 = {"limit": 300, "page": 1, 
            "yearFrom": 2017, "yearTo": 2020,
            "coo_all": True, "coa_all": True}

refugees_raw = []
max_pages = requests.get(URL3, params=params3).json()["maxPages"]

for page in range(1, max_pages + 1):
    params3["page"] = page
    data = requests.get(URL3, params=params3).json()
    refugees_raw.extend(data["items"])

selected_var = ["year", "coo_iso", "coo_name", "coa_iso", "coa_name", "refugees", "asylum_seekers"]
refugees = pd.DataFrame(refugees_raw)[selected_var]

# Conversion en numérique et en entier pour permettre les opérations statistiques

refugees["refugees"] = pd.to_numeric(refugees["refugees"])
refugees["asylum_seekers"] = pd.to_numeric(refugees["asylum_seekers"])
refugees["year"] = refugees["year"].astype(int)


# Ajout des régions des pays d'origine des réfugiés

unhcr_df = refugees.merge(countries[["iso", "region"]].rename(columns = {"region": "region_origin"}),
                        left_on="coo_iso", right_on="iso", how="left").drop(columns = "iso")

# Conversion du dataframe en fichier parquet

unhcr_df.to_parquet("unhcr_df.parquet", index=False)