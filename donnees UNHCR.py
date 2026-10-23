import requests
import pandas as pd

# Récupération des informations de chaque pays :
# identifiants, codes, noms (FR/ENG) et régions (FR/ENG)
URL2 = "https://api.unhcr.org/population/v1/countries"
params2= {"limit": 300, "page": 1}

req2 = requests.get(URL2, params = params2)
pays_brut = req2.json()

countries = pd.DataFrame([{"id": country["id"], 
                        "iso": country["iso"],
                        "name": country["name"],
                        "region": country["region"]} 
                        for country in pays_brut["items"]])


# Récupération du nombre de réfugiés présents en fin d'année
# coo = country of origin ; coa = country of asylum
# coo_all=True et coa_all=True permettent de récupérer toutes les paires origine-destination

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

# Conversion en numérique pour permettre les opérations statistiques

refugees["refugees"] = pd.to_numeric(refugees["refugees"])
refugees["asylum_seekers"] = pd.to_numeric(refugees["asylum_seekers"])

# Ajout des régions des pays d'origine et d'arrivée

unhcr_df = refugees.merge(countries[["iso", "region"]].rename(columns = {"region": "region_origin"}),
                        left_on="coo_iso", right_on="iso", how="left").merge(
                        countries[["iso", "region"]].rename(columns = {"region": "region_arrival"}),
                        left_on="coa_iso", right_on="iso", how="left", suffixes = ("_origin", "_arrival"))
unhcr_df.to_parquet("unhcr_clean.parquet", index=False)

# Diagnostic macro sur les déplacements des réfugiés selon leur région d'origine
# overview1:
# overview2 via overwiew0
# overview

overview1 = (unhcr_df.groupby("region_origin")["asylum_seekers"]
            .sum().reset_index().sort_values(axis= 0, by="asylum_seekers", ascending = False))

overview0 = (unhcr_df.groupby(["coo_name", "year"])["coa_name"].nunique().reset_index()
            .rename(columns= {"coa_name": "destination_countries"}))

overview0 = overview0.merge(countries[["name", "region"]], 
            left_on = "coo_name", right_on = "name", 
            how = "left").drop(columns = "name")
            
overview2 = (overview0.groupby(["region"])["destination_countries"]
            .mean()
            .reset_index()
            .rename(columns= {"region": "region_origin",
            "destination_countries": "mean_destination_countries"}))

overview = overview1.merge(overview2, 
            on = "region_origin", 
            how = "left")

overview.to_csv("overview.csv", index=False)